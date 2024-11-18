import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *  # Import GLUT

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
        GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, image_data
    )

    return texture_id, width, height


def draw_overlay(texture_id, display_size, opacity=0.5):
    """Draw the overlay image with blending."""
    width, height = display_size
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glDisable(GL_LIGHTING)  # Disable lighting before drawing the overlay
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Set transparency to 50%
    glColor4f(1, 1, 1, opacity)

    # Save the current projection matrix
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)

    # Save the current modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw the overlay quad
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glTexCoord2f(1, 1); glVertex2f(width, height)
    glTexCoord2f(0, 1); glVertex2f(0, height)
    glEnd()

    # Restore the original projection and modelview matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)  # Re-enable lighting


def draw_scene():
    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    # Set material properties
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.8, 0.5, 0.2, 1))  # Cube color
    glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1))             # Specular color
    glMaterialf(GL_FRONT, GL_SHININESS, 50)                             # Shininess factor

    glutSolidCube(2)

def save_screenshot(display, filename='cube_screenshot.png'):
    """Save a screenshot of the current OpenGL buffer."""
    width, height = display
    # Read the pixels from the frame buffer
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    # Create a Pygame surface from the pixel data
    image = pygame.image.fromstring(data, (width, height), 'RGBA', True)
    # Flip the image vertically to correct orientation
    image = pygame.transform.flip(image, False, True)
    # Save the image as a PNG file
    pygame.image.save(image, filename)
    print(f"Screenshot saved as {filename}")

def main():
    # Initialize Pygame and create an OpenGL-compatible window
    pygame.init()
    display = (1280, 800)
    pygame.display.set_caption('GenAI_render')
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)

    # Initialize GLUT
    glutInit([])

    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -5)

    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set up light parameters
    glLightfv(GL_LIGHT0, GL_POSITION,  (5, 5, 5, 1))  # Light position
    glLightfv(GL_LIGHT0, GL_AMBIENT,   (0.2, 0.2, 0.2, 1))  # Ambient light
    glLightfv(GL_LIGHT0, GL_DIFFUSE,   (0.5, 0.5, 0.5, 1))  # Diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR,  (1.0, 1.0, 1.0, 1))  # Specular light

    # Load the overlay texture
    texture_id, tex_width, tex_height = load_texture('overlay.png')

    clock = pygame.time.Clock()
    save_screenshot_flag = False  # Initialize the screenshot flag

    # Main loop
    running = True
    # angle = 0  # For cube rotation
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                save_screenshot_flag = True  # Set flag on mouse button press

        

        # Draw the scene
        draw_scene()

        # Check if we need to save the screenshot
        if save_screenshot_flag:
            save_screenshot(display)
            save_screenshot_flag = False  # Reset the flag

        # Draw the overlay image
        draw_overlay(texture_id, display)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
