import socket
import struct
import time
import threading
from pynput.mouse import Listener
import numpy as np
from pythonosc import udp_client
import pygame 
import sys

from pygame.locals import *

def map_range(value, old_min, old_max, new_min, new_max):
    return((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def map_point_2_pygame_window(x, y):
    window_size = (1280, 800)
    x = map_range(x, 4, -4, 0, window_size[0])
    y = map_range(y, 5, 0, 0, window_size[1])
    return x, y

def update_draw(values):
    if values == None:
        x, y = 640, 400
        dist = 10
    else:
        x, y = values[0], values[1]
        x, y = map_point_2_pygame_window(x, y)
        dist = values[5] * 100

    screen.fill((0, 0, 0))

    point_color = (0, 0, 255)
    point_radius = dist

    pygame.draw.circle(screen, point_color, (x, y), point_radius)
    pygame.display.flip()

def map_point_2_holophonix(x, y, z):
    x = -x
    y = z
    z = y
    return x, y, z

def receive():
    while True:
        data, addr = sock.recvfrom(1024)
        values = struct.unpack("ffffff", data)
        # print(f"Received message: {values} from {addr}")

        send_2_holophonix(values)
        update_draw(values)

def send_2_holophonix(values):
    global left_button_held
    if values == None:
        return
    
    x, y, z, dist = values[2], values[3], values[4], values[5]
    x, y, z = map_point_2_holophonix(x, y, z)

    # dist range: 0 - 1
    # reverb range: 0 - 10
    reverb = map_range(dist, 0, 1, 0, 15)
    holophonix_client.send_message("/reverb/2/tr0", reverb)

    if left_button_held:
        holophonix_client.send_message("/track/1/xyz", tuple([x, y, z]))
        holophonix_client.send_message("/track/1/gain", 6)
    else:
        holophonix_client.send_message("/track/1/xyz", tuple([0.1, 0.1, 0.1]))
        holophonix_client.send_message("/track/1/gain", 0)
        
def on_click(x, y, button, pressed):
    global left_button_held
    if pressed:
        if button.name == "left":
            left_button_held = True
            print(f"stream = {left_button_held}")

        elif button.name == "right":
            left_button_held = False
            print(f"stream = {left_button_held}")

if __name__ == "__main__":
    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # holophonix client
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

    # init pygame draw
    pygame.init()
    window_size = (1280, 800)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("draw a 2d point")

    # receive udp
    receice_thread = threading.Thread(target=receive)
    receice_thread.start()

    # main thread
    running = True

    left_button_held = False
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
                sock.close()
                receice_thread.join()
                pygame.quit()
                sys.exit()
                running = False
                break
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                print("stream")
                left_button_held = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                print("stop")
                left_button_held = False
        