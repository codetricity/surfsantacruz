"""
Educational program developed with pygame, pgs4a.  Shows tide
and surf forecasts for Santa Cruz.   Runs on 
the desktop and on Android phones.  To install the program
Uses `simple game code`_ for GUI widgets


pulls data from `spitcast`_

forecast by spot_id

- Capitola = 149

- The Hook = 147

- Pleasure Point = 1

- Steamer Lane = 2

- Cowells = 3

.. _simple game code: https://launchpad.net/simplegc
.. _spitcast: http://api.spitcast.com/api/docs/
"""


import sgc
import pygame
import sys
import urllib2
import json
import datetime

try:
    import android
except ImportError:
    android = None

if not android:
    import pprint

def get_date(daydelta=0):
    """
    Input number of days in the future for tide and surf forecast.
    Output the date as a string in this format YYYYMMDD.
    This is the spitcast format for tide and surf predictions.
    """
    date_data = datetime.datetime.now()
    date_data = date_data + datetime.timedelta(days=daydelta)
    month = str(date_data.month)
    if len(month) < 2:
        month = str(0) + month
    day = str(date_data.day)
    if len(day) < 2:
        day = str(0) + day
    date_string = str(date_data.year) + month + day
    return date_string

def get_tide(daydelta=0):
    """
    accept number of days in future from current date.
    returns tide data as a list of dictionaries.  
    each value of the list is an hour of tide forecast data.
    """
    date_string = get_date(daydelta)
    url_string = 'http://api.spitcast.com/api/county/tide/santa-cruz/' + "?dval={}".format(date_string)
    tide_object = urllib2.urlopen(url_string)
    tide_json = tide_object.read() # read in JSON data
    tide_d = json.loads(tide_json) # convert data into list of dictionaries
    return tide_d


def get_surf(spot_id, daydelta = 0):
    """
    Accepts spot_id as an integer value of the specific surfspot
    Accepts days in future to forecast
    Opens connection to spitcast API
    Returns list of dictionary values for the forecast of the specific
    spot.
    """
    date_string = get_date(daydelta)
    url_string = 'http://api.spitcast.com/api/spot/forecast/{}/'.format(spot_id) + "?dval={}".format(date_string)
    surf_object = urllib2.urlopen(url_string)
    surf_json = surf_object.read()
    surf_d = json.loads(surf_json)
    return surf_d


def get_spot(spot_name, daydelta= 0):
    """
    accept name of surf spot in human-readable format.
    for forecast, will accept number of days in the future
    return string that contains the name of the spot
    """
    spots = {"capitola":"149", "the_hook": "147",
             "pleasure_point":"1",
             "cowells": "3", "steamer_lane": "2"}
    spot_id = spots[spot_name]
    spot_data= get_surf(spot_id, daydelta)
    spot_noon = spot_data[12]
    break_name = spot_noon["spot_name"]
    spot_basic = "{}: {} ft, {}".format(break_name, spot_noon["size"], spot_noon["shape_full"])
    return spot_basic

class Graph():
    def get_title(self, tide_data):
        self.title = tide_data[0]["name"] + " - " + tide_data[0]["date"]

    def update(self, tide_data):
        self.point_list = []
        self.x = 20
        self.x_axis_grid = []
        self.hour_list =[]
        self.get_title(tide_data)

        for t in range(1, 25):
            height = tide_data[t]["tide"]
            height_pixel = int(550 - height * 50)
            y = height_pixel
            self.point_list.append((self.x,y))
            self.x_axis_grid.append(self.x)
            self.x = self.x +30
            self.hour_list.append(tide_data[t]["hour"])

def forecast_surf(surfspots, days_forecast):
    WHITE = (0, 0, 0)
    main_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 20)
    y = 50
    label_list =[]
    for surfspot in surfspots:
        spot_text = get_spot(surfspot, days_forecast)
        spot_label = sgc.Label(pos = (10, y),
                               text = spot_text,
                               font = main_font,
                               Label_col = WHITE)
        y += 30
        label_list.append(spot_label)
    return label_list

def draw_tide_graph(screensize, graph):
    counter = 0
    display_time = True
    main_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 20)
    WHITE = (255, 255, 255)
    BLUE = (100, 100, 220)
    RED = (200, 100, 100)
    YELLOW = (241, 248, 27)
    LIGHTBLUE = (174, 236, 255)
    big_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 36)
    graph_surface = pygame.Surface((screensize))

    for x in graph.x_axis_grid:
        hour_surface = main_font.render(graph.hour_list[counter], True, WHITE)
        if display_time:
            pygame.draw.line(graph_surface, BLUE, (x, 250), (x, 550))
            graph_surface.blit(hour_surface, (x -15, 570))
            display_time = False
        else:
            display_time = True
        counter +=1

    for y in range (50, 400, 50):
        y_axis_color = RED
        height = ((600-(y*2))/100) + 1
        if height == 3:
            y_axis_color = YELLOW
        height_text = str(height)
        height_surface = main_font.render(height_text + " ft", True, WHITE)
        graph_surface.blit(height_surface, (750, y+200))
        pygame.draw.line(graph_surface, y_axis_color, (10, y+200), (700, y+200))
    title_surface_1 = big_font.render(graph.title, True, LIGHTBLUE)    
    graph_surface.blit(title_surface_1, (10, 10))
    pygame.draw.lines(graph_surface, WHITE, False, graph.point_list, 3)
    return graph_surface

