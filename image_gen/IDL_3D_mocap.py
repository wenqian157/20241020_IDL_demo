import asyncio
import os
import random
import time
import socket
import struct
import threading
import sys
from pynput.mouse import Listener
from pythonosc import udp_client

# from math import radians, tan

import pygame
from highrise_funcs import (
    draw_overlay,
    draw_scene,
    generate_grid_structure,
    load_texture,
    save_screenshot,
    setup_projection_and_lighting,
)
from pygame.locals import *

# Set a seed for reproducibility
random.seed(42)

overlay_texture_data = None

USE_MOCK_DATA = True

COMFYUI_OUTPUT_FOLDER = "D:\\Demos\\Wen\\ComfyUI_windows_portable\\ComfyUI\\output"

mocap_x = 1280
mocap_y = 800
mocap_dist = 10
left_button_held = False
save_screenshot_flag = False

# Create an event to signal when the thread should stop
stop_event = threading.Event()

def map_range(value, old_min, old_max, new_min, new_max):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def map_point_2_pygame_window(x, y):
    window_size = (1280, 800)
    x = map_range(x, 4, -4, 0, window_size[0])
    y = map_range(y, 5, 0, 0, window_size[1])
    return x, y

def map_point_2_holophonix(x, y, z):
    x = -x
    y = z
    z = y
    return x, y, z

def receive():
    global mocap_x, mocap_y, mocap_dist
    while not stop_event.is_set():
        data, addr = sock.recvfrom(1024)
        values = struct.unpack("ffffff", data)
        print(f"Received message: {values} from {addr}")
        if values == None:
            mocap_x, mocap_y = 640, 400
            mocap_dist = 10
        else:
            # update drawing
            mocap_x, mocap_y = values[0], values[1]
            mocap_x, mocap_y = map_point_2_pygame_window(mocap_x, mocap_y)
            mocap_dist = values[5] * 20

            # update sound
            # send_2_holophonix(values)

def receive_mock():
    global mocap_x, mocap_y, mocap_dist
    while not stop_event.is_set():
        time.sleep(0.1)
        try:
            mocap_x, mocap_y = pygame.mouse.get_pos()
        except:
            mocap_x, mocap_y = 640, 400
        mocap_dist = mocap_y / 100

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
        holophonix_client.send_message("/track/1/gain", 12)
    else:
        holophonix_client.send_message("/track/1/xyz", tuple([0.1, 0.1, 0.1]))
        holophonix_client.send_message("/track/1/gain", 6)

async def load_rendered_img_async(img_folder):
    global overlay_texture_data
    if USE_MOCK_DATA:
        print("Loading the dummy rendered image asynchronously...")
        await asyncio.sleep(1)  # Wait for 1 second before loading the texture

        overlay_texture_data = load_texture("comfyui_worklfows/workflow_highrise.png")
        print("Dummy Rendered image loaded!")
        return
    print("Loading the rendered image asynchronously...")
    start_time = time.time()  # Record the start time

    # Wait until a new file is found in the folder with a modification time after start_time
    while True:
        await asyncio.sleep(0.1)  # Check every 100ms for a new file
        for file_name in os.listdir(img_folder):
            file_path = os.path.join(img_folder, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".png"):
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time > start_time:
                    # Retry loading if there is an issue due to a locked file
                    retries = 5
                    for attempt in range(retries):
                        try:
                            # global overlay_texture_data
                            overlay_texture_data = load_texture(file_path)
                            print("Rendered image loaded!")
                            return
                        except FileNotFoundError as e:
                            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                            await asyncio.sleep(
                                0.5
                            )  # Wait an additional 500ms before retrying


def main():
    global mocap_x, mocap_y, mocap_dist
    # use_mock_data = False
    if USE_MOCK_DATA:
        receive_thread = threading.Thread(target=receive_mock)
        receive_thread.start()
    else:
        receive_thread = threading.Thread(target=receive)
        receive_thread.start()

    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    window_scale = 0.5
    set_fullscreen = True
    screen_width, screen_height = 2560, 1600
    display = (int(screen_width * window_scale), int(screen_height * window_scale))
    pygame.display.set_caption("GenAI_render")
    if set_fullscreen:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    setup_projection_and_lighting()

    # Generate the grid structure for the building
    grid_structure = generate_grid_structure()

    global save_screenshot_flag
    # save_screenshot_flag = False
    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    global overlay_texture_data
    global left_button_held
    # mouse_button_held = False
    running = True
    value = 6
    last_x, last_y, last_value = 0, 20, 6

    # Main loop
    while running:
        for event in pygame.event.get():
            #if event.type == QUIT:
            #    running = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                left_button_held = True
                overlay_texture_data = None
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                left_button_held = False
                save_screenshot_flag = True
            # elif event.type == pygame.MOUSEWHEEL:
            #     value += event.y  # event.y is +1 for up scroll, -1 for down scroll

        if left_button_held:
            # mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x, mouse_y = mocap_x, mocap_y
            world_width = 96
            world_height = 60
            pos_x = (
                (display[0] - mouse_x) / display[0]
            ) * world_width - world_width / 2
            screen_edge_distance = 25
            pos_x = max(
                screen_edge_distance - world_width / 2,
                min(-screen_edge_distance + world_width / 2, pos_x),
            )
            value = mocap_dist # get dist from mocap
            pos_y = ((display[1] - mouse_y) / display[1]) * world_height
            last_x, last_y, last_value = pos_x, pos_y, value
            draw_scene(pos_x, pos_y, value, grid_structure)

        # Check if we need to save the screenshot
        if save_screenshot_flag:
            save_screenshot(display, os.path.join(screenshot_folder, "screenshot.png"))
            asyncio.run(load_rendered_img_async(COMFYUI_OUTPUT_FOLDER))
            save_screenshot_flag = False

        if overlay_texture_data is not None:
            texture_id, tex_width, tex_height = overlay_texture_data
            draw_overlay(texture_id, tex_width, tex_height, display)
        else:
            # Display the last state of the scene while rendering is happening
            draw_scene(last_x, last_y, last_value, grid_structure)

        pygame.display.flip()
    sock.close()
    pygame.quit()
    #sys.exit()
    stop_event.set()
    receive_thread.join()

if __name__ == "__main__":

    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # holophonix client
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)
    
    main()
