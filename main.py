import pygame
import sys
import urllib2
import json

pygame.init()

WHITE = (255, 255, 255)
BLUE = (100, 100, 220)
RED = (200, 100, 100)
SCREEN = pygame.display.set_mode((800, 600))
main_font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 50)


tide_object = urllib2.urlopen('http://api.spitcast.com/api/county/tide/santa-cruz/')
tide_json = tide_object.read()
tide_data = json.loads(tide_json)

point_list = []
x = 20

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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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
    pygame.display.update()