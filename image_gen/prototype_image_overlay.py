import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

# from OpenGL.GLUT import *  # Import GLUT
from pygame.locals import *
import time
import random
from math import tan, radians
import os

from highrise_funcs import (
    generate_grid_structure,
    draw_scene,
    save_screenshot,
    setup_projection_and_lighting,
)

# Set a seed for reproducibility
random.seed(42)


def load_texture(image_path):
    """Load an image and convert it to a texture."""
    image = pygame.image.load(image_path)
    # Remove the flip if image appears upside down
    # image = pygame.transform.flip(image, False, True)
    image_data = pygame.image.tostring(image, "RGBA", True)
    width, height = image.get_rect().size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        image_data,
    )

    return texture_id, width, height


def draw_overlay(texture_id, display_size):
    """Draw the overlay image, maintaining aspect ratio."""
    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    display_width, display_height = display_size
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glDisable(GL_LIGHTING)  # Disable lighting before drawing the overlay

    # Set color
    glColor4f(1, 1, 1, 1)

    # Save the current projection matrix
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display_width, 0, display_height, -1, 1)

    # Save the current modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Calculate aspect ratio to maintain proportions
    overlay_aspect_ratio = tex_width / tex_height
    display_aspect_ratio = display_width / display_height

    if display_aspect_ratio > overlay_aspect_ratio:
        new_height = display_height
        new_width = new_height * overlay_aspect_ratio
    else:
        new_width = display_width
        new_height = new_width / overlay_aspect_ratio

    x_offset = (display_width - new_width) / 2
    y_offset = (display_height - new_height) / 2

    # Draw the overlay quad with adjusted dimensions
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1, 0)
    glVertex2f(x_offset + new_width, y_offset)
    glTexCoord2f(1, 1)
    glVertex2f(x_offset + new_width, y_offset + new_height)
    glTexCoord2f(0, 1)
    glVertex2f(x_offset, y_offset + new_height)
    glEnd()

    # Restore the original projection and modelview matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)  # Re-enable lighting


def render_image():
    """Simulate rendering process (e.g., API call) by waiting for 1 second."""
    time.sleep(0.1)
    return True  # Simulate that rendering completed successfully


def main():
    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    window_scale = 0.5
    set_fullscreen = True
    screen_width, screen_height = 2560, 1600
    display = (int(screen_width * window_scale), int(screen_height * window_scale))

    screenshot_folder = "screenshot"
    os.makedirs(screenshot_folder, exist_ok=True)

    pygame.display.set_caption("GenAI_render")
    if set_fullscreen:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    setup_projection_and_lighting()

    # Generate the grid structure for the building
    grid_structure = generate_grid_structure()

    # Load the overlay texture
    global tex_width, tex_height
    texture_id, tex_width, tex_height = load_texture("overlay.png")

    clock = pygame.time.Clock()
    save_screenshot_flag = False  # Initialize the screenshot flag
    mouse_button_held = False
    rendering = False
    rendering_completed = False

    # Main loop
    running = True
    value = 6
    last_x, last_y, last_value = 0, 20, 6
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_button_held = True
                rendering_completed = False
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                mouse_button_held = False
                save_screenshot_flag = True  # Set flag on mouse button press
                rendering = True
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
            # add a timestamp to the filename
            # timestamp = time.strftime("%Y%m%d-%H%M%S")
            # save_screenshot(display, f"{timestamp}_screenshot.png")
            save_screenshot(display, os.path.join(screenshot_folder, "screenshot.png"))
            save_screenshot_flag = False  # Reset the flag

        if rendering:
            rendering_completed = render_image()
            rendering = False
        elif rendering_completed:
            draw_overlay(texture_id, display)
        else:
            # Display the last state of the scene while rendering is happening
            draw_scene(last_x, last_y, last_value, grid_structure)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
