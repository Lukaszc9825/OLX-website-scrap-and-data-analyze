import requests
from bs4 import BeautifulSoup as bs

url = 'https://www.olx.pl/elektronika/'

headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

page = requests.get(url, headers=headers)

# Convert to bs object
soup = bs(page.content, 'html.parser')

# Contains all informations about product
product_info = {}
products_list = []

# Separate the products from each other 
def separate(soupy):
	# Save all off the products into a list
	products = soupy.find_all(class_ = 'offer-wrapper')
	
	for product in products:
		
		# Separate single informations about product
		info = product.find_all('td')
		for i, data in enumerate(info):
			#print(data.prettify())
			if i == 0:
				for temp in data.find_all('a'):
					product_info['auction link'] = temp.get('href')
				for temp in data.find_all('img'):
					product_info['photo link'] = temp.get('src')
			
			elif i == 1:
				product_info['auction name'] = data.find('strong').get_text()
				product_info['category'] = data.find('small').get_text().strip()

			elif i == 2:
				product_info['price'] = data.find('strong').get_text()

			elif i ==3:
				for j, x in enumerate(data.find_all('span')):
					if j == 0:
						product_info['location'] = x.get_text()
					else:
						product_info['add time'] = x.get_text()
				
		products_list.append(product_info.copy())			
	return products_list

def get_number_of_pages():
	mess = soup.find_all(class_ = 'block br3 brc8 large tdnone lheight24')
	for index, number in enumerate(mess):
		if index == 12:
			last = number.get_text().strip()
	return int(last)		

def all_pages():
	for i in range(1, get_number_of_pages()):
		url2 = 'https://www.olx.pl/elektronika/?page=' + str(i+1)
		page2 = requests.get(url2, headers=headers)
		soup2 = bs(page2.content, 'html.parser')
		separate(soup2)	

separate(soup)
all_pages()
print(len(products_list))