import asyncio
import os
import random
import threading
import time

import idl_helper as idl
import pygame
from highrise_funcs import (
    draw_overlay,
    draw_scene,
    generate_grid_structure,
    load_texture,
    save_screenshot,
    setup_projection_and_lighting,
)
from NatNetClient import NatNetClient
from OpenGL.GL import *
from pygame.locals import *
from pynput.mouse import Listener
from pythonosc import udp_client

USE_MOCK_POS_DATA = True
USE_MOCK_IMAGE=True
COMFYUI_OUTPUT_FOLDER = "C:\\Demos\\Wen\\ComfyUI_windows_portable\\ComfyUI\\output"
SET_FULLSCREEN = False

mocap_x = 1280
mocap_y = 800
mocap_dist = 10
overlay_texture_data = None
left_button_held = False

# Create an event to signal when the thread should stop
stop_event = threading.Event()


def receive_new_pos(rigid_body_list):
    if len(rigid_body_list) != 2:
        return

    start = rigid_body_list[0]
    end = rigid_body_list[1]

    if start.id_num > end.id_num:
        start = end
        end = rigid_body_list[0]

    broadcast_rigid_body(rigid_body_list)

    pt_on_screen, pt_on_dome, rigidbody_dist = idl.process_tracked_poses(start, end)
    if (pt_on_screen is None) or (pt_on_dome is None) or (rigidbody_dist is None):
        return

    send_2_holophonix(pt_on_dome[0], pt_on_dome[1], pt_on_dome[2], rigidbody_dist)
    send_2_pygame(pt_on_screen[0], pt_on_screen[1], rigidbody_dist)


def receive_mock():
    global mocap_x, mocap_y, mocap_dist
    while not stop_event.is_set():
        time.sleep(0.1)
        try:
            mocap_x, mocap_y = pygame.mouse.get_pos()
        except:
            mocap_x, mocap_y = 640, 400
        mocap_dist = mocap_y / 50
        # mocap_z = 1.6

        # send_2_holophonix(mocap_x, mocap_y, mocap_z, mocap_dist) #not sure if this is needed
        # send_2_pygame(mocap_x, mocap_y, mocap_dist)


def broadcast_rigid_body(rigid_body_list):
    print(f"found rigid_body count: {len(rigid_body_list)}")
    for rigid_body in rigid_body_list:
        print(f"id: {rigid_body.id_num}")
        print(f"pos: {rigid_body.pos[0]}, {rigid_body.pos[1]}, {rigid_body.pos[2]}")


def send_2_holophonix(x, y, z, reverb):
    global left_button_held

    x, y, z = idl.map_point_2_holophonix(x, y, z)

    # dist range: 0 - 1
    # reverb range: 0 - 10
    reverb = idl.map_range(reverb, 0, 1, 0, 15)
    holophonix_client.send_message("/reverb/2/tr0", reverb)

    if left_button_held:
        holophonix_client.send_message("/track/1/xyz", tuple([x, y, z]))
        holophonix_client.send_message("/track/1/gain", 12)
    else:
        holophonix_client.send_message("/track/1/xyz", tuple([0.1, 0.1, 0.1]))
        holophonix_client.send_message("/track/1/gain", 6)


def send_2_pygame(w, h, room_size):
    global left_button_held
    global mocap_x, mocap_y, mocap_dist
    mocap_x, mocap_y = w, h
    mocap_x, mocap_y = idl.map_point_2_pygame_window(mocap_x, mocap_y)
    mocap_dist = room_size * 20


async def load_rendered_img_async(img_folder):
    global overlay_texture_data
    if USE_MOCK_IMAGE:
        print("Loading the dummy rendered image asynchronously...")
        await asyncio.sleep(1)  # Wait for 1 second before loading the texture

        overlay_texture_data = load_texture(
            "../image_gen/comfyui_worklfows/workflow_highrise.png"
        )
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
    random.seed(42)
    streaming_client = None
    receive_thread = None
    if USE_MOCK_POS_DATA:
        # from mouse
        receive_thread = threading.Thread(target=receive_mock)
        receive_thread.start()
    else:
        # from motive client
        streaming_client = NatNetClient()
        streaming_client.pos_listener = receive_new_pos
        streaming_client.set_print_level(update_interval)
        streaming_client.run()

    # pygame
    pygame.init()
    display = (int(screen_width * window_scale), int(screen_height * window_scale))
    pygame.display.set_caption("GenAI_render")
    if SET_FULLSCREEN:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    setup_projection_and_lighting()
    # Force a white background
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Pre-generate a big grid so we can handle up to e.g. 30 axes
    floors = 12
    max_axes = 30
    grid = generate_grid_structure(
        floors=floors, max_axes_x=max_axes, max_axes_z=max_axes, porosity=0.5
    )

    save_screenshot_flag = False
    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    # init game loop variables
    global overlay_texture_data
    global left_button_held
    running = True
    cafe_size = 6
    axes_w = 5
    last_x, last_y, last_cafe_size = 0, 20, 6

    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                left_button_held = True
                overlay_texture_data = None
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                left_button_held = False
                save_screenshot_flag = True

        if left_button_held:
            # mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x, mouse_y = mocap_x, mocap_y
            print(f"mouse_x: {mouse_x}, mouse_y: {mouse_y}")
            world_width = 96
            world_height = 45
            pos_x = (
                (display[0] - mouse_x) / display[0]
            ) * world_width - world_width / 2
            screen_edge_distance = 40
            pos_x = max(
                screen_edge_distance - world_width / 2,
                min(-screen_edge_distance + world_width / 2, pos_x),
            )
            
            print(f"display[1]: {display[1]}, mouse_y: {mouse_y}")
            pos_y = ((display[1] - mouse_y) / display[1]) * world_height

            cafe_size = mocap_dist  # get dist from mocap
            last_x, last_y, last_cafe_size = pos_x, pos_y, cafe_size
            print(f"pos_x: {pos_x}, pos_y: {pos_y}, cafe_size: {cafe_size}")
            draw_scene(pos_x, pos_y, cafe_size, axes_w, grid, floors)

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
            draw_scene(last_x, last_y, last_cafe_size, axes_w, grid, floors)

        pygame.display.flip()

    # clean up after the loop
    stop_event.set()
    if receive_thread:
        receive_thread.join()
    if streaming_client:
        streaming_client.shutdown()


if __name__ == "__main__":
    # region Constants
    # random.seed(42)
    screen_width, screen_height = 2560, 1600
    window_scale = 0.5
    # left_button_held = False

    stop_event = threading.Event()
    update_interval = 30
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)
    # endregion

    main()
