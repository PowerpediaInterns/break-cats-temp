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
NUMBER_OF_PAGES = 25

def build_api_url() -> str:
    '''
    Returns the URL for the site's URL. 
    '''
    site = pywikibot.Site()
    return site.protocol() + "://" + site.hostname() + site.apipath()


def pages_from(start_point: str) -> "Page Generator":
    '''
    Returns a generator of up to 500 pages starting from
    the given start point. 
    '''
    my_session = requests.Session()
    url = build_api_url()

    api_arguments= {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": start_point,
        "aplimit": 20
    } 

    request = my_session.get(url=url, params=api_arguments, verify=False)
    data = request.json()

    pages = data["query"]["allpages"]
    return pages

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
    for line in text:
        # preliminary test to make sure we have a line with "Cats"
        # before we start all the regex searches
        if "Cats" in line:
            template_str = find_cats(line)

            if template_str is not None:
                categories_str = get_cats(template_str)
                page.text = page.text.replace(template_str, categories_str)
        
    # finally, remove the category
    category_to_remove = f"[[{CATEGORY_NAME}]]"
    page.text = page.text.replace(category_to_remove, "")

    # confirm changes
    page.save("Replace Categories template with individual category links. ")

def run() -> None:
    '''
    Breaks apart category templates in all pages of the wiki.
    '''
    # new page generator
    site = pywikibot.Site()
    cat = pywikibot.Category(site, CATEGORY_NAME)
    gen = pagegenerators.CategorizedPageGenerator(cat)

    pages_left = NUMBER_OF_PAGES

    for page in gen:
        break_category_templates(page)
        pages_left -= 1

        if pages_left == 0:
            break

if __name__ == "__main__":
    run()
