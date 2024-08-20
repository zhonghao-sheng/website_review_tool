from django.shortcuts import render
from multiprocessing import JoinableQueue as Queue
from threading import Thread
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
import requests
from bs4 import BeautifulSoup


class Web_spider():
    def __init__(self):
        self.visited_or_about_to_visit = set()
        self.web_links = Queue()
        self.baseurl = None
        self.broken_link_file = open('broken_links_faster.txt', 'w')
        self.uom_sign_link_file = open('uom_links.txt', 'w')

        self.counter = 0
        self.broken_links = list()
        self.UOM_sign_links = list()

    def put_url(self, baseurl):
        self.web_links.put([baseurl, None])
        self.counter += 1
        self.baseurl = baseurl

    def add_uom_sign_link(self, link, source_link):
        self.UOM_sign_links.append({'url': link, 'source_link': source_link})

    def write_uom_sign_link(self, link, source_link):
        self.uom_sign_link_file.write(f'uom link:{link}, page source:{source_link}\n')

    def add_broken_link(self, link, source_link):
        self.broken_links.append({'url': link, 'source_link': source_link})

    def write_broken_link(self, link, source_link, response_status):
        self.broken_link_file.write(f'status:{response_status}, broken link: {link}, page source: {source_link}')

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
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href not in self.visited_or_about_to_visit:
                            if 'mailto:' not in href:
                                self.visited_or_about_to_visit.add(href)
                                self.web_links.put([href, link])
                                self.counter += 1
                            else:
                                print(f'not responsible for checking mails{href}')
                            print('new links founded', href)
                else:
                    # if response.status_code == 403:
                    #     self.add_uom_sign_link(link, link_combo[1])
                    #     self.write_uom_sign_link(link, link_combo[1])
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    self.add_broken_link(link, link_combo[1])
                    self.write_broken_link(link, link_combo[1], response.status_code)
                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}, source page {link_combo[1]}')
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
                response = requests.get(link)
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
                    # if response.status_code == 403:
                    #     self.add_uom_sign_link(link, link_combo[1])
                    #     self.write_uom_sign_link(link, link_combo[1])
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    self.add_broken_link(link, link_combo[1])
                    self.write_broken_link(link, link_combo[1], response.status_code)
                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}, pagesource is {link_combo[1]}')
            finally:
                self.web_links.task_done()
                self.counter -= 1

                print(f'counter = {self.counter}')
                print(f'remaining detected tasks{self.web_links.qsize()}')

    def main(self, baseurl):
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
        return self.broken_links


def index(request):
    return render(request, 'index.html')


def search_link(request):
    if request.method == 'POST':
        url = request.POST['url']
        web_spider = Web_spider()
        results = web_spider.main(url)
        # results = scrape_pages(url)
        return render(request, 'results.html', {'results': results})
    return render(request, 'index.html')

