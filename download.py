from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import os
import codecs
import pickle
import requests
import json
import time
from tqdm import tqdm

MAX_INSTRUCTABLES_PAGE_NUM = 595
MAX_SNAPGUIDE_PAGE_NUM = 1068

class Crawler(object):
    def __init__(self):
        self.instructable_ids = []
        self.snapguide_ids = []

    def get_instructable_ids(self):
        for i in range(MAX_INSTRUCTABLES_PAGE_NUM + 1):
            if i == 0:
                page = "https://www.instructables.com/cooking/projects/"
            else:
                page = "https://www.instructables.com/cooking/projects/?page=" + str(i+1)

            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
            headers = {'User-Agent': ua}
            response = requests.get(page, headers=headers)
            if response.status_code is 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for hit in soup.find_all('div', attrs={'class' : 'category-projects-ible'}):
                    href = hit.find_all('a', attrs={'class' : 'ible-title'})[0].get("href")
                    self.instructable_ids.append(href)
        return self.instructable_ids

    def get_instructables_data(self, ids):
        recipes = []
        for idd in tqdm(ids):
            recipe = {}
            context = []
            url = "https://www.instructables.com" + idd
            soup = BeautifulSoup(requests.get(url).text, "html.parser")
            title = "None"
            try:
                title = soup.select('h1.header-title')[0].text.strip()
            except Exception as e:
                print (e)

            for stepi, hit in enumerate(soup.findAll('section', attrs={'class' : 'step'})):
                step = {}
                step_title = "None"
                try:
                    step_title = hit.find(attrs={'class' : 'step-title'}).text
                except Exception as e:
                    print (e)
                step['step_title'] = step_title
                step_body = hit.find(attrs={'class' : 'step-body'}).text
                step['step_text'] = step_body
                step['step_images'] = []
                imgi = 0
                for el in hit.findAll('img'):
                    if hit.find('div', attrs={'class': 'author-promo'}):
                        continue
                    rename = idd.strip().split("/")[2] + '_' + str(stepi) + '_' + str(imgi)+ ".jpg"
                    try:
                        step['step_images'].append( (el['src'], rename ))
                    except Exception as e:
                        step['step_images'].append(("None", rename))
                    imgi += 1
                context.append(step)
            recipe['title'] = title
            recipe['context'] = context
            recipes.append(recipe)
        return recipes

    def get_snapguide_ids(self):
        for i in range(MAX_SNAPGUIDE_PAGE_NUM):
            page = "https://snapguide.com/guides/topic/food/recent/?page=" + str(i)
            response = requests.get(page, headers={"User-Agent" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
            if response.status_code is 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for hit in soup.find_all('a'):
                    if hit.get("title") is not None \
                    and hit.get("class") is None \
                    and hit.get("itemprop") is None:
                        href = hit.get("href")
                        print(href)
                        self.snapguide_ids.append(href)
        return self.snapguide_ids

    def get_snapguide_data(self, snapguide_ids):
        recipes = []
        for idd in tqdm(snapguide_ids):
            recipe = {}
            context = []
            url = "https://snapguide.com" + idd
            try:
                os.system('wget -O index.html '+ url)
            except:
                continue
            soup = BeautifulSoup(open("index.html"), "html.parser")
            title = "None"
            try:
                title = soup.select('title')[0].text.strip()
            except Exception as e:
                print (e)
            recipe['title'] = title
            for stepi, hit in enumerate(soup.findAll('div', attrs={'class' : 'step-content'})):
                step = {}
                try:
                    step_title = hit.find(attrs={'class' : 'step-title'}).text
                except:
                    step_title = "None"
                step['step_title'] = step_title
                step_body = "None"
                try:
                    step_body = hit.find(attrs={'class' : 'caption'}).text
                except Exception as e:
                    print (e)
                step['step_text'] = step_body
                step['step_images'] = []
                imgi = 0
                for el in hit.findAll('img'):
                    if hit.find('img', attrs={'class': 'step-media'}):
                        if 'auto=webp' not in el['data-src']:
                            rename = idd.strip().split("/")[2] + '_' + str(stepi) + '_' + str(imgi)+ ".jpg"
                            step['step_images'].append( ("https:"+el['data-src'], rename ))
                        imgi += 1
                context.append(step)
            recipe['context'] = context
            recipes.append(recipe)
            os.system('rm index.html')
        return recipes

def main():
    crawler = Crawler()

    # Instructables (Cooking)
    if os.path.exists("./instructable_ids.pkl"):
        instructable_ids = pickle.load(open("./instructable_ids.pkl", 'rb'))
    else:
        instructable_ids = crawler.get_instructable_ids()
        pickle.dump(instructable_ids, open("instructable_ids.pkl", 'wb'))

    if not os.path.exists("./instructable_data.json"):
        instructables_data = crawler.get_instructables_data(instructable_ids)
        with open("instructables.json", 'w') as fp:
            json.dump(instructables_data, fp, indent=4)
    
    # Snapguide (Cooking)
    """
    if os.path.exists("./snapguide_ids.pkl"):
        snapguide_ids = pickle.load(open("./snapguide_ids.pkl", 'rb'))
    else:
        snapguide_ids = list(set(crawler.get_snapguide_ids()))
        pickle.dump(snapguide_ids, open("snapguide_ids.pkl", 'wb'))

    if not os.path.exists("./snapguide_data.json"):
        snapguide_data = crawler.get_snapguide_data(snapguide_ids)
        with open("snapguide.json", 'w') as fp:
            json.dump(snapguide_data, fp, indent=4)
    """

if __name__== "__main__":
    main()