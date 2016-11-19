#!/usr/bin/python3

'''
This script scrapes photos from travelgirls.com

For instance if you see a url like this:
    http://www.travelgirls.com/member/[user_id]
then the id for this script will be:
    [user_id]
'''

import requests # for post
import lxml.html # for fromstring
import lxml.etree # for tostring
import json # for loads
import shutil # for copyfileobj
import sys # for argv
import logging # for basicConfig, getLogger
import argparse  # for ArgumentParser
import browser_cookie3 # for firefox
import scrape.utils # for download_urls, get_real_content


# set up the logger
logging.basicConfig()
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

def main():
    # command line parsing
    parser = argparse.ArgumentParser(
            description='''download photos from travelgirls'''
    )
    parser.add_argument(
            '-i',
            '--id', 
            help='''id of the user to download the albums of
            For instance if you see a url like this:
                http://www.travelgirls.com/member/[user_id]
            then the id for this script will be:
                [user_id]
            '''
    )
    args = parser.parse_args()
    if args.id is None:
        parser.error('-i/--id must be given')

    # load cookies from browser
    cookies=browser_cookie3.firefox()

    main_url='http://www.travelgirls.com/member/{id}'.format(id=args.id)
    r = requests.get(main_url, cookies=cookies)
    root = scrape.utils.get_real_content(r)

    urls=[]
    e_a = root.xpath('//a[contains(@class,\'photo\')]')
    for x in e_a:
        #print(lxml.etree.tostring(x, pretty_print=True))
        children=x.getchildren()
        assert len(children)==1
        img=children[0]
        url=scrape.utils.add_http(img.attrib['src'], main_url)
        url=url.replace('mini','')
        urls.append(url)

    scrape.utils.download_urls(urls)

if __name__ == '__main__':
    main()
