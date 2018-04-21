# SI206_Final
Final Project for SI206: A Bite Out on the Town

A Bite Out on the Town is an interactive Flask app where users can search restaurants in a given area, see how far away they are, get information 
about the restaurants, and finally get nutritional information about menu items at the restaurant. 

Data sources for this project are...
1. The Google Geocoding API. This can be used without a key but is better to use with a key which you can access via https://developers.google.com/maps/documentation/geocoding/get-api-key and should be referenced as google_api_key within secrets.py
2. The Spoontacular API. This can be accessed at the following website https://spoonacular.com/food-api and should be referenced as spoontacular_key in the secrets file.
3. OpenTable web scraping, which you need nothing for to run the program.

The code is structured in a MVC format with flask_app.py being the controller, flask_model.py being the model which controls all the data and the connection to restaurants.db, and tempaltes being the views.
The database contains two tables: Restaurants and Menu. They are connected by a foreign key which is the restaurant name a menu item cannot be added to the databases unless it has a corresponding retaurant name in the Restaurant table.
The biggest function in the file is set_up_data which sets up all of the information for the user after the user provides a target location, current location, and party size. The function will then grab all the restaurant and menu item information by scraping OpenTable.
Another important function is get_api_data_using_cache which gets the nutrition information for a men item. 
There are 3 caches, one for the Google API, one for the Spoontacular PI, and one for the OpenTable html content.
The two classes included in the project are Restaurant and Menu_Item. Restaurant is a class to hold the information for each restaurant and Menu_Item, logically, contains each meny item information.

User Guide:
1. Run python3 flask_app.py in the terminal to trigger the app
2. Navigate to the local server URL
3. Enter information into the three fields on the welcome page and hit submit.
4. On the next page, enter in the number of the restaurant that you would like to receive more information about.
5. On the next page, either enter in the menu item that you would like nutrition on go back in your browser to get back to the restaurant list and go back to step 3 of the user guide.
6. On the nutrition page, view the nutrition info for the menu item and hit the back button on your browser after you are finished.
