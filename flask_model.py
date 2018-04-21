import requests
import datetime
import json
from bs4 import BeautifulSoup
import re
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
from flask import Flask, render_template, request
from geographiclib.geodesic import Geodesic
import math
geod = Geodesic.WGS84

# Set up cache for Open Table Scarping, Spoontacular API, and Google Maps API
CACHE_FNAME = 'cache_data.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICT = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICT = {}

CACHE_FNAME2 = 'cache_data2.json'
try:
    cache_file = open(CACHE_FNAME2, 'r')
    cache_contents = cache_file.read()
    CACHE_DICT2 = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICT2 = {}

CACHE_FNAME3 = 'cache_data3.json'
try:
    cache_file = open(CACHE_FNAME3, 'r')
    cache_contents = cache_file.read()
    CACHE_DICT3 = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICT3 = {}

#cache function for Google Geocoding API
def get_lat_long_using_cache(url):
    unique_ident = url
    if unique_ident in CACHE_DICT3:
        return CACHE_DICT3[unique_ident]
    else:
        response = requests.get(url)
        CACHE_DICT3[unique_ident] = json.loads(response.text)
        fref = open('cache_data3.json','w')
        dumped_data = json.dumps(CACHE_DICT3)
        fref.write(dumped_data)
        fref.close()
        return CACHE_DICT3[unique_ident]

# Function to grab lat and long from Google Geocoding API
def get_lat_and_long(search_term):
    search_term = search_term.split()
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    count = 1
    total = len(search_term)
    for x in search_term:
        url += x
        if count != total:
            url += '+'
            count += 1
    google_api_key = secrets.google_api_key
    url += '&key=' + google_api_key
    response_text = get_lat_long_using_cache(url)
    response_list = response_text['results'][0]['geometry']['location']
    real_response_list = [response_list['lat'],response_list['lng']]
    return(real_response_list)

# Cache function for Spoontacular API
def get_api_data_using_cache(menu_item):
    unique_ident = menu_item
    if unique_ident in CACHE_DICT2:
        print('Getting cached spoontacular data...')
        return CACHE_DICT2[unique_ident]
    else:
        print('Getting new spoontacular data...')
        menu_item = menu_item.split()
        baseurl = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/guessNutrition?title='
        total = len(menu_item)
        count = 1
        extension = ''
        for x in menu_item:
            if count != total:
                extension += menu_item[count-1] + '+'
                count += 1
            else:
                extension += menu_item[count-1]
                count += 1
        extended_url = baseurl + extension
        response = requests.get(extended_url,
          headers={
            "X-Mashape-Key": secrets.spoontacular_key
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com"
          }
        )
        CACHE_DICT2[unique_ident] = json.loads(response.text)
        dumped_data = json.dumps(CACHE_DICT2)
        fref = open('cache_data2.json','w')
        fref.write(dumped_data)
        fref.close()
        return CACHE_DICT2[unique_ident]


