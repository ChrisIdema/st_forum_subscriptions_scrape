import browser_cookie3
import requests
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse



def main():
    # process arguments:
    parser = argparse.ArgumentParser("st_forum_subscriptions.py",
                                    description='Scrape subscriptions from your st community forum account before they are deleted in migration.'
                                    #,epilog=''
                                    )
    parser.add_argument("--browser", "-b", help="Select your browser (e.g. firefox or chrome, chrome is default)", type=str, default='chrome')    
    args = parser.parse_args()

    browser = args.browser

    max_num_pages = 100

    session = requests.Session()

    if browser.lower() == 'chrome':
        cookies = browser_cookie3.chrome(domain_name="community.st.com")
    elif browser.lower() == 'firefox':
        cookies = browser_cookie3.firefox(domain_name="community.st.com")
    else:
        print("unknown browser")
        return -1

    session.cookies.update(cookies)

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://community.st.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })


    items = []
    page=1
    while True:
        file_path = f'page{page}.html'
        html = None
        delay = False
        if not os.path.exists(file_path):
            delay = True
            url = f"https://community.st.com/t5/user/myprofilepage/tab/user-subscriptions/page/{page}"
            r = session.get(url)
            #print(r.status_code)
            if r.status_code == 200:
                html = r.text
                with open(file_path,'w',encoding="utf-8") as f:
                    f.write(html)
        else:
            #print('file exists')
            with open(file_path,'r',encoding="utf-8") as f:
                html = f.read()

        soup = BeautifulSoup(html, "html.parser")



        if page == 1:
            last_page_link = soup.select_one("li.lia-paging-page-last a")

            if last_page_link:
                last_page = int(last_page_link.get_text(strip=True))
            else:
                last_page = 1

            print("number of pages: ", last_page)

        for a in soup.select("a.subscription-thread"):
            title = a.get_text(strip=True)
            href = urljoin("https://community.st.com", a.get("href"))
        

            items.append({
                "title": title,
                "url": href,
            })


        if page != last_page and page < max_num_pages:
            page += 1
            if delay:
                time.sleep(1)
        else:
            break

    for item in items:
        print(item["title"])
        print(item["url"])
        print()

    if len(items) > 0:
        with open('subscriptions.csv','w',encoding="utf-8") as f:
            for item in items:
                html = f.write(f'{item["title"]},{item["url"]}\n')


if __name__ == '__main__':
    main()