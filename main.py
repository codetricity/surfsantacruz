import sgc
from sgc.locals import *
import pygame
import sys
import urllib2
import json
import datetime

# uses simple game code for GUI widgets
# https://launchpad.net/simplegc

# pulls data from spitcast
# http://api.spitcast.com/api/docs/
# forecast by spot_id
# Capitola = 149
# The Hook = 147
# Pleasure Point = 1
# Cowells = 3
# Steamer Lane = 2

try:
    import android
except ImportError:
    android = None

def get_date(daydelta=0):
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
    date_string = get_date(daydelta)
 #   print(date_string)
    url_string = 'http://api.spitcast.com/api/county/tide/santa-cruz/' + "?dval={}".format(date_string)
    tide_object = urllib2.urlopen(url_string)
    tide_json = tide_object.read()
    tide_d = json.loads(tide_json)
    return tide_d


def get_surf(spot_id, daydelta = 0):
    date_data = datetime.datetime.now()
    date_data = date_data + datetime.timedelta(days=daydelta)
    month = str(date_data.month)
    if len(month) < 2:
        month = str(0) + month
    day = str(date_data.day)
    if len(day) < 2:
        day = str(0) + day

    date_string = str(date_data.year) + month + day
    print(date_string)
    url_string = 'http://api.spitcast.com/api/spot/forecast/{}/'.format(spot_id) + "?dval={}".format(date_string)
    #url_string = 'http://api.spitcast.com/api/spot/forecast/149/'
    surf_object = urllib2.urlopen(url_string)
    surf_json = surf_object.read()
    surf_d = json.loads(surf_json)
    return surf_d


def get_spot(spot_name, daydelta= 0):

    spots = {"capitola":"149", "the_hook": "147",
             "pleasure_point":"1",
             "cowells": "3", "steamer_lane": "2"}
    spot_id = spots[spot_name]
    print(spot_name, spot_id)
   # spot_data= get_surf(spot_id, daydelta)
    spot_data= get_surf(spot_id, daydelta)
    spot_noon = spot_data[12]
    break_name = spot_noon["spot_name"]
   # print (capitola_noon)
    spot_basic = "{}: {} ft, {}".format(break_name, spot_noon["size"], spot_noon["shape_full"])
    print (spot_basic)
    return spot_basic



def get_graph(tide_data):
    point_list = []
    x = 20
    big_font = pygame.font.SysFont(None, 50)

    x_axis_grid = []
    hour_list =[]

    title_text_1 = tide_data[0]["name"] + " - " + tide_data[0]["date"]
    title_surface_1 = big_font.render(title_text_1, True, WHITE)

    for t in range(1, 25):
        height = tide_data[t]["tide"]
        height_pixel = int(550 - height * 50)
        y = height_pixel
        point_list.append((x,y))
        x_axis_grid.append(x)
        x = x +30
        hour_list.append(tide_data[t]["hour"])

    return point_list, x_axis_grid, hour_list, title_surface_1

class DayButton(sgc.Button):
    clicked = False

    def on_click(self):
        self.clicked = True


pygame.init()

if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE = (100, 100, 220)
RED = (200, 100, 100)
YELLOW = (241, 248, 27)

SCREENSIZE = (800, 600)
SCREEN = pygame.display.set_mode(SCREENSIZE)
GUI_SCREEN = sgc.surface.Screen(SCREENSIZE)
main_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 20)
med_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 32)
big_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 50)

fonts = {"widget": "fnt/Ubuntu-M.ttf", "title": "fnt/Ubuntu-M.ttf",
         "mono": "fnt/Ubuntu-M.ttf"}
sgc.Font.set_fonts(fonts)

#spots = {"capitola":149, "the_hook": 147, "pleasure_point": 1,
#         "cowells": 3, "steamer_lane": 2}

# adds buttons using the sgc gui toolkit
change_day_btn = DayButton(pos=(650,3), label = "Day +1",
                            label_font = med_font, label_col = WHITE)

reset_day_btn = DayButton(pos = (650, 80), label = "Today",
                          label_font = med_font, label_col = WHITE )


capitola_basic = get_spot("capitola")
capitola = sgc.Label(pos = (10, 50),
                         text = capitola_basic,
                         font = main_font,
                         label_col = WHITE)

pleasure_point_basic = get_spot("pleasure_point")
pleasure_point = sgc.Label(pos = (10, 80),
                           text = pleasure_point_basic,
                           font = main_font,
                           label_col = WHITE)

the_hook = sgc.Label(pos = (10, 110),
                           text = get_spot("the_hook"),
                           font = main_font,
                           label_col = WHITE)


change_day_btn.add(0)
reset_day_btn.add(1)
capitola.add(1)
the_hook.add(3)
pleasure_point.add(4)


days_forecast = 0
tide_data = get_tide()
point_list, x_axis_grid, hour_list, title_surface_1 = get_graph(tide_data)


while True:

    if android:
        if android.check_pause():
            android.wait_for_resume()
    time = clock.tick(30)

    for event in pygame.event.get():
        sgc.event(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()


    if change_day_btn.clicked:
        days_forecast += 1
        tide_data = get_tide(days_forecast)
        capitola.text = get_spot("capitola", days_forecast)
        the_hook.text = get_spot("the_hook", days_forecast)
        pleasure_point.text = get_spot("pleasure_point", days_forecast)
        point_list, x_axis_grid, hour_list, title_surface_1 = \
            get_graph(tide_data)
        SCREEN.fill((0,0,0))
        change_day_btn.clicked = False

    if reset_day_btn.clicked:
        days_forecast = 0
        capitola.text = get_spot("capitola", days_forecast)
        the_hook.text = get_spot("the_hook", days_forecast)
        pleasure_point.text = get_spot("pleasure_point", days_forecast)

        tide_data = get_tide(days_forecast)
        point_list, x_axis_grid, hour_list, title_surface_1 = \
            get_graph(tide_data)
        SCREEN.fill((0,0,0))
        reset_day_btn.clicked = False

    counter = 0
    display_time = True
    for x in x_axis_grid:

        hour_surface = main_font.render(hour_list[counter], True, WHITE)
        if display_time:
            pygame.draw.line(SCREEN, BLUE, (x, 250), (x, 550))
            SCREEN.blit(hour_surface, (x -15, 570))
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
        SCREEN.blit(height_surface, (750, y+200))
        pygame.draw.line(SCREEN, y_axis_color, (10, y+200), (700, y+200))
    SCREEN.blit(title_surface_1, (10, 10))
    pygame.draw.lines(SCREEN, WHITE, False, point_list, 3)
    sgc.update(time)
    pygame.display.update()
