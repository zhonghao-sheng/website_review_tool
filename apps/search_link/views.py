from django.shortcuts import render, redirect
from multiprocessing import JoinableQueue as Queue
from threading import Thread
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
import uuid
import json
import logging
from django.http import JsonResponse

import time
from django.http import JsonResponse
import time

S = 70
def index(request):
    return render(request, 'search.html')

class Web_spider():
    def __init__(self):
        self.visited_or_about_to_visit = set()
        self.web_links = Queue()
        self.baseurl = 'https://sites.research.unimelb.edu.au/research-funding'
        self.broken_link_file = open('broken_links_faster.txt', 'w')
        self.UOM_sign_links = list()
        self.uom_sign_link_file = open('uom_links.txt','w')
        self.keyword_link_file = open('keyword_links.txt','w')
        self.counter = 0
        self.broken_links = list()
        self.keyword = 'Funding Partners'
        self.keyword_links = list()


    def put_url(self, baseurl):
        # [link, source page link, associated text]
        self.web_links.put([baseurl, None, None])
        self.counter += 1
        self.baseurl = baseurl
    def put_keyword(self, keyword):
        self.keyword = keyword
    def is_uom_sign_link(self, link):
        return self.baseurl in link
    def add_uom_sign_link(self, link, source_link):
        self.UOM_sign_links.append({'url': link, 'source_link': source_link})

    def write_uom_sign_link(self, link, associated_text, source_link):
        self.uom_sign_link_file.write(f'uom link:{link}, associated_text:{associated_text},page source:{source_link}\n')

    def deal_uom_sign_link(self, link,associated_text, source_link):
        if self.is_uom_sign_link(link):
            self.add_uom_sign_link(link, source_link)
            self.write_uom_sign_link(link, associated_text, source_link)
    def add_broken_link(self, link, source_link, associated_text):
        self.broken_links.append({'url': link, 'source_link':
            source_link, 'associated_text': associated_text})

    def write_broken_link(self, link, source_link, response_status, associated_text):
        self.broken_link_file.write(f'status:{response_status}, broken link: '
                                    f'{link}, page source: {source_link}, associated_text: {associated_text}\n')

    def deal_broken_link(self, link, source_link, response_status, associated_text):
        self.add_broken_link(link, source_link, associated_text)
        self.write_broken_link(link, source_link, response_status, associated_text)

    def get_more_links(self):

        while True:
            if self.counter >= 200:
                while not self.web_links.empty():
                    self.web_links.get()
                    self.web_links.task_done()
                return
            link_combo = self.web_links.get()

            link = link_combo[0]
            try:
                print(f'getting link {link}')
                response = requests.get(link, timeout=S)
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
                        self.deal_uom_sign_link(link, link_combo[2], link_combo[1])
                    else:
                        self.deal_broken_link(link, link_combo[1], response.status_code, link_combo[2])
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}, associated_text:{link_combo[2]}')

                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1
                print(f'counter = {self.counter}')
                print(f'remaining links number {self.web_links.qsize()}')

    # help save time by filtering out broken link to reduce response time
    def detect_links(self):
        while True:
            link_combo = self.web_links.get()
            link = link_combo[0]

            try:
                print(f'detecting link {link}')
                response = requests.get(link, timeout=S)
                # if not broken, then put back to the queue
                if response.status_code == 200:
                    if link.startswith(self.baseurl):
                        self.web_links.put(link_combo)
                        self.counter += 1
                    else:
                        if self.web_links.qsize() == 0:
                            print('finished')
                            return
                else:
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    if response.status_code == 403:
                        self.deal_uom_sign_link(link, link_combo[2],link_combo[1])
                    else:
                        self.deal_broken_link(link, link_combo[1], response.status_code, link_combo[2])

                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1

                print(f'counter = {self.counter}')
                print(f'remaining detected tasks{self.web_links.qsize()}')

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

# def process_link(href, source_url):
#     try:
#         print(f'Processing link {href} from source {source_url}')
#         response = requests.get(href)
#         if response.status_code == 200:
#             print(f'Link {href} is valid.')
#         else:
#             print(f'Link {href} is broken with status code {response.status_code}.')
#             # Handle broken link (e.g., log it, save it to a file, etc.)
#     except Exception as e:
#         print(f'Error processing link {href}: {str(e)}')


def search_link(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        keyword = request.POST.get('keyword')  # Fetch the keyword if it's provided
        results = search_task(url, keyword)
        return render(request, 'results.html', {'results': results})
    return render(request, 'search.html')

# assign a job ID to each task
def search_task(url, keyword):
    
    # Initialize Web_spider instance
    web_spider = Web_spider()

    if keyword:
        results = web_spider.search_keyword_links(url, keyword)
    else:
        results = web_spider.search_broken_links(url)
    return results
    
    

# def results(request, job_id):
#     try:
#         job_id_str = str(job_id)
#         job = Job.fetch(job_id_str, connection=conn)
#
#         # if job.is_finished or job.is_failed:
#         #     # Perform job cleanup, delete the job immediately after it finishes
#         #     job.cleanup(ttl=0)
#         #     # remove the job from Redis
#         #     # conn.delete(job.id)
#
#         if job.is_finished:
#             results = job.result
#             if not results:
#                 # If job.result is empty, try to get results from Redis
#                 results_json = conn.get(job_id_str)
#                 if results_json:
#                     results = json.loads(results_json)
#                 else:
#                     results = []
#
#             logger.error(f"Final results (error): {results}")
#             send_stop_job_command(conn, job_id_str)
#             return render(request, 'results.html', {'results': results})
#
#         elif job.is_failed:
#             return render(request, 'results.html', {'error': 'Job failed.'})
#         else:
#             results = job.result
#             if not results:
#                 # If job.result is empty, try to get results from Redis
#                 results_json = conn.get(job_id_str)
#                 if results_json:
#                     results = json.loads(results_json)
#                 else:
#                     results = []
#
#             logger.error(f"Not finished final results (error): {results}")
#             send_stop_job_command(conn, job_id_str)
#             return render(request, 'results.html', {'results': results, 'status': 'Job cannot be completed because of the timeout.'})
#
#     except NoSuchJobError:
#         return render(request, 'results.html', {'error': 'No such job found.'})
#     except ConnectionError as e:
#         logger.error(f"Redis connection error: {str(e)}")
#         return render(request, 'results.html', {'error': 'Could not connect to Redis. Please try again later.', 'results': []})
#     except Exception as e:
#         return render(request, 'results.html', {'error': str(e), 'results': []})