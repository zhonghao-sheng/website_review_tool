from django.shortcuts import render, redirect
from multiprocessing import JoinableQueue as Queue
from threading import Thread
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from django.http import FileResponse, HttpResponse
import time

REQUEST_TIMEOUT = 20

def index(request):
    return render(request, 'search.html')

class Web_spider():
    def __init__(self):
        self.visited_or_about_to_visit = set()
        self.web_links = Queue()
        self.baseurl = 'https://sites.research.unimelb.edu.au/research-funding'
        self.UOM_sign_links = list()
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


    def deal_uom_sign_link(self, link,associated_text, source_link):
        if self.is_uom_sign_link(link):
            self.add_uom_sign_link(link, source_link)
    def add_broken_link(self, link, source_link, associated_text):
        self.broken_links.append({'url': link, 'source_link':
            source_link, 'associated_text': associated_text})

    def deal_broken_link(self, link, source_link, response_status, associated_text):
        self.add_broken_link(link, source_link, associated_text)

    def get_more_links(self):

        while True:
            link_combo = self.web_links.get()

            link = link_combo[0]
            try:
                print(f'getting link {link}')
                response = requests.get(link, timeout=REQUEST_TIMEOUT)
                self.visited_or_about_to_visit.add(link)
                if response.status_code == 200:
                    if not link.startswith(self.baseurl):
                        continue
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if self.keyword is not None:
                        text = soup.get_text()
                        for keyword in self.keyword:
                            if keyword in text:
                                print(f'found keyword {keyword} in link {link}')
                                self.keyword_links.append({'url':link, 'associated_text':keyword})

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
                response = requests.get(link, timeout=REQUEST_TIMEOUT)
                # if not broken, then put back to the queue
                content_type = response.headers.get('Content-Type', '').lower()

                # Check if the link is a valid download link
                if 'application/' in content_type or 'octet-stream' in content_type:
                    print(f'Valid download link detected: {link}')
                    self.handle_download_link(link, link_combo[1], content_type)
                
                elif response.status_code == 200:
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

    def handle_download_link(self, link, source_link, content_type):
        # download the file
        try:
            response = requests.get(link, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Extract the filename from the URL
            filename = link.split('/')[-1]
            download_path = os.path.join('downloads', filename)

            # Ensure the downloads directory exists
            os.makedirs(os.path.dirname(download_path), exist_ok=True)

            # Write the file to the downloads directory
            with open(download_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f'File downloaded: {download_path}')
        except Exception as e:
            # Log the failure to the broken links file
            self.deal_broken_link(link, source_link, 'download_failed', str(e))

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
        keyword_list = keyword.split()
        self.put_keyword(keyword_list)
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
        url = request.POST.get('url')
        keyword = request.POST.get('specifiedText')  # Fetch the keyword if it's provided
        results = search_task(url, keyword)
        return render(request, 'results.html', {'results': results})
    return render(request, 'search.html')

def search_task(url, keyword):
    
    # Initialize Web_spider instance
    web_spider = Web_spider()

    if keyword:
        results = web_spider.search_keyword_links(url, keyword)
    else:
        results = web_spider.search_broken_links(url)
    download_table(results)
    return results
def download_table(results):
    df = pd.DataFrame(results)
    filename = 'output.xlsx'
    if not os.path.exists('download_table'):
        os.mkdir('download_table')
    path = os.path.join('download_table', filename)
    output = pd.ExcelWriter(path, engine='openpyxl')
    df.to_excel(output, index=False)
    output.close()

def download(request):
    # Specify the path to the existing Excel file
    file_path = os.path.join('download_table', 'output.xlsx')
    print(file_path)
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file in binary mode and send it as a response
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = 'attachment; filename="output.xlsx"'
        return response
    else:
        return HttpResponse("File not found.", status=404)