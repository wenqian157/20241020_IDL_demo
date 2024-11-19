import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *  # Import GLUT
from pygame.locals import *
import time


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


def draw_scene(pos_x, pos_y, distance):
    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    # Set material properties
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.8, 0.5, 0.2, 1))  # Cube color
    glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1))  # Specular color
    glMaterialf(GL_FRONT, GL_SHININESS, 50)  # Shininess factor

    # Draw the first box (40 tall, 21 wide, 21 deep), centered at (pos_x, 20, 0)
    glPushMatrix()
    glTranslatef(pos_x, 20, 0)  # Translate to the desired position
    glScalef(21, 40, 21)  # Scale to the desired dimensions
    glutSolidCube(1)  # Draw a unit cube scaled to the desired size
    glPopMatrix()

    # Draw the second box (distance wide, 4 tall, 23 deep), centered at (pos_x, pos_y, 0)
    glPushMatrix()
    glTranslatef(pos_x, pos_y, 0)  # Translate to the desired position
    glScalef(distance, 4, 23)  # Scale to the desired dimensions
    glutSolidCube(1)  # Draw a unit cube scaled to the desired size
    glPopMatrix()


def save_screenshot(display, filename="cube_screenshot.png"):
    """Save a screenshot of the current OpenGL buffer."""
    width, height = display
    # Read the pixels from the frame buffer
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    # Create a Pygame surface from the pixel data
    image = pygame.image.fromstring(data, (width, height), "RGBA", True)
    # Flip the image vertically to correct orientation
    image = pygame.transform.flip(image, False, True)
    # Save the image as a PNG file
    pygame.image.save(image, filename)
    print(f"Screenshot saved as {filename}")


def render_image():
    """Simulate rendering process (e.g., API call) by waiting for 1 second."""
    time.sleep(1)
    return True  # Simulate that rendering completed successfully


def main():
    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    window_scale = 0.5
    set_fullscreen = False
    screen_width, screen_height = 2560, 1600
    display = (int(screen_width * window_scale), int(screen_height * window_scale))
    pygame.display.set_caption("GenAI_render")
    if set_fullscreen:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    else:
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Initialize GLUT
    glutInit([])

    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 150.0)
    glMatrixMode(GL_MODELVIEW)
    # camera position, look at position, up direction
    gluLookAt(0.0, 20.0, -100.0, 0.0, 20.0, 0.0, 0.0, 1.0, 0.0)

    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set up light parameters
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))  # Light position
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Ambient light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1))  # Diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1))  # Specular light

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
    value = 0
    last_x, last_y, last_value = 0, 0, 0
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
            pos_y = ((display[1] - mouse_y) / display[1]) * world_height
            last_x, last_y, last_value = pos_x, pos_y, value
            draw_scene(pos_x, pos_y, value)

        # Check if we need to save the screenshot
        if save_screenshot_flag:
            save_screenshot(display)
            save_screenshot_flag = False  # Reset the flag

        if rendering:
            rendering_completed = render_image()
            rendering = False
        elif rendering_completed:
            draw_overlay(texture_id, display)
        else:
            # Display the last state of the scene while rendering is happening
            draw_scene(last_x, last_y, last_value)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
