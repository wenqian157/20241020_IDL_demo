import socket
import struct
import pygame
import time
import sys
import threading
from pynput.mouse import Listener


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
        dist = values[2] * 100

    screen.fill((0, 0, 0))

    point_color = (0, 0, 255)
    point_radius = dist

    pygame.draw.circle(screen, point_color, (x, y), point_radius)
    pygame.display.flip()

def update_ai_draw(values):
    # here to update the box location and size based on values
    # succesful values is a list of 3 float: point.x, point.y, dist 
    pass

def update_ai_generate():
    # here take mouse input to update ai generating
    # see function on_click
    pass

def on_click(x, y, button, pressed):
    if pressed:
        if button.name == "left":
            print("left")
            # update_ai_generate()
        elif button.name == "right":
            print("right")

def receive():
    while True:
        data, addr = sock.recvfrom(12)
        values = struct.unpack("!fff", data)
        print(f"Received message: {values} from {addr}")

        # display result
        update_draw(values)
    

if __name__ == "__main__":
    
    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # init pygame draw
    pygame.init()
    window_size = (1280, 800)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("draw a 2d point")

    receice_thread = threading.Thread(target=receive)
    # receice_thread.daemon = True
    receice_thread.start()
    
    # set up listener to for mouse click
    listener = Listener(on_click=on_click)
    listener.start()

    # main thread
    running = True
    while running:
        print("running")
        user_input = input('Enter q to quit')
        if user_input == "q":
            sock.close()
            # receice_thread.join()
            pygame.quit()
            sys.exit()
            listener.stop()
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

