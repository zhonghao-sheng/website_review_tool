from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import JoinableQueue as Queue
broken_links = []


def check_link(url):
    try:

        response = requests.get(url)

        return url, response.status_code

    except requests.RequestException as e:

        return url, str(e)


def scrape_pages(baseurl):
    visited_or_about_to_visit = set()

    to_visit_list = Queue()
    to_visit_list.put([baseurl, None])

    with open('broken_links.txt', 'w') as f:

        with ThreadPoolExecutor(max_workers=30) as executor:

            while to_visit_list:

                url_combo = to_visit_list.get()
                to_visit_list.task_done()

                url = url_combo[0]

                visited_or_about_to_visit.add(url)

                future = executor.submit(check_link, url)

                # Process the results as they complete

                for future in as_completed([future]):

                    link, status = future.result()

                    if status == 200:

                        # For external links, just check accessibility

                        if not link.startswith(baseurl):
                            continue

                        soup = BeautifulSoup(requests.get(link).content, 'html.parser')

                        for link in soup.find_all('a', href=True):

                            href = link['href']
                            # exclude mails
                            if "mailto:" in href:
                                continue

                            if href not in visited_or_about_to_visit:
                                visited_or_about_to_visit.add(href)

                                to_visit_list.put([href, url])

                                print('New link found:', href)

                    else:

                        print(f'Broken link found: {link} with status {status}')

                        broken_links.append((link, status))

                        f.write(f'{link} - {status}\n')  # Write broken link and status to file
                #  to release one task

    to_visit_list.join()
if __name__ == '__main__':
    scrape_pages('https://sites.research.unimelb.edu.au/research-funding')