# Cache function for getting to data to scrape from OpenTable
def get_opentable_data_using_cache(url,num_guests):
    unique_ident = url + str(num_guests)
    if unique_ident in CACHE_DICT:
        print('Retrieving cached data...')
        return CACHE_DICT[unique_ident]
    else:
        print('Collecting new data')
        headers = {'Accept':'text/html,application/xhtml+xml,applißcation/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-GB,en-US;q=0.8,en;q=0.6',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        resp = requests.get(url,headers=headers)
        CACHE_DICT[unique_ident] = resp.text
        fref = open('cache_data.json','w')
        dumped_data = json.dumps(CACHE_DICT)
        fref.write(dumped_data)
        fref.close()
        return CACHE_DICT[unique_ident]

# Create valid web_url to scrape from OpenTable website
# Used in OpenTable cache function
def create_opentable_web_url(search_term,num_guests):
    date_list = get_date_time()
    year = date_list[0]
    month = date_list[1]
    day = date_list[2]
    search_term = search_term.split()
    length = len(search_term)
    return_string = 'https://www.opentable.com/s/restaurantlist?currentview=list&size=10&sort=Popularity&covers=' + str(num_guests) + '&&dateTime=' + str(year) + '-' + str(month) + '-' + str(day) + '+19%3A00&term='
    count = 1
    for x in search_term:
        return_string += x
        if count != length:
            return_string += '+'
            count += 1
    return return_string

# Restaurant class to temporarily set up restaurant data
class Restaurant:
    def __init__(self, name,food_type,city,url,address,phone_number,rating,lat,lng,distance):
        self.name = name
        self.food_type = food_type
        self.city = city
        self.url = url
        self.address = address
        self.phone_number = phone_number
        self.rating = rating
        self.lat = lat
        self.lng = lng
        self.distance = distance


    def __str__(self):
        return_string = self.name + ' - ' + self.food_type + ' - ' + ' Rating: ' + self.rating
        return return_string

# Menu Item class to emporaryily holding to setup menu items ,
class Menu_Item:

    def __init__(self,name,price,type,desc,restaurant_name):
        self.name = name
        self.price = price
        self.desc = desc
        self.type = type
        self.restaurant_name = restaurant_name

    def __str__(self):
        return_string =  self.type + '\n' + str(self.name) + ' ' + str(self.price) + '\n' + str(self.desc)
        return return_string

# Get relevant restaurant info by scraping OpenTable site
def get_opentable_restaurant_info(search_term,num_guests,user_location):
    special_url = create_opentable_web_url(search_term,num_guests)
    opentable_html = get_opentable_data_using_cache(special_url,num_guests)
    opentable_soup = BeautifulSoup(opentable_html, "html.parser")
    restaurant_list = []
    if opentable_soup.find_all('div', {'class' : 'no-result-message'}):
        restaurant_list = ['No Results']
        return restaurant_list
    if opentable_soup.find_all('div',{'class': 'error-content'}):
        restaurant_list = ['Invalid Entry']
        return restaurant_list
    data_list = opentable_soup.find('div', {'class' : 'content-section-list infinite-results-list analytics-results-list'}).find_all('div', {'class': 'result content-section-list-row cf with-times'})
    for item in data_list:
        name = item.find('span', {'class': 'rest-row-name-text'}).text.strip()
        food_type = item.find('span', {'class': 'rest-row-meta--cuisine rest-row-meta-text'}).text.strip()
        city = item.find('span', {'class': 'rest-row-meta--location rest-row-meta-text'}).text.strip()
        url =  'https://www.opentable.com' + item.find('div', {'class': 'rest-row-header'}).find('a').get('href')
        headers = {'Accept':'text/html,application/xhtml+xml,applißcation/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-GB,en-US;q=0.8,en;q=0.6',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        resp = requests.get(url,headers=headers).text
        restaurant_soup = BeautifulSoup(resp, "html.parser")
        user_lat_lng = get_lat_and_long(user_location)
        user_lat = user_lat_lng[0]
        user_lng = user_lat_lng[1]
        try:
            restaurant_address = restaurant_soup.find('span', {'itemprop': 'streetAddress'}).text.strip()
            try:
                lat_lng = get_lat_and_long(restaurant_address)
                restaurant_lat = lat_lng[0]
                restaurant_lng = lat_lng[1]
            except:
                restaurant_lat = None
                restaurant_lng = None
        except:
            restaurant_address = 'No Address Listed'
            restaurant_lat = None
            restaurant_lng = None
        try:
            restaurant_rating = restaurant_soup.find('div', {'class': '_491257d8'}).text.strip()
        except:
            restaurant_rating = 'No rating available'
        try:
            div_list = restaurant_soup.find_all('div', {'class': '_9c5985ce'})
            for div in div_list:
                if div.find(text=re.compile("Phone Number")):
                    phone_number = div.find('div', {'class': 'b4b277db _9ff93041'}).text.strip()
                    count = 1
            if count != 1:
                phone_number = 'No phone number available'
        except:
            phone_number = 'No phone number available'
        d = geod.Inverse(restaurant_lat, restaurant_lng, user_lat,user_lng)
        distance = 0.000621*d['s12']
        distance = round(distance,2)
        temp = Restaurant(name,food_type,city,url,restaurant_address,phone_number,restaurant_rating,restaurant_lat,restaurant_lng,distance)
        restaurant_list.append(temp)
    restaurant_list = restaurant_list[:10]
    return restaurant_list

# Set up information and data for menu items from a restaurant's OpenTable site
def scrape_menu(url_list):
    headers = {'Accept':'text/html,application/xhtml+xml,applißcation/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-GB,en-US;q=0.8,en;q=0.6',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    menu_item_list = []
    for x in url_list:
        resp = requests.get(str(x),headers=headers).text
        opentable_soup = BeautifulSoup(resp, "html.parser")
        try:
            restaurant_name = opentable_soup.find('h1', {'class': 'dffa9ef4 _66a2d72e'}).text.strip()
            first_menu = opentable_soup.find('div', {'id': 'menu-1'})
            menu_sections = first_menu.find_all('div', {'class': 'menuSection'})
            for x in menu_sections:
                section_name = x.find('div', {'class': 'menuSectionHeader'}).find('h3').text.strip()
                menu_items = x.find_all('div', {'class': 'menu-items'})
                for y in menu_items:
                    for z in y.find_all('div', {'class': 'menu-item'}):
                        menu_item_title = z.find('div', {'class': 'menu-item-title'}).text.strip()
                        try:
                            menu_item_description = z.find('p', {'class': 'menu-item-desc'}).text.strip()
                        except:
                            menu_item_description = 'No description available'
                        try:
                            menu_item_price = z.find('div', {'class': 'menu-item-price'}).text.strip()
                        except:
                            menu_item_price = 'No price available'
                        temp = Menu_Item(menu_item_title,menu_item_price,section_name,menu_item_description,restaurant_name)
                        menu_item_list.append(temp)

        except:
            continue
    return menu_item_list

# Master function to set up all of the data needed for program
def set_up_data(search_term,num_guests,user_location):
    # Set up DBLite Databasese access
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # Drop tables if they already exist
    statement = '''
        DROP TABLE IF EXISTS 'Restaurants';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Menu';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Spoontacular';
    '''
    cur.execute(statement)
    conn.commit()

    # Set up restaurant table
    statement = '''
        CREATE TABLE "Restaurants" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Name" TEXT,
            "City" TEXT,
            "Type" TEXT,
            "URL" TEXT,
            "Address" TEXT,
            "Phone Number" TEXT,
            "Rating" TEXT,
            "Lat" INT,
            "Lng" INT,
            "Distance" INT
            );
        '''
    cur.execute(statement)

    # Set up menu table, ensure it has a restaurant_name that is in Restaurants as foreign key
    statement = '''
        CREATE TABLE 'Menu' (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Item Name TEXT,
            Price TEXT,
            Type TEXT,
            Description TEXT,
            RestaurantName TEXT,
            FOREIGN KEY(RestaurantName) REFERENCES Restaurants(Name)
        );
        '''
    cur.execute(statement)
    conn.commit()

    # Get restaurant info for area
    restaurant_list = get_opentable_restaurant_info(search_term,num_guests,user_location)

    # Insert restaurant info into Restaurants table
    for restaurant in restaurant_list:
        insertion = (restaurant.name,restaurant.city,restaurant.food_type,restaurant.url,restaurant.address,restaurant.phone_number,restaurant.rating,restaurant.lat,restaurant.lng,restaurant.distance)
        statement = 'INSERT INTO Restaurants '
        statement += 'VALUES (NULL,?,?,?,?,?,?,?,?,?,?)'
        cur.execute(statement, insertion)
        conn.commit()

    # Gather urls for menu scraping
    statement = '''
        SELECT url
        FROM Restaurants
        '''
    cur.execute(statement)
    # Get urls into workable data form (list)
    url_list = []
    for x in cur:
        url_list.append(x[0])

    # Gather menu data for each Restaurant in 'Restaurants' table
    menu_items = scrape_menu(url_list)

    # Insert menu data into 'Menu' table
    for item in menu_items:
        insertion = (item.name,item.price,item.type,item.desc,item.restaurant_name)
        statement = 'INSERT INTO Menu '
        statement += 'VALUES (NULL,?,?,?,?,?)'
        cur.execute(statement,insertion)
    conn.commit()

# The following functions are all used in flak_model.py to gather required information when needed

# Gather restaurant information from DB
def get_restaurant_data():
    statement = '''
        SELECT *
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    result_list = []
    for row in cur:
        string = ' ' + row[1] + ' || Style: ' + row[3] + ' || Rating: ' + row[7]
        result_list.append(string)
    return result_list

# Gather lattitude data from database
def get_lat_data():
    statement = '''
        SELECT Lat
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    lat_list = []
    for x in cur:
        lat_list.append(x[0])
    return lat_list

# Gather longitude data from database
def get_lng_data():
    statement = '''
        SELECT Lng
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    lng_list = []
    for x in cur:
        lng_list.append(x[0])
    return lng_list

# Gather restaurant names from database
def get_name_data():
    statement = '''
        SELECT Name
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    name_list = []
    for x in cur:
        name_list.append(x[0])
    return name_list

# Gather rating data from database
def get_ratings_data():
    statement = '''
        SELECT Rating
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    rating_list = []
    for x in cur:
        rating_list.append(x[0])
    return rating_list

# Gather distance data from database
def get_distance_data():
    statement = '''
        SELECT Distance
        FROM Restaurants
        '''
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    distance_list = []
    for x in cur:
        distance_list.append(x[0])
    return distance_list

# Gather menu items from database
def get_menu_data(restaurant_name):
    statement = 'SELECT Item, Price, m.Type, Description '
    statement += 'FROM Restaurants as r '
    statement += 'JOIN Menu as m '
    statement += 'ON m.RestaurantName = r.Name '
    statement += 'WHERE m.RestaurantName = ' + '"' + restaurant_name + '"'
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    menu_list = []
    for x in cur:
        string = x[2] + ' ||| ' + x[0] + ' ||| ' + x[1] + ' ||| ' + x[3]
        menu_list.append(string)
    return menu_list

# Gather additional restaurant data from database
def get_advanced_restaurant_data(id):
    statement = 'SELECT Name, Type, Address, Rating, url '
    statement += 'FROM Restaurants '
    statement += 'WHERE Id = ' + str(id)
    DBNAME = 'restaurants.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(statement)
    info_list = []
    x = 0
    for row in cur:
        while x < 5:
            info_list.append(row[x])
            x += 1
    return info_list

# Get relevant food info from Spoontacular API
def get_food_info(food_name):
    food_info = get_api_data_using_cache(food_name)
    d = {}
    try:
        d[food_name] = {'calories': food_info['calories']['value'],'fat': food_info['fat']['value'],'protein': food_info['protein']['value'],'carbs': food_info['carbs']['value']}
        return d
    except:
        return 'No data'

# Grab date/time information from date_time module
def get_date_time():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return_list = [year,month,day]
    return(return_list)
