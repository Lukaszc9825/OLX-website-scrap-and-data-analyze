import requests
from bs4 import BeautifulSoup as bs

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
			
			# Separate single informations about product
			self.info = product.find_all('td')
			for i, data in enumerate(self.info):
				#print(data.prettify())
				if i == 0:
					for temp in data.find_all('a'):
						self.product_info['auction link'] = temp.get('href')
					for temp in data.find_all('img'):
						self.product_info['photo link'] = temp.get('src')
				
				elif i == 1:
					self.product_info['auction name'] = data.find('strong').get_text()
					self.product_info['category'] = data.find('small').get_text().strip()

				elif i == 2:
					self.product_info['price'] = data.find('strong').get_text()

				elif i ==3:
					for j, x in enumerate(data.find_all('span')):
						if j == 0:
							self.product_info['location'] = x.get_text()
						else:
							self.product_info['add time'] = x.get_text()
					
			self.products_list.append(self.product_info.copy())			
		return self.products_list

	def get_number_of_pages(self):
		self.mess = self.soup.find_all(class_ = 'block br3 brc8 large tdnone lheight24')
		for index, number in enumerate(self.mess):
			if index == 12:
				self.last = number.get_text().strip()
		return int(self.last)		

	def all_pages(self):
		for i in range(1, Scraper.get_number_of_pages(self)):
			self.url2 = 'https://www.olx.pl/elektronika/?page=' + str(i+1)
			self.page2 = requests.get(self.url2, headers=self.headers)
			self.soup2 = bs(self.page2.content, 'html.parser')
			Scraper.separate(self, self.soup2)


if __name__ == '__main__':

	url = 'https://www.olx.pl/elektronika/'

	headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

	scraper = Scraper(url, headers)
	print(scraper.products_list)
