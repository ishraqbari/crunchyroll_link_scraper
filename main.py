from distutils.debug import DEBUG
from time import sleep
from weakref import proxy
import cfscrape
from requests.structures import CaseInsensitiveDict
import json
import logging
import re

proxies = {"http": '127.0.0.1:8080', "https": '127.0.0.1:8080'}

logging.basicConfig(level=logging.WARNING)

url = "https://www.crunchyroll.com/series/GRDV0019R/jujutsu-kaisen"

headers = CaseInsensitiveDict()
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"
headers["Accept"] = "application/json, text/plain, */*"
headers["Accept-Encoding"] = "gzip, deflate"
headers["Authorization"] = "Basic Y3Jfd2ViOg=="
headers["Content-Type"] = "application/x-www-form-urlencoded"

session = cfscrape.create_scraper()
resp = json.loads(session.post('https://www.crunchyroll.com/auth/v1/token',data="grant_type=client_id",headers=headers).text)

logging.info("Call to '/auth/v1/token' complete")


headers["Authorization"] = "Bearer {}".format(resp['access_token'])

logging.debug("Bearer token is {}".format(resp['access_token']))

resp = json.loads(session.get('https://www.crunchyroll.com/index/v2',headers=headers).text)

cms_web = resp['cms_web']

print('Authorization complete.')
url  = input('Please provide the series URL: ')
match = re.search('/series/(?P<token>[A-Z0-9]+)/',url)
print(match)
if match:
    seriesToken =  match.group('token')
else:
    raise Exception("Sorry, series token not found.") 


seriesURL= 'https://www.crunchyroll.com/cms/v2{bucket}/seasons?series_id={seriesToken}&locale=en-US&Signature={signature}&Policy={policy}&Key-Pair-Id={key}'.format(bucket=cms_web['bucket'],seriesToken=seriesToken,signature=cms_web['signature'],policy=cms_web['policy'],key=cms_web['key_pair_id'])
print(seriesURL)
seriesItems = json.loads(session.get(seriesURL,headers=headers).text)['items']
for i in range(len(seriesItems)):
    print('{itemNumber}: Title: {title}, season_id: {season}, is_subbed: {subbed}, is_dubbed: {dubbed}'.format(itemNumber=i, title=seriesItems[i]['title'],season=seriesItems[i]['id'], subbed=seriesItems[i]['is_subbed'], dubbed = seriesItems[i]['is_dubbed']))

season_id = season=seriesItems[int(input('Please select a season: '))]['id']
print(season_id)
seasonURL= 'https://www.crunchyroll.com/cms/v2{bucket}/episodes?season_id={seriesToken}&locale=en-US&Signature={signature}&Policy={policy}&Key-Pair-Id={key}'.format(bucket=cms_web['bucket'],seriesToken=season_id,signature=cms_web['signature'],policy=cms_web['policy'],key=cms_web['key_pair_id'])

logging.debug("Season URL is {}".format(seasonURL))

episodes = session.get(seasonURL,headers=headers,proxies=proxies, verify=False).json().get("items")
for i in range(len(episodes)):
    print('https://www.crunchyroll.com/watch/{id}/{slug_title}'.format(id=episodes[i]['id'],slug_title=episodes[i]['slug_title']))

