from flask_model import *
import unittest

class TestOpenTableScraping(unittest.TestCase):
    pass

class TestRestaurantClass(unittest.TestCase):
    def test_init(self):
        new = Restaurant('Savas','Casual Dining','Ann Arbor','https://www.opentable.com/savas?page=1','216 State St. Ann Arbor, MI 48109','(734) 623-2233','4.4',42.279683,-83.741184,10)
        self.assertEqual(new.name, 'Savas')
        self.assertEqual(new.food_type, 'Casual Dining')
        self.assertEqual(new.city, 'Ann Arbor')
        self.assertEqual(new.url, 'https://www.opentable.com/savas?page=1')
        self.assertEqual(new.address, '216 State St. Ann Arbor, MI 48109')
        self.assertEqual(new.rating, '4.4')
        self.assertEqual(new.lat,42.279683)
        self.assertEqual(new.lng,-83.741184)
        self.assertEqual(new.distance,10)

    def test_str(self):
        new = Restaurant('Savas','Casual Dining','Ann Arbor','https://www.opentable.com/savas?page=1','216 State St. Ann Arbor, MI 48109','(734) 623-2233','4.4',42.279683,-83.741184,10)
        self.assertEqual(str(new),'Savas - Casual Dining -  Rating: 4.4')

class TestMenuClass(unittest.TestCase):
    def test_init(self):
        new = Menu_Item('Grilled Cheese','$11.00','Sandwhiches','Bread, Butter, and Cheese','Grilled Cheeserie')
        self.assertEqual(new.name, 'Grilled Cheese')
        self.assertEqual(new.price, '$11.00')
        self.assertEqual(new.desc, 'Bread, Butter, and Cheese')
        self.assertEqual(new.type, 'Sandwhiches')
        self.assertEqual(new.restaurant_name, 'Grilled Cheeserie')

    def test_str(self):
        new = Menu_Item('Grilled Cheese','$11.00','Sandwhiches','Bread, Butter, and Cheese','Grilled Cheeserie')
        self.assertEqual(str(new),'Sandwhiches\nGrilled Cheese $11.00\nBread, Butter, and Cheese')

class TestSpoontacularAPI(unittest.TestCase):
    def test_init(self):
        food_name = 'Spinach-Artichoke Dip'
        food_info = get_api_data_using_cache(food_name)
        calories = food_info['calories']['value']
        fat = food_info['fat']['value']
        protein = food_info['protein']['value']
        carbs = food_info['carbs']['value']
        self.assertEqual(fat,12.0)
        self.assertEqual(calories,157.0)
        self.assertEqual(protein,5.0)
        self.assertEqual(carbs,8.0)

class TestGoogleGeocodingAPI(unittest.TestCase):
    def test_get_coordinates(self):
        search_term = '320 E Michigan Ave Lansing, MI 48933'
        response = get_lat_and_long(search_term)
        lat = response[0]
        long = response[1]
        self.assertEqual(lat,42.7333526)
        self.assertEqual(long,-84.5485503)

class TestDistanceGeocoding(unittest.TestCase):
    def test_geocode_inverse(self):
        search_term1 = '320 E Michigan Ave Lansing, MI 48933'
        search_term2 = '2975 Preyde Blvd. Lansing, MI 48912'
        response1 = get_lat_and_long(search_term1)
        response2 = get_lat_and_long(search_term2)
        lat1 = response1[0]
        long1 = response1[1]
        lat2 = response2[0]
        long2 = response2[1]
        d = geod.Inverse(lat1,long1,lat2, long2)
        distance = 0.000621*d['s12']
        distance = round(distance,2)
        self.assertEqual(distance,2.65)

class TestInformationGathering(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
