from flask import Flask, render_template, request, redirect, url_for
import plotly
from plotly.graph_objs import *
import plotly.graph_objs as go
import flask_model
from markupsafe import Markup, escape

mapbox_access_token = 'pk.eyJ1IjoiemFtaWFyYWIiLCJhIjoiY2pnNXgwMzUwMnA2czJ3cXBqYng1bXgwciJ9.kEizefcCiWp2nREawPnvjA'
app = Flask(__name__)
menu_info = []

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/restaurant_map', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        global location
        global party_size
        location = request.form['location']
        party_size = request.form['party_size']
        user_location = request.form['user_location']
        flask_model.set_up_data(location,party_size,user_location)
        lat_list = flask_model.get_lat_data()
        lng_list = flask_model.get_lng_data()
        global name_list
        name_list = flask_model.get_name_data()
        rating_list = flask_model.get_ratings_data()
        real_name_list = []
        count = 0
        for x in name_list:
            real_name_list.append(x + ' | Rating: ' + rating_list[count])
            count += 1
        data = Data([
        Scattermapbox(
            lat=lat_list,
            lon=lng_list,
            mode='markers',
            marker=Marker(
                size=12
            ),
            text=real_name_list,
            hoverinfo = 'text'
        )
        ])
        layout = Layout(
            title='Top 10 restaurants in this area!',
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=lat_list[0],
                    lon=lng_list[0]
                ),
                pitch=0,
                zoom=10
            ),
        )
        fig = go.Figure(data=data, layout=layout)
        my_plot_div1 = plotly.offline.plot(fig,output_type="div")
        distances = flask_model.get_distance_data()
        names = flask_model.get_name_data()
        data = [go.Bar(
                x=names,
                y=distances,
                text=distances,
                textposition = 'auto',
                marker=dict(
                    color='rgb(158,202,225)',
                    line=dict(
                        color='rgb(8,48,107)',
                        width=1.5),
                ),
                opacity=0.6
            )]
        layout = go.Layout(
            title = 'Distances (in miles) From Your Location'
            )
        fig2 = go.Figure(data=data, layout=layout)
        my_plot_div2 = plotly.offline.plot(fig2,output_type="div")
        return render_template('display_graph.html',map_placeholder1 = Markup(my_plot_div1),map_placeholder2 = Markup(my_plot_div2),result_list=flask_model.get_restaurant_data())
    elif request.method == "GET":
        return redirect('/')

@app.route('/restaurant_info',methods = ['GET','POST'])
def get_restaurant_info():
    restaurant_id = request.form['restaurant_id']
    restaurant_info = flask_model.get_advanced_restaurant_data(restaurant_id)
    restaurant_name = restaurant_info[0]
    restaurant_type = restaurant_info[1]
    restaurant_address = restaurant_info[2]
    restaurant_rating = restaurant_info[3]
    restaurant_website = restaurant_info[4]
    global menu_info
    menu_info = flask_model.get_menu_data(restaurant_name)
    #return_string += 'restaurant_address = restaurant_address,restaurant_rating = restaurant_rating,'
    #return_string += 'restauraunt_website = restaurant_website,menu_info=menu_info)'
    return render_template('menu_display.html',restaurant_name = restaurant_name,restaurant_type = restaurant_type,restaurant_rating = restaurant_rating,restaurant_address = restaurant_address,restauraunt_website = restaurant_website,menu_info=menu_info)

@app.route('/food_info',methods = ['GET','POST'])
def get_food_info():
    food_id = request.form['food_id']
    global menu_info
    menu_item = menu_info[int(food_id) - 1]
    menu_item_string_list = menu_item.split(" ||| ")
    menu_item = menu_item_string_list[1]
    food_info = flask_model.get_food_info(menu_item)
    if food_info == 'No data':
        return render_template('error.html')
    else:
        fat_level = food_info[menu_item]['fat']
        carb_level = food_info[menu_item]['carbs']
        protein_level = food_info[menu_item]['protein']
        calorie_level = food_info[menu_item]['calories']
        value_list = [fat_level,protein_level,carb_level,calorie_level]
        text_list = [str(fat_level) + ' g',str(protein_level) + ' g',str(carb_level) + ' g',str(calorie_level) + ' cal']
        trace0 = go.Bar(
            x=['Fat', 'Protein', 'Carbs','Calories'],
            y=value_list,
            text=text_list,
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5,
                )
            ),
            opacity=0.6
        )

        data = [trace0]
        layout = go.Layout(
            title='Nutritional info for '+ menu_item,
        )
        fig = go.Figure(data=data, layout=layout)
        my_plot_div = plotly.offline.plot(fig,output_type="div")
        return render_template('food_display.html',menu_item = menu_item,my_plot_div = Markup(my_plot_div))


@app.route('/distance_rating')
def show_distance():
    distances = flask_model.get_distance_data()
    names = flask_model.get_name_data()
    data = [go.Bar(
            x=names,
            y=distances,
            text=distances,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]
    layout = go.Layout(
        title = 'Distances (in miles) From Your Location'
        )
    fig2 = go.Figure(data=data, layout=layout)
    my_plot_div2 = plotly.offline.plot(fig2,output_type="div")
    return render_template('distance.html',my_plot_div = Markup(my_plot_div))

if __name__ == '__main__':
    app.run(debug=True)
