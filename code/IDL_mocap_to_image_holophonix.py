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

# ----------------------
# Configuration
# ----------------------
USE_MOCK_POS_DATA = False
USE_MOCK_IMAGE = False
COMFYUI_OUTPUT_FOLDER = "C:\\Demos\\Wen\\ComfyUI_windows_portable\\ComfyUI\\output"
SET_FULLSCREEN = True

# ----------------------
# Modes
# ----------------------
MODE_INTERACTION = 0  # User can move cafe around
MODE_RENDER = 1  # Position is frozen, then overlay image is displayed
current_mode = MODE_INTERACTION

# ----------------------
# Globals
# ----------------------
mocap_x = 1280
mocap_y = 800
mocap_dist = 10

# Café position in the world
pos_x, pos_y = 0, 20
cafe_size = 6

# When we switch to RENDER mode, freeze the position
frozen_x, frozen_y, frozen_size = 0, 20, 6

# Overlay image (None means no image loaded)
overlay_texture_data = None

# This flag lets us know we need to screenshot & load an image
save_screenshot_flag = False

# For reverb or other logic
left_button_held = False

# Create an event to signal threads to stop
stop_event = threading.Event()

# holophonix client
holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

# ----------------------
# Mocap + Holophonix
# ----------------------
def receive_new_pos(rigid_body_list):
    if len(rigid_body_list) != 2:
        return

    start, end = rigid_body_list
    if start.id_num > end.id_num:
        start, end = end, start

    #broadcast_rigid_body(rigid_body_list)

    pt_on_screen, pt_on_dome, rigidbody_dist = idl.process_tracked_poses(start, end)
    if (pt_on_screen is None) or (pt_on_dome is None) or (rigidbody_dist is None):
        return

    #old sound effect
    # send_2_holophonix(pt_on_dome[0], pt_on_dome[1], pt_on_dome[2], rigidbody_dist)
     
    # new sound effect
    send_2_holophonix_new(rigidbody_dist) 
    send_2_pygame(pt_on_screen[0], pt_on_screen[1], rigidbody_dist)


def receive_mock():
    """Mock thread to continuously set mocap_x, mocap_y from pygame's mouse."""
    global mocap_x, mocap_y, mocap_dist
    while not stop_event.is_set():
        time.sleep(0.1)
        try:
            mocap_x, mocap_y = pygame.mouse.get_pos()
        except:
            mocap_x, mocap_y = 640, 400
        mocap_dist = mocap_y / 50


def broadcast_rigid_body(rigid_body_list):
    print(f"found rigid_body count: {len(rigid_body_list)}")
    for rigid_body in rigid_body_list:
        print(f"id: {rigid_body.id_num}")
        print(f"pos: {rigid_body.pos[0]}, {rigid_body.pos[1]}, {rigid_body.pos[2]}")


def send_2_holophonix(x, y, z, reverb):
    """Example function that updates a Holophonix client based on user input."""
    global current_mode

    x, y, z = idl.map_point_2_holophonix(x, y, z)
    reverb_mapped = idl.map_range(reverb, 0, 1, 0, 15)
    holophonix_client.send_message("/reverb/2/tr0", reverb_mapped)
    if current_mode == MODE_RENDER:
        holophonix_client.send_message("/track/1/xyz", (0.1, 0.1, 0.1))
        holophonix_client.send_message("/track/1/gain", 6) 
    else:
        holophonix_client.send_message("/track/1/xyz", (x, y, z))
        holophonix_client.send_message("/track/1/gain", 12)
        
def send_2_holophonix_new(reverb):
    global current_mode
    if current_mode == MODE_INTERACTION:
        reverb_mapped = idl.map_range(reverb, 0, 1, 0, 15)
        holophonix_client.send_message("/reverb/2/tr0", reverb_mapped)

    # below two lines can be removed if the default setting in holophonix is set properly 
    holophonix_client.send_message("/track/1/xyz", (0.1, 0.1, 0.1))  # location of sound
    holophonix_client.send_message("/track/1/gain", 6) # volume of sound

def send_2_pygame(w, h, room_size):
    """Updates global mocap_x/mocap_y from w,h. Adjusts distance."""
    global mocap_x, mocap_y, mocap_dist
    mocap_x, mocap_y = idl.map_point_2_pygame_window(w, h)
    mocap_dist = room_size * 20


