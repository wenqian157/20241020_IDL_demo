import asyncio
import os
import random
import time

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

COMFYUI_OUTPUT_FOLDER = "D:\\Anton\\ComfyUI_windows_portable\\ComfyUI\\output"


async def load_rendered_img_async(img_folder):
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
                            global overlay_texture_data
                            overlay_texture_data = load_texture(file_path)
                            print("Rendered image loaded!")
                            return
                        except FileNotFoundError as e:
                            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                            await asyncio.sleep(0.5)  # Wait an additional 500ms before retrying


def main():
    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    window_scale = 0.25
    set_fullscreen = False
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

    save_screenshot_flag = False
    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    global overlay_texture_data
    mouse_button_held = False
    running = True
    value = 6
    last_x, last_y, last_value = 0, 20, 6

    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_button_held = True
                overlay_texture_data = None
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                mouse_button_held = False
                save_screenshot_flag = True
            elif event.type == pygame.MOUSEWHEEL:
                value += event.y  # event.y is +1 for up scroll, -1 for down scroll

        if mouse_button_held:
            mouse_x, mouse_y = pygame.mouse.get_pos()
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

    pygame.quit()


if __name__ == "__main__":
    main()
