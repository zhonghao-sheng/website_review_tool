import requests
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process, JoinableQueue as Queue
import sys
import time
class web_spider():
    def __init__(self):
        self.visited_or_about_to_visit = set()
        self.web_links = Queue()
        self.baseurl = None
        self.file = open('broken_links_faster.txt','w')
        self.counter = 0
        self.broken_links = list()
    def put_url(self, baseurl):
        self.web_links.put([baseurl, None])
        self.counter += 1
        self.baseurl = baseurl
    def get_more_links(self):
        while True:
            url_combo = self.web_links.get()

            url = url_combo[0]
            try:
                print(f'getting link {url}')
                response = requests.get(url)
                self.visited_or_about_to_visit.add(url)
                if response.status_code == 200:
                    if not url.startswith(self.baseurl):
                        continue
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href not in self.visited_or_about_to_visit:
                            self.visited_or_about_to_visit.add(href)
                            self.web_links.put([href, url])
                            self.counter += 1
                            print('new links founded', href)
                else:
                    print(f'status_code:{response.status_code}, broken_link:{url}, page source:{url_combo[1]}')
                    self.file.write(f'status_code:{response.status_code}, broken_link:{url}, page source:{url_combo[1]}\n')
                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {url}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1
                print(f'counter = {self.counter}')
                print(f'remaining links number {self.web_links.qsize()}')
                if self.counter == 0 and self.web_links.qsize() == 0:
                    self.file.close()
                    sys.exit()
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
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    self.file.write(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}\n')
                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
            finally:
                self.web_links.task_done()
                self.counter -= 1

                print(f'counter = {self.counter}')
                print(f'remaining detected tasks{self.web_links.qsize()}')
                if self.counter == 0 and self.web_links.qsize() == 0:
                    self.file.close()
                    sys.exit()
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
            t.start()
        self.web_links.join()

if __name__ == '__main__':
    ws = web_spider()
    base_url = 'https://sites.research.unimelb.edu.au/research-funding'
    ws.main(base_url)