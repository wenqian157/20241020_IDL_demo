from NatNetClient import NatNetClient
from pythonosc import udp_client
import idl_helper as idl
from pynput.mouse import Listener
import random
import pygame
import threading
import time
from highrise_funcs import (
    draw_overlay,
    draw_scene,
    generate_grid_structure,
    load_texture,
    save_screenshot,
    setup_projection_and_lighting,
)
from pygame.locals import *


def receive_new_pos(rigid_body_list):
    if(len(rigid_body_list) != 2):
        return 
    
    start = rigid_body_list[0]
    end = rigid_body_list[1]

    if start.id_num > end.id_num:
        start = end
        end = rigid_body_list[0]

    broadcast_rigid_body(rigid_body_list)

    pt_on_screen, pt_on_dome, regidbody_dist = idl.process_tracked_poses(start, end)
    if(pt_on_screen is None) or (pt_on_dome is None) or (regidbody_dist is None):
        return 
    
    send_2_holophonix(pt_on_dome[0], pt_on_dome[1], pt_on_dome[2], regidbody_dist)
    send_2_pygame(pt_on_screen[0], pt_on_screen[1], regidbody_dist)

def receive_mock():
    while not stop_event.is_set():
        time.sleep(0.1)
        try:
            mocap_x, mocap_y = pygame.mouse.get_pos()
        except:
            mocap_x, mocap_y = 640, 400
        mocap_dist = mocap_y / 100
        mocap_z = 1.6

        # send_2_holophonix(mocap_x, mocap_y, mocap_z, mocap_dist) #not sure if this is needed
        send_2_pygame(mocap_x, mocap_y, mocap_dist)

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
    # TODO

def main():
    if USE_MOCK_DATA:
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
    if set_fullscreen:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    #TODO


if __name__ == "__main__":
    # region Constants
    USE_MOCK_DATA = False
    COMFYUI_OUTPUT_FOLDER = "D:\\Anton\\ComfyUI_windows_portable\\ComfyUI\\output"
    random.seed(42)
    window_scale = 0.5
    set_fullscreen = True
    screen_width, screen_height = 2560, 1600
    left_button_held = False
    save_screenshot_flag = False
    stop_event = threading.Event()
    update_interval = 30
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)
    # endregion

    main()




