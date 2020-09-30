"""
Utilities for ffnet.
"""
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs

import bs4
import requests


def get_urls_from_ffnet_category(url, sleep=1, since=-1):
    """
    Find all story URLs in a specified ffnet category.
    
    @param url: url to ffnet category
    @type url: L{str}
    @param sleep: time to sleep between each GET. Default: 1s
    @type sleep: L{int} or L{float}
    @param since: only return stories modified after this unix time
    @type since: L{int} or L{float}
    @return: a list of ffnet categories
    @rtype: L{list} of L{str}
    """
    page = requests.get(url, params={"srt": "1", "r": "10"}).text
    soup = bs4.BeautifulSoup(page, "html.parser")
    last_a = soup.find("a", text="Last")
    if last_a is not None:
        n_pages = int(parse_qs(urlparse(last_a["href"]).query)["p"][0])
    else:
        next_a = soup.find("a", text=re.compile("Next.*"))
        if next_a is None:
            n_pages = 1
        else:
            n_pages = int(parse_qs(urlparse(next_a["href"]).query)["p"][0])
    pages = [page]
    for i in range(1, n_pages + 1):
        url = "{}?srt=1&r=10&p={}".format(url, i)
        page = requests.get(url).text
        pages.append(page)
        time.sleep(sleep)
    all_urls = []
    for page in pages:
        urls_and_updates = find_ffnet_ids_and_update_time_from_str(page)
        for url, last_updated in urls_and_updates:
            if (since >= 0) and last_updated <= since:
                # not modified since 'since'
                continue
            if url not in all_urls:
                all_urls.append(url)
    return all_urls


def find_ffnet_ids_in_str(s):
    """
    Find all ffnet story IDs in a string.
    
    @param s: string to parse
    @type s: L{str}
    @return: the URLs of the stories
    @rtype: l{list} of L{str}
    """
    matches = re.findall(r"/s/[0-9]+/", s)
    urls = [urljoin("https://fanfiction.net/", e) for e in matches]
    return urls


def find_ffnet_ids_and_update_time_from_str(s):
    """
    Find all ffnet IDs and their last updated time in a html string.
    
    @param s: html string to parse
    @type s: L{str}
    @return: a list of tuples of (url, last_updated)
    @rtype: L{list} of L{tuple} of (L{str}, L{int})
    """
    soup = bs4.BeautifulSoup(s, "html.parser")
    story_as = soup.find_all("a", {"class": "stitle"})
    stories = []
    for story_a in story_as:
        url = urljoin("https://fanfiction.net/", story_a["href"])
        parent = story_a.parent
        spans = parent.find_all("span", {"data-xutime": True})
        last_updated = max([int(span["data-xutime"]) for span in spans])
        stories.append((url, last_updated))
    return stories


def get_ffnet_category_name_by_url(url):
    """
    Retrieve the name of a ffnet category from it's url.
    
    @param url: url of category
    @type url: L{str}
    @return: the name of the category
    @rtype: L{str}
    """
    r = requests.get(url)
    t = r.text
    soup = bs4.BeautifulSoup(t, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.contents[0]
    title = title[:title.find(" FanFiction Archive")].strip()
    return title
