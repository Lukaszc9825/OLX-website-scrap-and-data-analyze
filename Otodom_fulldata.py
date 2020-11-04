from Otodom_scraper import Scraper
from Otodom_scraper import Json_file
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

df1 = pd.read_json('otodom_rent_data')
df2 = pd.read_json('otodom_sale_data')

districts = pd.read_excel('districts.xlsx')
districts = districts.drop(columns = ['Gmina', 'Województwo',
 'Identyfikator miejscowości z krajowego rejestru urzędowego podziału terytorialnego kraju TERYT','Dopełniacz','Przymiotnik'])

def add_column(*args):
	for arg in args:
		arg_temp = arg.copy()
		arg['Rent'] = 'no data'
		arg['Deposit'] = 'no data'
		arg['Number of rooms'] = 'no data'
		arg['built in'] = 'no data'
		arg['floor'] = 'no data'
		arg['number of floors'] = 'no data'
		arg['price'] = arg['price'].str.replace('zł', '').str.replace(',', '.').str.replace(' ','').str.replace('~','')
		arg['area'] = arg['area'].str.replace('m²', '').str.replace(',','.').str.replace(' ','')
		arg['localization'] = arg_temp['localization'].str.split(',',expand = True)[0]
		arg['localization 1'] = arg_temp['localization'].str.split(',',expand = True)[1]
		arg['localization 2'] = arg_temp['localization'].str.split(',',expand = True)[2]
		arg['district'] = add_district(arg)
		
def find_data(*args):
	for arg in args:

		for index,href in enumerate(arg['href']):
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
					arg.at[index,'Rent'] = "+" + temp.get('Czynsz - dodatkowo')
				elif 'Czynsz' in temp:
					arg.at[index,'Rent'] = temp.get('Czynsz')
				elif 'Czynsz - dodatkowo' in temp == False and 'Czynsz' in temp == False:
					arg.at[index,'Rent'] = 0
	      
				# add deposit to data frame
				if 'Kaucja' in temp:
					arg.at[index,'Deposit'] = temp.get('Kaucja')
				elif 'Kaucja' in temp == False:
					arg.at[index,'Deposit'] = 0
	      
				# add number of rooms to data frame
				if 'Liczba pokoi' in temp:
					arg.at[index,'Number of rooms'] = temp.get('Liczba pokoi')
				elif 'Liczba pokoi' in temp == False:
					arg.at[index,'Number of rooms'] = 0

				# add year of building to data frame
				if 'Rok budowy' in temp:
					arg.at[index,'built in'] = temp.get('Rok budowy')
				elif 'Rok budowy' in temp == False:
					arg.at[index,'built in'] = 0

				# add floor to data frame
				if 'Piętro' in temp:
					if temp.get('Piętro') == 'parter':
						arg.at[index,'floor'] = '0'
					else:
						arg.at[index,'floor'] = temp.get('Piętro')
				elif 'Piętro' in temp == False:
					arg.at[index,'floor'] = 'no data'

				# add number of floors to data frame
				if 'Liczba pięter' in temp:
					arg.at[index,'number of floors'] = temp.get('Liczba pięter')
				elif 'Liczba pięter' in temp == False:
					arg.at[index,'number of floors'] = 0

def add_district(df):
	temp =[]
	for city in df['localization']:

		if districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'miasto')].empty ==  False:
			d = districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'miasto')]
			temp.append('powiat ' + d.iloc[0]['Powiat (miasto na prawach powiatu)'])
		
		elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'wieś')].empty ==  False:
			d = districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'wieś')]
			temp.append('powiat ' + d.iloc[0]['Powiat (miasto na prawach powiatu)'])

		elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'osada')].empty ==  False:
			d = districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'osada')]
			temp.append('powiat ' + d.iloc[0]['Powiat (miasto na prawach powiatu)'])

		elif districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'kolonia')].empty ==  False:
			d = districts.loc[(districts['Nazwa miejscowości '] == city) & (districts['Rodzaj'] == 'kolonia')]
			temp.append('powiat ' + d.iloc[0]['Powiat (miasto na prawach powiatu)'])

		elif city == 'Stargard':
			temp.append('powiat stargardzki')

		else:
			print(city)

	return temp


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

	add_column(df1,df2)
	find_data(df1,df2)
	df3 = pd.concat([df1, df2], ignore_index=True)
	df3.to_json('otodom_full_data', orient= 'split')