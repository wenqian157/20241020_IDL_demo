import os
import random
import time
import math

import pygame
from pygame.locals import *

from OpenGL.GL import glClear, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

from highrise_funcs import (
    draw_scene,
    generate_grid_structure,
    save_screenshot,
    setup_projection_and_lighting,
)

# Seed for reproducibility if needed
random.seed(42)


# --- HELPER FUNCTIONS FOR ANIMATIONS --- #
def linear_animation_params(
    anim_time, start_x, start_y, end_x, end_y, start_size, end_size, duration=1.0
):
    """
    Returns (pos_x, pos_y, size) linearly interpolated over 'duration' seconds,
    looping every time 'anim_time' reaches duration.
    """
    # Convert anim_time into a repeating 0–1 factor
    t = (anim_time % duration) / duration

    # Linear interpolation
    pos_x = start_x + (end_x - start_x) * t
    pos_y = start_y + (end_y - start_y) * t
    size = start_size + (end_size - start_size) * t
    return pos_x, pos_y, size


def circular_animation_params(
    anim_time, center_x, center_y, radius, base_size, size_amplitude
):
    """
    Returns (pos_x, pos_y, size) moving along a circle of 'radius',
    and optionally oscillating the size in a sinusoidal manner.
    """
    pos_x = center_x + radius * math.cos(anim_time)
    pos_y = center_y + radius * math.sin(anim_time)
    size = base_size + size_amplitude * math.sin(anim_time)
    return pos_x, pos_y, size


def main():
    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    window_scale = 0.25
    screen_width, screen_height = 2560, 1600
    display = (int(screen_width * window_scale), int(screen_height * window_scale))
    pygame.display.set_caption("GenAI_render_Animation")

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Set up the OpenGL projection, lighting, etc.
    setup_projection_and_lighting()

    # Force a white background
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Generate the grid structure for the building
    grid_structure = generate_grid_structure()

    # Folder for screenshots
    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    # Number of frames to export
    total_frames = 300

    # Animation parameters (adjust these to suit your scene)
    # For linear animation:
    linear_start = (10, 2)
    linear_end = (-10, 45)
    linear_size_start = 4
    linear_size_end = 13
    linear_duration = 3.0

    param_names = ["y", "size", "axes_width"]
    states = [[2, 4.0, 3.0],[2, 4.0, 3.0]]

    # For circular animation:
    circle_center = (0, 0)
    circle_radius = 15
    circle_base_size = 6
    circle_size_amplitude = 3

    running = True
    frame = 0

    while running:
        # Simple event handling to allow window close
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        if frame >= total_frames:
            # After we reach total_frames, end the loop
            running = False
        else:
            # Calculate animation time
            anim_time = frame * 0.01

            # Clear the buffers to ensure white background each frame
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Choose your animation function:
            # 1) Linear
            pos_x, pos_y, size = linear_animation_params(
                anim_time,
                linear_start[0],
                linear_start[1],
                linear_end[0],
                linear_end[1],
                linear_size_start,
                linear_size_end,
                linear_duration,
            )

            # 2) Circular (uncomment to use instead of linear)
            # pos_x, pos_y, size = circular_animation_params(
            #     anim_time,
            #     circle_center[0], circle_center[1],
            #     circle_radius,
            #     circle_base_size,
            #     circle_size_amplitude
            # )

            # Draw the scene
            draw_scene(pos_x, pos_y, size, grid_structure)

            # Save screenshot with frame index
            screenshot_path = os.path.join(
                screenshot_folder, f"screenshot_{frame:03d}.png"
            )
            save_screenshot(display, screenshot_path)

            # Update display
            pygame.display.flip()

            frame += 1

    pygame.quit()


if __name__ == "__main__":
    main()
