import requests
import json
from bs4 import BeautifulSoup as bs
from datetime import date
from datetime import datetime

class Scraper(object):
	
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
		self.page = requests.get(url, headers=headers)

		# Convert to bs object
		self.soup = bs(self.page.content, 'html.parser')

		# Contains all informations about product
		self.product_info = {}
		self.products_list = []

		Scraper.separate(self, self.soup)
		Scraper.all_pages(self)

	
	# Separate the products from each other 
	def separate(self,soupy):
		
		# Save all off the products into a list
		self.products = soupy.find_all(class_ = 'offer-wrapper')
		
		for product in self.products:
			
			# Separate one product table into small tables with single informations
			self.info = product.find_all('td')
			for i, data in enumerate(self.info):
				
				#first table which contains auction and photo link
				if i == 0:
					for temp in data.find_all('a'):
						self.product_info['auction link'] = temp.get('href')
					for temp in data.find_all('img'):
						self.product_info['photo link'] = temp.get('src')
				
				#second table which contains auction name and category			
				elif i == 1:
					self.product_info['auction name'] = data.find('strong').get_text()
					self.product_info['category'] = data.find('small').get_text().strip().replace('»', '->')

				#third table which contains price converted into float if posiible (because of "zamienię" word)
				elif i == 2:
					try:
						self.product_info['price (zł)'] = float(data.find('strong').get_text().replace('zł', '').replace(' ',''))
					except:
						self.product_info['price (zł)'] = data.find('strong').get_text().replace('zł', '').replace(' ','')


				#last table which contains price	
				elif i ==3:
					for j, x in enumerate(data.find_all('span')):
						if j == 0:
							self.product_info['location'] = x.get_text()

						#change "dzisiaj" word into today date
						else:
							today = date.today()
							if 'dzisiaj' in x.get_text():
								self.product_info['date'] = today.strftime("%d/%m/%y")

							#change date format ex. 21 paź -> 21 10 2020 and then into datetime format 21/10/2020 
							else:
								dt = x.get_text().split()
								months = ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paź', 'lis', 'gru']
								for i, m in enumerate(months, start = 1):
									if dt[1] == m:
										dt[1] = str(i)
										dt = dt[0] + " " + dt[1] + " " + str(today.year)
										self.product_info['date'] = datetime.strptime(dt, '%d %m %Y').strftime("%d/%m/%y")
			

			#add dictionary to list with all products		
			self.products_list.append(self.product_info.copy())			
		return self.products_list

    #return information about the number of last page
	def get_number_of_pages(self):
		self.mess = self.soup.find_all(class_ = 'block br3 brc8 large tdnone lheight24')
		for index, number in enumerate(self.mess):
			if index == 12:
				self.last = number.get_text().strip()
		return int(self.last)		

	#make "separate" function fo all off the pages. (without first because of different url)
	def all_pages(self):
		for i in range(1, Scraper.get_number_of_pages(self)):
			self.url2 = 'https://www.olx.pl/elektronika/?page=' + str(i+1)
			self.page2 = requests.get(self.url2, headers=self.headers)
			self.soup2 = bs(self.page2.content, 'html.parser')
			Scraper.separate(self, self.soup2)

	#print list of dictionary in a more readable way (line by line)
	def display(self):
		for product in self.products_list:
			[print(key, value) for key, value in product.items()]



#help storage data in json file
class Json_file():

	def save(self, title, data):
		with open(title, 'w', encoding = 'utf-8') as f:
			json.dump(data, f, ensure_ascii = False, indent = 2)

	def load(self, title):
		with open(title, encoding = 'utf-8') as f:
			return json.load(f)



if __name__ == '__main__':

	url = 'https://www.olx.pl/elektronika/'

	headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

	scraper = Scraper(url, headers)
	j = Json_file()
	j.save("olx_data", scraper.products_list)
