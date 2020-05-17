"""
The default group of operations that pyscrapers has
"""
import logging
import shelve

import browser_cookie3
from pytconf.config import register_endpoint, register_function_group

import pyscrapers.core.utils
import pyscrapers.version
from pyscrapers.configs import ConfigDebugRequests, ConfigCookiesSource, ConfigSiteId
from pyscrapers.workers.drumeo import get_number_of_pages, get_courses, get_course_details, get_course_urls, \
    download_course
from pyscrapers.workers.facebook import scrape_facebook
from pyscrapers.workers.instagram import scrape_instagram
from pyscrapers.workers.mambaru import scrape_mambaru
from pyscrapers.workers.travelgirls import scrape_travelgirls
from pyscrapers.workers.vk import scrape_vk

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pyscapers commands"


def register_group_default():
    """
    register the name and description of this group
    """
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    configs=[],
    suggest_configs=[],
    group=GROUP_NAME_DEFAULT,
)
def version() -> None:
    """
    Print version
    """
    print(pyscrapers.version.VERSION_STR)


@register_endpoint(
    configs=[
        ConfigSiteId,
        ConfigDebugRequests,
        ConfigCookiesSource,
    ],
    suggest_configs=[],
    group=GROUP_NAME_DEFAULT,
)
def photos():
    """
    Download photo albums from various sites
    """
    if ConfigDebugRequests.debug:
        pyscrapers.core.utils.debug_requests()
    cookies = None
    if ConfigCookiesSource.browser == "firefox":
        cookies = browser_cookie3.firefox()
    if ConfigCookiesSource.browser == "chrome":
        cookies = browser_cookie3.chrome()

    urls = []
    if ConfigSiteId.site == "facebook":
        urls = scrape_facebook(ConfigSiteId.user_id, cookies)
    if ConfigSiteId.site == "instagram":
        urls = scrape_instagram(ConfigSiteId.user_id, cookies)
    if ConfigSiteId.site == "travelgirls":
        urls = scrape_travelgirls(ConfigSiteId.user_id, cookies)
    if ConfigSiteId.site == "vk":
        urls = scrape_vk(ConfigSiteId.user_id, cookies)
    if ConfigSiteId.site == "mamba.ru":
        urls = scrape_mambaru(ConfigSiteId.user_id, cookies)
    pyscrapers.core.utils.download_urls(urls, start=ConfigSiteId.start)


@register_endpoint(
    configs=[
        ConfigDebugRequests,
        ConfigCookiesSource,
    ],
    suggest_configs=[],
    group=GROUP_NAME_DEFAULT,
)
def drumeo():
    """
    Download videos from drumeo
    """
    if ConfigDebugRequests.debug:
        pyscrapers.core.utils.debug_requests()
    cookies = None
    if ConfigCookiesSource.browser == "firefox":
        cookies = browser_cookie3.firefox()
    if ConfigCookiesSource.browser == "chrome":
        cookies = browser_cookie3.chrome()

    logger = logging.getLogger(__name__)
    courses = False
    reload = {}
    with shelve.open("cache.db") as d:
        if "courses" in d:
            list_of_courses = d["courses"]
            print("got from cache [{}] courses".format(len(list_of_courses)))
        else:
            pages = get_number_of_pages(courses=courses, cookies=cookies)
            print("number of pages is [{}]".format(pages))
            list_of_courses = get_courses(pages, courses=courses, cookies=cookies)
            print("got [{}] courses".format(len(list_of_courses)))
            d["courses"] = list_of_courses
        for i, course in enumerate(list_of_courses):
            logger.info("course number [%s]", i)
            if course.number in d and course.number not in reload:
                list_of_courses[i] = d[course.number]
                logger.info("got from cache [%s]", list_of_courses[i])
            else:
                get_course_details(course, courses=courses, cookies=cookies)
                get_course_urls(course, courses=courses, cookies=cookies)
                print(course)
                d[course.number] = course
            download_course(list_of_courses[i])