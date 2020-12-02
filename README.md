# Analysis of real estate in Poland

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This project scrapes data from the Otodom.pl website (about 170,000 ads). Then the data is cleaned and completed. All this is displayed on the website (currently only on locallhost) as a map and graph. You can view data of real estate for sale or for rent.
![](images/screen1.png)

## Technologies
Project is created with:
* Python: 3.8.5
* pandas: 1.1.3
* dash: 1.17.0
* plotly: 4.12.0
* grequests: 0.6.0
* beautifulsoup4: 4.9.3
	
## Setup
To run this project install requirements:

```
$ pip install -r requirements.txt
```
If you want to run page on your locallhost

```
$ python3 Dash_plot.py 
```
If you want to scrap fresh data and preapare it to analysis (it takes about 3h, I will speed up the process soon)

```
$ python3 Otodom_fulldata.py
```
