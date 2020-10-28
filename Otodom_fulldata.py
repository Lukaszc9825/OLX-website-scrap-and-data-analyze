from Otodom_scraper import Scraper
from Otodom_scraper import Json_file
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

df1 = pd.read_json('otodom_rent_data')
df2 = pd.read_json('otodom_sale_data')


df1['Rent'] = 'no data'
df1['Deposit'] = 'no data'
df1['Number of rooms'] = 'no data'
df1['built in'] = 'no data'
df1['floor'] = 'no data'
df1['number of floors'] = 'no data'


def find_data(df):
  for index,href in enumerate(df['href']):
    page = requests.get(href, headers = headers)
    soup = bs(page.content, 'html.parser')
    mess = soup.find_all(class_ ='section-overview')
    for m in mess:
      data = m.find('ul')
      data = data.find_all('li')
      temp = {}
      for d in data:
        temp[d.get_text().split(":")[0]] = d.get_text().split(":")[1].strip()
      
      # add rent price to data frame
      if 'Czynsz - dodatkowo' in temp:
        df.at[index,'Rent'] = "+" + temp.get('Czynsz - dodatkowo')
      elif 'Czynsz' in temp:
        df.at[index,'Rent'] = temp.get('Czynsz')
      elif 'Czynsz - dodatkowo' in temp == False and 'Czynsz' in temp == False:
        df.at[index,'Rent'] = 0
      
      # add deposit to data frame
      if 'Kaucja' in temp:
        df.at[index,'Deposit'] = temp.get('Kaucja')
      elif 'Kaucja' in temp == False:
        df.at[index,'Deposit'] = 0
      
      # add number of rooms to data frame
      if 'Liczba pokoi' in temp:
        df.at[index,'Number of rooms'] = temp.get('Liczba pokoi')
      elif 'Liczba pokoi' in temp == False:
        df.at[index,'Number of rooms'] = 0

      # add year of building to data frame
      if 'Rok budowy' in temp:
        df.at[index,'built in'] = temp.get('Rok budowy')
      elif 'Rok budowy' in temp == False:
        df.at[index,'built in'] = 0

      # add floor to data frame
      if 'Piętro' in temp:
        if temp.get('Piętro') == 'parter':
          df.at[index,'floor'] = '0'
        else:
          df.at[index,'floor'] = temp.get('Piętro')
      elif 'Piętro' in temp == False:
        df.at[index,'floor'] = 'no data'

      # add number of floors to data frame
      if 'Liczba pięter' in temp:
        df.at[index,'number of floors'] = temp.get('Liczba pięter')
      elif 'Liczba pięter' in temp == False:
        df.at[index,'number of floors'] = 0

  return df

if __name__ == '__main__':

	url1 = 'https://www.otodom.pl/wynajem/mieszkanie/'
	url2 = 'https://www.otodom.pl/sprzedaz/mieszkanie/'
	headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

	scraper1 = Scraper(url1, headers)
	scraper2 = Scraper(url2, headers)
	j = Json_file()
	j.save("otodom_rent_data", scraper1.apartments_list)
	j.save("otodom_sale_data", scraper2.apartments_list)

	find_data(df1)
	df1.to_json('otodom_full_data', orient= 'split')