# ----------------------
# Async image loading
# ----------------------
async def load_rendered_img_async(img_folder):
    """Wait for a new .png in img_folder, then load it into overlay_texture_data."""
    global overlay_texture_data
    if USE_MOCK_IMAGE:
        print("Loading the dummy rendered image asynchronously...")
        await asyncio.sleep(1)
        overlay_texture_data = load_texture(
            "../image_gen/comfyui_worklfows/workflow_highrise.png"
        )
        print("Dummy Rendered image loaded!")
        return

    print("Loading the rendered image asynchronously...")
    start_time = time.time()
    time_elapsed = 0
    # Wait until a new PNG file is found in the folder with a modification time after start_time
    while time_elapsed < 30:
        await asyncio.sleep(0.1)
        for file_name in os.listdir(img_folder):
            file_path = os.path.join(img_folder, file_name)
            if os.path.isfile(file_path) and file_name.endswith(".png"):
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time > start_time:
                    retries = 5
                    for attempt in range(retries):
                        try:
                            overlay_texture_data = load_texture(file_path)
                            print("Rendered image loaded!")
                            return
                        except FileNotFoundError as e:
                            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                            await asyncio.sleep(0.5)
        time_elapsed = time.time() - start_time
        print(time_elapsed)
    print("loading image failed")


# ----------------------
# Main Pygame Loop
# ----------------------
def main():
    global current_mode
    global pos_x, pos_y, cafe_size
    global frozen_x, frozen_y, frozen_size
    global overlay_texture_data, save_screenshot_flag

    random.seed(42)
    streaming_client = None
    receive_thread = None

    # Start up either a mock or real streaming client
    if USE_MOCK_POS_DATA:
        receive_thread = threading.Thread(target=receive_mock)
        receive_thread.start()
    else:
        streaming_client = NatNetClient()
        streaming_client.pos_listener = receive_new_pos
        streaming_client.set_print_level(10)
        streaming_client.run()

    # Pygame init
    pygame.init()
    screen_width, screen_height = 2560, 1600
    window_scale = 0.5
    display = (int(screen_width * window_scale), int(screen_height * window_scale))
    pygame.display.set_caption("GenAI_render")

    if SET_FULLSCREEN:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    setup_projection_and_lighting()
    glClearColor(1.0, 1.0, 1.0, 1.0)

    floors = 12
    floor_height = 4.0
    building_height = floors * floor_height
    axes_width = 4.0
    max_axes = 30
    grid = generate_grid_structure(
        floors=floors, max_axes_x=max_axes, max_axes_z=max_axes, porosity=0.5
    )

    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Toggle between modes on each click
                if current_mode == MODE_INTERACTION:
                    # Switch to render mode: freeze the last known café position
                    current_mode = MODE_RENDER
                    frozen_x, frozen_y, frozen_size = pos_x, pos_y, cafe_size

                    # Clear any old overlay
                    overlay_texture_data = None

                    # Trigger screenshot -> new image load
                    save_screenshot_flag = True
                    print("render")
                else:
                    # Switch back to interaction mode
                    current_mode = MODE_INTERACTION
                    overlay_texture_data = None
                    print("interact")

        # Update / Draw based on the current mode
        if current_mode == MODE_INTERACTION:
            # Read from mocap
            mouse_x, mouse_y = mocap_x, mocap_y
            world_width = 96
            world_height = 50

            # Convert from screen coords to world coords
            pos_x = ((display[0] - mouse_x) / display[0]) * world_width - (
                world_width / 2
            )

            screen_edge_distance = 40
            pos_x = max(
                screen_edge_distance - world_width / 2,
                min(-screen_edge_distance + world_width / 2, pos_x),
            )

            pos_y = ((display[1] - mouse_y) / display[1]) * world_height
            pos_y = max(0, min(pos_y, building_height-floor_height))


            cafe_size = max(axes_width,mocap_dist)
            # Draw the scene with the live café position
            draw_scene(pos_x, pos_y, cafe_size, axes_width, grid, floors, floor_height=floor_height)
        else:
            # If an overlay texture is available, draw it now
            if overlay_texture_data is not None:
                texture_id, tex_width, tex_height = overlay_texture_data
                draw_overlay(texture_id, tex_width, tex_height, display)
            else:
                # RENDER mode: freeze at (frozen_x, frozen_y, frozen_size)
                draw_scene(
                    frozen_x, frozen_y, frozen_size, axes_width, grid, floors, floor_height=floor_height
                )

        # If user requested a screenshot, do so and load the new image
        if save_screenshot_flag:
            save_screenshot_flag = False
            save_screenshot(display, os.path.join(screenshot_folder, "screenshot.png"))
            asyncio.run(load_rendered_img_async(COMFYUI_OUTPUT_FOLDER))

        

        pygame.display.flip()

    # Cleanup
    stop_event.set()
    if receive_thread:
        receive_thread.join()
    if streaming_client:
        streaming_client.shutdown()


if __name__ == "__main__":
    main()