class Forecast():

    def __init__(self, surfspots):
        self.WHITE = (0,0,0)
        self.med_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 32)
        # adds buttons using the sgc gui toolkit
        self.change_day_btn = DayButton(pos=(650,3), label = "Day +1",
                                    label_font = self.med_font, label_col = self.WHITE)

        self.reset_day_btn = DayButton(pos = (650, 80), label = "Today",
                                  label_font = self.med_font, label_col = self.WHITE )

        self.days = 0
        self.surfspots = surfspots
        self.f_list = forecast_surf(self.surfspots, self.days)



def update_days(forecast):
    if forecast.change_day_btn.clicked:
        forecast.days += 1
        forecast.change_day_btn.clicked = False
    if forecast.reset_day_btn.clicked:
        forecast.days = 0
        forecast.reset_day_btn.clicked = False
    spot_index = 0
    for f_label in forecast.f_list:
        spot_text = get_spot(forecast.surfspots[spot_index], forecast.days)
        f_label.text = spot_text
        spot_index += 1
    return forecast

class Weather():
    def __init__(self):
        weather_obj = urllib2.urlopen("http://api.openweathermap.org/data/2.5/weather?q=santa%20cruz,%20us&units=imperial")
        weather_json = weather_obj.read()
        self.w_dict = json.loads(weather_json)
        sunrise_datestamp = self.w_dict["sys"]["sunrise"]
        sunrise = datetime.datetime.fromtimestamp(int(sunrise_datestamp))
        self.sunrise = sunrise.strftime('%H:%M')
        sunset_stamp = self.w_dict["sys"]["sunset"]
        sunset = datetime.datetime.fromtimestamp(int(sunset_stamp))
        self.sunset = sunset.strftime('%H:%M')
        self.temp_min = str(int(self.w_dict["main"]["temp_min"]))
        self.temp_max = str(int(self.w_dict["main"]["temp_max"]))
        self.description = self.w_dict["weather"][0]["description"]
        self.windspeed = self.w_dict["wind"]["speed"]
        self.show()


    def show(self):
        WHITE = (0, 0, 0)
        main_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 20)
        weather_text = "Sunrise: {}\nSunset: {}".format(self.sunrise, self.sunset)
        self.weather_label = sgc.Label(pos = (10, 140),
                               text = weather_text,
                               font = main_font,
                               Label_col = WHITE)
        self.weather_label.add()
        temp_text = "Coldest Air Temp: {}F\n".format(self.temp_min) +\
            "Warmest Air Temp: {}F".format(self.temp_max)


        self.temp_label = sgc.Label(pos=(190, 140),
                                    text= temp_text,
                                    font = main_font,
                                    Label_col = WHITE)
        self.temp_label.add()

        desc_text = self.description + "\nWind: {}".format(str(self.windspeed))
        self.desc_label = sgc.Label(pos=(450, 140),
                                    text = desc_text,
                                    font = main_font,
                                    Label_col = WHITE)
        self.desc_label.add()

    def forecast(self):
        url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=santa%20cruz,%20ca&mode=json&units=imperial&cnt=7"
        try:
            weath_cast_obj = urllib2.urlopen((url))
        except URLError, e:
            print e.reason
        weath_cast_json = weath_cast_obj.read()
        self.weath_cast = json.loads(weath_cast_json)

class DayButton(sgc.Button):
    clicked = False

    def on_click(self):
        self.clicked = True

pygame.init()
if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

def main():
    SURFSPOTS=("capitola", "pleasure_point", "the_hook")
    clock = pygame.time.Clock()
    SCREENSIZE = (800, 600)
    SCREEN = pygame.display.set_mode(SCREENSIZE)
    sgc.surface.Screen(SCREENSIZE) # needed for SGC GUI toolkit
    fonts = {"widget": "fnt/Ubuntu-M.ttf", "title": "fnt/Ubuntu-M.ttf",
             "mono": "fnt/Ubuntu-M.ttf"}
    sgc.Font.set_fonts(fonts)

    forecast = Forecast(SURFSPOTS)
    graph = Graph()

    for fcast in forecast.f_list:
        fcast.add()
    forecast.change_day_btn.add()
    forecast.reset_day_btn.add()
    tide_data = get_tide()
    graph.update(tide_data)

    # get weather from Open Weather Map
    weather = Weather()
    weather.forecast()
   # pprint.pprint(weather.weath_cast)
    pprint.pprint(weather.w_dict)

    while True:
        if android:
            if android.check_pause():
                android.wait_for_resume()
        time = clock.tick(30)

        for event in pygame.event.get():
            sgc.event(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN 
                                             and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        if forecast.change_day_btn.clicked or forecast.reset_day_btn.clicked:
            forecast = update_days(forecast)
            tide_data = get_tide(forecast.days)
            graph.update(tide_data)

        graph_surface = draw_tide_graph(SCREENSIZE, graph)
        SCREEN.fill((0,0,0))
        SCREEN.blit(graph_surface, (0,0))
        sgc.update(time)
        pygame.display.update()

if __name__ == "__main__":
    main()
