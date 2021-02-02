# imports
from pywikibot.family import Family
from pywikibot import config2 as config
from pywikibot import pagegenerators

import pywikibot
import requests
import re

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CATEGORY_NAME = "Category:Pages with the Cats template"
REFERENCE_PAGE = "Break Cats Bot Last Page"
PAGES_TO_GO_THROUGH = 25
site = pywikibot.Site()
API_URL = site.protocol() + "://" + site.hostname() + site.apipath()

def build_api_url() -> str:
    '''
    Returns the URL for the site's URL. 
    '''
    site = pywikibot.Site()
    return site.protocol() + "://" + site.hostname() + site.apipath()



def find_cats(s: str) -> str:
    '''
    Given a line in a wiki page, uses regex to
    figure out if the line has a Cats template.
    If it does, it returns the string with the Cats template. 
    Otherwise, returns None.
    '''
    regex_string = r"(.*)(\{\{Cats\|([^{}]*)\}\})(.*)"
    x = re.match(regex_string, s)

    if x is not None:
        # if there was a cats template
        return x.group(2)
    else:
        # if there was no Cat template
        return None

def get_cats(s: str) -> str:
    '''
    Given a string with the Cats template,
    returns a string with all the categories. 
    '''
    no_brackets = s.strip("{}")
    categories = no_brackets.split("|")[1:]

    output_list = []
    for category in categories:
        # account for empty strings
        if len(category) >= 1:
            output_list.append(f"[[Category:{category}]]")
    
    return '\n'.join(output_list)

def break_category_templates(page: pywikibot.Page) -> None:
    text = (page.text).split('\n')

    found_cats = False

    for line in text:
        # preliminary test to make sure we have a line with "Cats"
        # before we start all the regex searches
        if "Cats" in line:
            template_str = find_cats(line)

            if template_str is not None:
                found_cats = True
                categories_str = get_cats(template_str)
                page.text = page.text.replace(template_str, categories_str)
        
    # finally, remove the category
    # category_to_remove = f"[[{CATEGORY_NAME}]]"
    # page.text = page.text.replace(category_to_remove, "")

    # confirm changes
    if found_cats:
        page.save("Replace Categories template with individual category links. ")



def get_page_start() -> str:
    '''
    Returns the page that this bot is supposed to start editing from,
    according to this bot's reference page. 
    '''
    page = pywikibot.Page(pywikibot.Site(), REFERENCE_PAGE)
    return page.text.split('\n')[0]

def set_page_start(new_start: str) -> None:
    '''
    Sets the page that this bot will start from next to the string given.
    '''
    page = pywikibot.Page(pywikibot.Site(), REFERENCE_PAGE)
    page.text = new_start
    page.save("Store new page from last execution.")

def pages_from(start_point: str) -> "page generator":
    '''
    Returns a generator with 25 pages starting from
    the given page.
    '''
    my_session = requests.Session()

    api_arguments= {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": start_point,
        "aplimit": PAGES_TO_GO_THROUGH
    } 

    request = my_session.get(url=API_URL, params=api_arguments, verify=False)
    data = request.json()

    pages = data["query"]["allpages"]
    return pages

def run() -> None:
    '''
    Runs the bot on a certain number of pages.
    Records the last page the bot saw on a certain Mediawiki page.
    '''
    start_page_title = get_page_start()
    last_page_seen = ""

    pages_to_run = pages_from(start_page_title)

    for page in pages_to_run:
        last_page_seen = page['title']
        real_page = pywikibot.Page(site, last_page_seen)
        break_category_templates(real_page)
    
    if len(list(pages_to_run)) < PAGES_TO_GO_THROUGH:
        # if we hit the end, then loop back to beginning
        set_page_start("")
    else:
        # otherewise, just record the last page seen
        set_page_start(last_page_seen)



if __name__ == "__main__":
    run()
