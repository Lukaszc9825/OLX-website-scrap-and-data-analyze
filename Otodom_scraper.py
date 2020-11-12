import grequests
import json
from bs4 import BeautifulSoup as bs
import math
	
class Scraper(object):
	
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
		self.urls = []

		for voiv in Scraper.voivodeship_split(self.url):
			Scraper.deeper(self, voiv)

		self.reqs = [grequests.get(u, headers=headers) for u in self.urls]
		self.resp = grequests.map(self.reqs, size = 100)

		# Contains all informations about apartments
		self.apartment_info = {}
		self.apartments_list = []

		Scraper.make_all_req(self)

	
	# Separate the apartments from each other 
	def separate(self,soupy):
		
		# Save all off the apartments into a list
		self.apartments = soupy.find_all(class_ = 'offer-item-details')
		
		#loop for evry single apartment
		for ap in self.apartments:

	  		#take data from <a> section
	  		temp = ap.find('a')
	  		self.apartment_info['href'] = temp.get('href')
	  		self.apartment_info['area'] = temp.find('strong').get_text()
	  		self.apartment_info['advertisment name'] = temp.find(class_ = 'offer-item-title').get_text()
	  		
	  		#take data from <p> section	
	  		temp = ap.find('p')

	  		if 'mieszkanie na wynajem:' == temp.find('span').get_text().lower().strip():
	  			self.apartment_info['for rent/sale'] = 'rent'
	  		else:
	  			self.apartment_info['for rent/sale'] = 'sale'

	  
	  		self.apartment_info['localization'] = temp.get_text().split(':')[1].strip()
	  		self.apartment_info['price'] = ap.find(class_ = 'offer-item-price').get_text().replace('/mc', '').strip()
	  
	  		self.apartments_list.append(self.apartment_info.copy())

		return self.apartments_list	

	

	def voivodeship_split(url):
		voivodeship = ['dolnoslaskie',
		'kujawsko-pomorskie',
		'lubelskie',
		'lubuskie',
		'lodzkie',
		'malopolskie',
		'mazowieckie',
		'opolskie',
		'podkarpackie',
		'podlaskie',
		'pomorskie',
		'slaskie',
		'swietokrzyskie',
		'warminsko-mazurskie',
		'wielkopolskie',
		'zachodniopomorskie']

		voivodeship_urls = [url+voiv+'/' for voiv in voivodeship ]
		
		return voivodeship_urls	

	

	def get_annoucments_number(self, url):
		
		page = [grequests.get(url, headers = self.headers )]
		resp = grequests.map(page)
		soup = bs(resp[0].content, 'html.parser') 

		number = soup.find(class_ = 'offers-index pull-left text-nowrap')
		number = number.find('strong').get_text() 
		number = number.strip().replace(' ','')
		number = int(number)
		
		return number



	def deeper(self, url):

		page = [grequests.get(url, headers = self.headers )]
		print(url)
		resp = grequests.map(page)
		soup = bs(resp[0].content, 'html.parser') 
		
		if Scraper.get_annoucments_number(self, url) <= 12000:
			Scraper.all_pages(self, url)
		
		else:
			deep = soup.find(id = 'locationLinks')
			deep = deep.find_all('a')
			urls = []
			for a in deep:
				urls.append(a.get('href'))
			for u in urls:
				if u == '#':
					continue
				else:
					Scraper.deeper(self, u)


	#return information about the number of last page
	# def get_number_of_pages(self, url):

	# 	page = [grequests.get(url, headers = self.headers )]
	# 	resp = grequests.map(page)
	# 	soup = bs(resp[0].content, 'html.parser')

	# 	mess = soup.find_all(class_ = 'pager')
	# 	for m in mess:
	# 		a_class = m.find_all('a')
	# 		for i, page in enumerate(a_class):
	# 			if i == 4:
	# 				last_page = int(page.get_text())
	# 				return last_page		
	def get_number_of_pages(self, url):

		last = Scraper.get_annoucments_number(self, url)
		last = last/24
		last = math.ceil(last)
		return last
	
	#make "separate" function fo all off the pages. (without first because of different url)
	def all_pages(self, url):

		for i in range(1, Scraper.get_number_of_pages(self,url) + 1):
	
			self.urls.append(url+ '?page=' + str(i+1))

		
		return self.urls


	def make_all_req(self):
		for r in self.resp:
		
			soup = bs(r.content, 'html.parser')
			Scraper.separate(self,soup)


	#print list of dictionary in a more readable way (line by line)
	def display(list):
		for ap in list:
			[print(key, value) for key, value in ap.items()]



#help storage data in json file
class Json_file():

	def save(self, title, data):
		with open(title, 'w', encoding = 'utf-8') as f:
			json.dump(data, f, ensure_ascii = False, indent = 2)

	def load(self, title):
		with open(title, encoding = 'utf-8') as f:
			return json.load(f)



if __name__ == '__main__':

	url2 = 'https://www.otodom.pl/sprzedaz/mieszkanie/'
	headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
	(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

	scraper2 = Scraper(url2, headers)
	j = Json_file()

	j.save("otodom_sale_data", scraper2.apartments_list)