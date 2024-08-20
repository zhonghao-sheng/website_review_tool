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
        self.UOM_sign_links = list()
        self.uom_sign_link_file = open('uom_links.txt','w')
        self.counter = 0
        self.broken_links = list()

    def put_url(self, baseurl):
        self.web_links.put([baseurl, None])
        self.counter += 1
        self.baseurl = baseurl
    # def add_uom_sign_link(self, link, source_link):
    #     self.UOM_sign_links.append({'url': link, 'source_link': source_link})
    #
    # def write_uom_sign_link(self, link, source_link):
    #     self.uom_sign_link_file.write(f'uom link:{link}, page source:{source_link}\n')
    # def deal_uom_sign_link(self, link, source_link):
    #     self.add_uom_sign_link(link, source_link)
    #     self.write_uom_sign_link(link, source_link)
    # def add_broken_link(self, link, source_link):
    #     self.broken_links.append({'url': link, 'source_link': source_link})
    #
    # def write_broken_link(self, link, source_link, response_status):
    #     self.broken_link_file.write(f'status:{response_status}, broken link: {link}, page source: {source_link}')
    # def deal_broken_link(self, link, source_link, response_status):
    #     self.add_broken_link(link, source_link)
    #     self.write_broken_link(link, source_link, response_status)

    def get_more_links(self):
        while True:
            link_combo = self.web_links.get()

            link = link_combo[0]
            source_link = link_combo[1]
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
                                print(f'not responsible for checking mails {href}')
                            print('new links founded', href)
                else:
                    # if response.status_code ==403:
                    #     self.uom_sign_link_file.write(f'uom link:{link}, page source:{source_link}\n')
                    #     self.UOM_sign_links.append({'url': link, 'source_link': source_link})
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    self.broken_link_file.write(
                        f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}\n')
                    self.broken_links.append(
                        {'link': link, 'status_code': response.status_code, 'page source': link_combo[1]})
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
            source_link = link_combo[1]
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
                    # if response.status_code ==403:
                    #     self.uom_sign_link_file.write(f'uom link:{link}, page source:{source_link}\n')
                    #     self.UOM_sign_links.append({'url': link, 'source_link': source_link})
                    print(f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}')
                    self.broken_link_file.write(
                        f'status_code:{response.status_code}, broken_link:{link}, page source:{link_combo[1]}\n')
                    self.broken_links.append(
                        {'url': link, 'status_code': response.status_code, 'page source': link_combo[1]})

                    print(f'now the queue size is {self.web_links.qsize()}')
            except Exception as e:
                print(f'error fetch {link}, {str(e)}')
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

#
# def scrape_pages(baseurl):
#     broken_links = []
#     visited = set()
#     visited_or_about_to_visit = set()
#     to_visit_list = list()
#
#     # base url don't have parent in pattern [current link, source page link]
#     to_visit_list.append([baseurl, None])
#
#     while to_visit_list:
#         url_combo = to_visit_list.pop(0)
#         url = url_combo[0]
#         if url in visited:
#             continue
#
#         try:
#             response = requests.get(url)
#             visited.add(url)
#             visited_or_about_to_visit.add(url)
#
#             if response.status_code == 200:
#                 # For external links, just need to check accessibility, no need to find sublink
#                 if not url.startswith(baseurl):
#                     continue
#
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 # print(url)
#
#                 # Find all links on the page
#                 for link in soup.find_all('a', href=True):
#                     href = link['href']
#
#                     # Check if the link is already in the list to avoid repeats
#                     if href not in visited_or_about_to_visit:
#                         visited_or_about_to_visit.add(href)
#                         to_visit_list.append([href, url])
#                         print('New link found:', href)
#             else:
#                 print(f'Broken link {url} found with status {response.status_code}')
#                 broken_links.append({'url': url, 'source': url_combo[1], 'status_code': response.status_code})
#
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching {url}: {e}")
#
#     return broken_links

# def search_keyword(request):
#     if request.method == 'POST':
#         url = request.POST['url']
#         keyword = request.POST['keyword']
#         results = search_for_keyword(url, keyword)
#         return render(request, 'results.html', {'results': results, 'keyword': keyword})
#     return render(request, 'index.html')

# def search_for_keyword(url, keyword):
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(options=options)

#     try:
#         driver.get(url)

#         # Pause to allow user to log in manually if needed
#         input("Press Enter after logging in...")

#         # Check if logged in and search for keyword
#         body_text = driver.find_element(By.TAG_NAME, 'body').text
#         occurrences = body_text.lower().count(keyword.lower())

#     finally:
#         driver.quit()

#     return occurrences