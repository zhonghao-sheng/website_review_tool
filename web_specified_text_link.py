# same logic as search for broken links method while being simpler
# as only need to check if the string is contained in response.text
import requests

from bs4 import BeautifulSoup


def scrape_pages(baseurl, search_string):
    # the file used to record the broken links and its parent links
    with open('string_pattern_links.txt', 'w') as f:

        visited = set()
        to_visit_list = [base_url]



        while to_visit_list:

            url = to_visit_list.pop(0)
            if url in visited or url in to_visit_list:
                continue



            try:

                response = requests.get(url)

                visited.add(url)


                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')



                    # Print the current URL

                    print(url)
                    page_text = soup.get_text()

                    if search_string in page_text:
                        print("The specified string was found in the page source.", url)
                        f.write(url + '\n')
                    # Find all links on the page

                    for link in soup.find_all('a', href=True):

                        href = link['href']



                        # Check if the link already in the list to avoid repeat
                        if href.startswith(baseurl):
                            if href not in to_visit_list and href not in visited:
                                to_visit_list.append(href)

                                print('new links founded', href)
            # i guess no need to handle with error here? as only task is to search specified text
            except Exception as e:
                pass



# Replace with the base URL you want to scrape

base_url = 'https://sites.research.unimelb.edu.au/research-funding'

scrape_pages(base_url, search_string = "Funding Partners")