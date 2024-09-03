from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
import uuid
import json
import logging
from django_rq import get_queue, get_connection
from rq.job import Job, NoSuchJobError
from multiprocessing import JoinableQueue as Queue
from threading import Thread

logger = logging.getLogger(__name__)

class Web_spider():
    def __init__(self):
        self.visited_or_about_to_visit = set()
        self.web_links = Queue()
        self.baseurl = 'https://sites.research.unimelb.edu.au/research-funding'
        self.broken_link_file = open('broken_links_faster.txt', 'w')
        self.UOM_sign_links = list()
        self.uom_sign_link_file = open('uom_links.txt', 'w')
        self.keyword_link_file = open('keyword_links.txt', 'w')
        self.counter = 0
        self.broken_links = list()
        self.keyword = 'Funding Partners'
        self.keyword_links = list()

    def put_url(self, baseurl):
        self.web_links.put([baseurl, None, None])
        self.counter += 1
        self.baseurl = baseurl

    def put_keyword(self, keyword):
        self.keyword = keyword

    def is_uom_sign_link(self, link):
        return self.baseurl in link

    def add_uom_sign_link(self, link, source_link):
        self.UOM_sign_links.append({'url': link, 'source_link': source_link})

    def write_uom_sign_link(self, link, source_link):
        self.uom_sign_link_file.write(f'uom link:{link}, page source:{source_link}\n')

    def deal_uom_sign_link(self, link, source_link):
        if self.is_uom_sign_link(link):
            self.add_uom_sign_link(link, source_link)
            self.write_uom_sign_link(link, source_link)

    def add_broken_link(self, link, source_link, associated_text):
        self.broken_links.append({'url': link, 'source_link': source_link, 'associated_text': associated_text})

    def write_broken_link(self, link, source_link, response_status, associated_text):
        self.broken_link_file.write(f'status:{response_status}, broken link: {link}, page source: {source_link}, associated_text: {associated_text}\n')

    def deal_broken_link(self, link, source_link, response_status, associated_text):
        self.add_broken_link(link, source_link, associated_text)
        self.write_broken_link(link, source_link, response_status, associated_text)

    def get_more_links(self):
        while True:
            link_combo = self.web_links.get()
            link = link_combo[0]
            try:
                print(f'getting link {link}')
                response = requests.get(link)
                self.visited_or_about_to_visit.add(link)
                if response.status_code == 200:
                    if not link.startswith(self.baseurl):
                        continue
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if self.keyword is not None:
                        text = soup.get_text()
                        if self.keyword in text:
                            print(f'found keyword {self.keyword} in link {link}')
                            self.keyword_links.append(link)
                            self.keyword_link_file.write(link + '\n')
                    for href_link in soup.find_all('a', href=True):
                        href = href_link['href']
                        text = href_link.get_text()
                        if href not in self.visited_or_about_to_visit:
                            if 'mailto:' not in href:
                                self.visited_or_about_to_visit.add(href)
                                self.web_links.put([href, link, text])
                                self.counter += 1
                            else:
                                print(f'not responsible for checking mails {href}')
                            print('new links founded', href)
                else:
                    if response.status_code == 403:
                        self.deal_uom_sign_link(link, link_combo[1])
                    else:
                        self.deal_broken_link(link, link_combo[1], response.status_code, link_combo[2])
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}, associated_text:{link_combo[2]}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1
                print(f'counter = {self.counter}')

    def detect_links(self):
        while True:
            link_combo = self.web_links.get()
            link = link_combo[0]
            try:
                print(f'detecting link {link}')
                response = requests.get(link)
                if response.status_code == 200:
                    if link.startswith(self.baseurl):
                        self.web_links.put(link_combo)
                        self.counter += 1
                    else:
                        if self.counter == 0:
                            print('finished')
                            return
                else:
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    if response.status_code == 403:
                        self.deal_uom_sign_link(link, link_combo[1])
                    else:
                        self.deal_broken_link(link, link_combo[1], response.status_code, link_combo[2])
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1
                print(f'counter = {self.counter}')

    def search_broken_links(self, baseurl):
        self.put_url(baseurl)
        thread_list = list()
        for _ in range(20):
            t = Thread(target=self.get_more_links)
            thread_list.append(t)
        for _ in range(20):
            t = Thread(target=self.detect_links)
            thread_list.append(t)
        for t in thread_list:
            t.daemon = True
            t.start()
        for t in thread_list:
            t.join()
        self.web_links.join()
        print(self.keyword_links)
        return self.broken_links

    def search_keyword_links(self, baseurl, keyword):
        self.put_keyword(keyword)
        self.put_url(baseurl)
        thread_list = list()
        for _ in range(20):
            t = Thread(target=self.get_more_links)
            thread_list.append(t)
        for _ in range(20):
            t = Thread(target=self.detect_links)
            thread_list.append(t)
        for t in thread_list:
            t.daemon = True
            t.start()
        self.web_links.join()
        return self.keyword_links

@login_required
def search_link(request):
    if request.method == 'POST':
        try:
            url = request.POST.get('url')
            keyword = request.POST.get('keyword')  # Fetch the keyword if it's provided

            # Generate a unique ID for this task
            job_id = str(uuid.uuid4())
            logger.info(f"Enqueueing job with ID: {job_id} for URL: {url} and Keyword: {keyword}")

            # Enqueue the job
            queue = get_queue('default')
            queue.enqueue(search_task, url, keyword, job_id)
            logger.info(f"Job {job_id} enqueued successfully.")

            # Redirect to a results page that will display the job status
            return redirect('results', job_id=job_id)
        except Exception as e:
            logger.error(f"Error in search_link view: {str(e)}")
            return render(request, 'results.html', {'error': str(e)})
    return render(request, 'search.html')

def search_task(url, keyword, job_id):
    logger.info(f"Starting search task with job ID: {job_id}")
    try:
        web_spider = Web_spider()

        if keyword:
            results = web_spider.search_keyword_links(url, keyword)
        else:
            results = web_spider.search_broken_links(url)
        
        results_json = json.dumps(results)
        conn = get_connection('default')
        conn.set(job_id, results_json, ex=3600)  # Results expire after 1 hour
        logger.info(f"Completed search task with job ID: {job_id}")
    except Exception as e:
        logger.error(f"Error in search task with job ID: {job_id}: {e}")

def results(request, job_id):
    try:
        job_id_str = str(job_id)
        logger.debug(f"Fetching job with ID: {job_id_str}")
        conn = get_connection('default')
        job = Job.fetch(job_id_str, connection=conn)

        if job.is_finished:
            results = job.result  # Get the result from the job
            return render(request, 'results.html', {'results': results})
        else:
            logger.debug(f"Job with ID: {job_id_str} is still processing")
            return render(request, 'results.html', {'status': 'Job is still processing...', 'results': []})
    except NoSuchJobError:
        logger.error(f"No such job found with ID: {job_id_str}")
        return render(request, 'results.html', {'error': 'No such job found.'})
    except Exception as e:
        logger.error(f"Error in results view: {str(e)}")
        return render(request, 'results.html', {'error': str(e), 'results': []})