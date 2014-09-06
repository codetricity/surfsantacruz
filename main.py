import sgc
from sgc.locals import *
import pygame
import sys
import urllib2
import json
import datetime

# uses simple game code for GUI widgets
# https://launchpad.net/simplegc

try:
    import android
except ImportError:
    android = None

def get_tide(daydelta=0):
    date_data = datetime.datetime.now()
    date_data = date_data + datetime.timedelta(days=daydelta)
    month = str(date_data.month)
    if len(month) < 2:
        month = str(0) + month
    day = str(date_data.day)
    if len(day) < 2:
        day = str(0) + day



    date_string = str(date_data.year) + month + day
 #   print(date_string)
    url_string = 'http://api.spitcast.com/api/county/tide/santa-cruz/' + "?dval={}".format(date_string)
    tide_object = urllib2.urlopen(url_string)
    tide_json = tide_object.read()
    tide_d = json.loads(tide_json)
    return tide_d


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
        height_pixel = int(600 - height * 100)
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
SCREEN = pygame.display.set_mode((800, 600))
GUI_SCREEN = sgc.surface.Screen((800, 600))
main_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 20)
big_font = pygame.font.Font("fnt/Ubuntu-M.ttf", 50)

fonts = {"widget": "fnt/Ubuntu-M.ttf", "title": "fnt/Ubuntu-M.ttf",
         "mono": "fnt/Ubuntu-M.ttf"}
sgc.Font.set_fonts(fonts)

days_forecast = 0
tide_data = get_tide()
point_list, x_axis_grid, hour_list, title_surface_1 = get_graph(tide_data)

# adds buttons using the sgc gui toolkit
change_day_btn = DayButton(pos=(650,3), label = "Day +1",
                            label_font = main_font, label_col = WHITE)

reset_day_btn = DayButton(pos = (650, 50), label = "Today",
                          label_font = main_font, label_col = WHITE )

change_day_btn.add(0)
reset_day_btn.add(1)

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
        point_list, x_axis_grid, hour_list, title_surface_1 = \
            get_graph(tide_data)
        SCREEN.fill((0,0,0))
        change_day_btn.clicked = False

    if reset_day_btn.clicked:
        days_forecast = 0
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
            pygame.draw.line(SCREEN, BLUE, (x, 50), (x, 550))
            SCREEN.blit(hour_surface, (x -15, 570))
            display_time = False
        else:
            display_time = True
        counter +=1

    for y in range (100, 600, 100):
        height_text = str((600-y)/100)
        height_surface = main_font.render(height_text + " ft", True, WHITE)
        SCREEN.blit(height_surface, (750, y))
        pygame.draw.line(SCREEN, RED, (50, y), (700, y))
    SCREEN.blit(title_surface_1, (10, 10))
    pygame.draw.lines(SCREEN, WHITE, False, point_list, 3)
    sgc.update(time)
    pygame.display.update()
