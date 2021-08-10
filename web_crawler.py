import fileinput
import threading
import time
import concurrent.futures
import requests
import re
import html2text
import sys
import os
import datetime as dt
import json
from bs4 import BeautifulSoup


thread_local = threading.local()
DEBUG = False


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        pid_str = '(pid ' + str(os.getpid()) + ')'
        print('started', method.__name__, args, kw, pid_str, 'at', time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        result = method(*args, **kw)
        te = time.time()
        print('finished', method.__name__, args, kw, pid_str, 'at', time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        print('%r took %s' % (method.__name__, dt.timedelta(seconds=(te - ts))))
        return result

    return timed


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def get_phone_numbers(html_text, url):
    # ^\s*(?:\+?(\d{1,4}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$
    # \s(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\s
    # [+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]* -- bad one- matches any number
    # \(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5} ?-?[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?
    # \s[+#*\(\)\[\]]*([0-9][ ext+-pw#*\(\)\[\]]*){6,45}\s -- good one possibly
    # ^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$
    phone_pattern = r"\s[+#*\(\)\[\]]*([0-9][ ext+-pw#*\(\)\[\]]*){6,45}\s"
    rule = re.compile(phone_pattern)
    phones_list = [re.search(rule, line)[0] for line in html_text.split('\n') if (re.search(rule, line))]
    if not phones_list:
        sys.stderr.write(f'Phone numbers not found or not recognized in url: {url}')
    phones_list = [re.sub(r"[/!@#$%^&*\[\]{};:,-]", ' ', v) for v in phones_list]
    return phones_list


def get_logo_img_url(html, url):
    soup = BeautifulSoup(html, "html.parser")
    images = soup.findAll('img')
    try:
        src_contents = [(image.get('class'), image.get('src')) for image in images]
        for class_attr, src_attr in src_contents:
            if url.rsplit('/', 2)[0] not in src_attr:
                src_attr = str(url.rsplit('/', 2)[0]) + str(src_attr)
            class_attr = class_attr[0] if isinstance(class_attr, list) else class_attr
            if class_attr:
                if ('logo' in str.lower(class_attr)) or ('logo' in str.lower(src_attr)):
                    return src_attr
            else:
                if 'logo' in str.lower(src_attr):
                    return src_attr
    except Exception as e:
        sys.stderr.write(f'Getting logo img url failed for site: {url}. \nException: {e}')
        return ''


def handle_html(html):
    h = html2text.HTML2Text()
    html_text = h.handle(str(html))
    return html_text


def fetch_info(url):
    session = get_session()
    page_info = {}
    with session.get(url, timeout=5) as response:
        html = response.content
        html_text = handle_html(html)
        phone_numbers = get_phone_numbers(html_text, url)
        img_url = get_logo_img_url(html, url)
        page_info['logo'] = img_url
        page_info['phones'] = phone_numbers
        page_info['website'] = url
        json_obj = json.dumps(page_info)
        print(json_obj)


@timeit
def main():
    sites_list = []
    for site_url in fileinput.input():
        url = str(site_url).replace('\n', '')
        sites_list.append(url)
    # print(sites_list)
    # max_workers=10
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(fetch_info, sites_list)


@timeit
def main_debug():
    sites_list = ['https://www.cmsenergy.com/contact-us/default.aspx']
    # for site_url in fileinput.input():
    #     url = str(site_url).replace('\n', '')
    #     sites_list.append(url)
    # print(sites_list)
    for url in sites_list:
        fetch_info(url)


if __name__ == '__main__':
    if not DEBUG:
        main()
    else:
        main_debug()
