from django.shortcuts import render
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
import requests
from bs4 import BeautifulSoup

def index(request):
    return render(request, 'index.html')

def search_link(request):
    if request.method == 'POST':
        url = request.POST['url']
        results = scrape_pages(url)
        return render(request, 'results.html', {'results': results})
    return render(request, 'index.html')

def scrape_pages(baseurl):
    broken_links = []
    visited = set()
    visited_or_about_to_visit = set()
    to_visit_list = list()
    
    # base url don't have parent in pattern [current link, source page link]
    to_visit_list.append([baseurl, None])
    
    while to_visit_list:
        url_combo = to_visit_list.pop(0)
        url = url_combo[0]
        if url in visited:
            continue

        try:
            response = requests.get(url)
            visited.add(url)
            visited_or_about_to_visit.add(url)
            
            if response.status_code == 200:
                # For external links, just need to check accessibility, no need to find sublink
                if not url.startswith(baseurl):
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                # print(url)

                # Find all links on the page
                for link in soup.find_all('a', href=True):
                    href = link['href']

                    # Check if the link is already in the list to avoid repeats
                    if href not in visited_or_about_to_visit:
                        visited_or_about_to_visit.add(href)
                        to_visit_list.append([href, url])
                        print('New link found:', href)
            else:
                print(f'Broken link {url} found with status {response.status_code}')
                broken_links.append({'url': url, 'source': url_combo[1], 'status_code': response.status_code})

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    return broken_links

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
