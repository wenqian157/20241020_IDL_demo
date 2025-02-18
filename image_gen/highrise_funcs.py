from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame


def setup_projection_and_lighting(
    camera_height=2.0,
    camera_distance=80.0,
    top=60.0,
    bottom=-8.0,
    right=50.0,
    left=-50.0,
):
    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    # gluPerspective(45, (display[0] / display[1]), 0.1, 150.0)

    glLoadIdentity()

    # Calculate aspect ratio
    # aspect_ratio = display[0] / display[1]

    # Define a perspective frustum with an asymmetric vertical offset
    near = 0.1
    far = 150.0
    factor = near / camera_distance
    top = top * factor
    bottom = bottom * factor
    right = right * factor
    left = -right

    # Set asymmetric frustum to shift the viewport downward
    glFrustum(left, right, bottom, top, near, far)

    glMatrixMode(GL_MODELVIEW)
    # camera position, look at position, up direction
    gluLookAt(
        0.0, camera_height, -camera_distance, 0.0, camera_height, 0.0, 0.0, 1.0, 0.0
    )

    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set up light parameters
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))  # Light position
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Ambient light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1))  # Diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1))  # Specular light


def draw_box(size):
    """Draws a cube with proper lighting and shading."""
    half_size = size / 2.0

    # Define vertices for the cube
    vertices = [
        # Front face
        (-half_size, -half_size, half_size),
        (half_size, -half_size, half_size),
        (half_size, half_size, half_size),
        (-half_size, half_size, half_size),
        # Back face
        (-half_size, -half_size, -half_size),
        (half_size, -half_size, -half_size),
        (half_size, half_size, -half_size),
        (-half_size, half_size, -half_size),
    ]

    # Define normals for each face
    normals = [
        (0, 0, 1),  # Front
        (0, 0, -1),  # Back
        (-1, 0, 0),  # Left
        (1, 0, 0),  # Right
        (0, 1, 0),  # Top
        (0, -1, 0),  # Bottom
    ]

    # Define indices for the six cube faces
    faces = [
        (0, 1, 2, 3),  # Front
        (4, 5, 6, 7),  # Back
        (0, 4, 7, 3),  # Left
        (1, 5, 6, 2),  # Right
        (3, 2, 6, 7),  # Top
        (0, 1, 5, 4),  # Bottom
    ]

    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])  # Set the normal for the current face
        # glColor3fv(colors[i])    # Set the color for the current face (optional)
        for vertex in face:
            glVertex3fv(vertices[vertex])  # Pass each vertex
    glEnd()


def generate_grid_structure(floors=12, axes_x=7, axes_z=7, porosity=0.5):
    # floors = 12
    # axes_x = 7
    # axes_z = 7
    # Pre-generate the random grid structure for the building
    grid_structure = [
        [[random.random() < porosity for y in range(axes_z)] for x in range(axes_x)]
        for floor in range(floors)
    ]
    return grid_structure


def draw_scene(pos_x, pos_y, distance, grid_structure):
    # print(grid_structure)
    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background color to white

    # Draw the ground as a plane extending to the horizon
    glPushMatrix()
    glTranslatef(0, -1, 0)  # Lower the plane slightly below the boxes
    glMaterialfv(
        GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.95, 0.95, 0.95, 1)
    )  # Set color for the base
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)  # Normal pointing up
    plane_size = 10000
    glVertex3f(-plane_size, 0.0, -plane_size)  # Bottom left corner
    glVertex3f(-plane_size, 0.0, plane_size)  # Top left corner
    glVertex3f(plane_size, 0.0, plane_size)  # Top right corner
    glVertex3f(plane_size, 0.0, -plane_size)  # Bottom right corner
    glEnd()
    glPopMatrix()

    floors = len(grid_structure)
    axes_x = len(grid_structure[0])
    axes_z = len(grid_structure[0][0])

    axes_width = 3
    floor_height = 4

    building_height = floors * floor_height

    # Draw the building as a grid of cubes
    for floor in range(len(grid_structure)):
        for x in range(len(grid_structure[0])):
            for z in range(len(grid_structure[0][0])):
                if grid_structure[floor][x][z]:
                    glPushMatrix()
                    cube_x = pos_x + (x - axes_x / 2) * axes_width
                    cube_y = (floor * floor_height) + (floor_height / 2)
                    cube_z = (z - axes_z / 2) * axes_width
                    glTranslatef(cube_x, cube_y, cube_z)
                    glScalef(axes_width, floor_height, axes_width)
                    # Set color for the building
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 1, 1))
                    # glutSolidCube(1)  # Draw a unit cube scaled to the desired size
                    draw_box(1)
                    glPopMatrix()

    # Draw the frame (beams and columns)
    # Set color for the frame
    # glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.2, 0.2, 0.2, 1))
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 0.8, 0.0, 1))
    frame_d = 0.5
    for x in range(axes_x + 1):
        for z in range(axes_z + 1):
            # Draw vertical columns
            glPushMatrix()
            column_x = pos_x + (x - axes_x / 2) * axes_width - axes_width / 2
            column_y = building_height / 2
            column_z = (z - axes_z / 2) * axes_width - axes_width / 2
            # Translate to the desired position
            glTranslatef(column_x, column_y, column_z)
            # Scale to the desired dimensions
            glScalef(frame_d, building_height, frame_d)
            # glutSolidCube(1)  # Draw a unit cube scaled to the desired size
            draw_box(1)
            glPopMatrix()

    # Draw horizontal beams at each floor level
    for floor in range(1, floors + 1):
        for z in range(axes_z + 1):
            glPushMatrix()
            beam_x = pos_x - axes_width / 2
            beam_y = floor * floor_height
            beam_z = (z - axes_z / 2) * axes_width - axes_width / 2
            # Translate to the desired position
            glTranslatef(beam_x, beam_y, beam_z)
            # Scale to the desired dimensions
            glScalef(axes_x * axes_width + frame_d, frame_d, frame_d)
            # glutSolidCube(1)  # Draw a unit cube scaled to the desired size
            draw_box(1)
            glPopMatrix()
        for x in range(axes_x + 1):
            glPushMatrix()
            beam_x = pos_x + (x - axes_x / 2) * axes_width - axes_width / 2
            beam_y = floor * floor_height
            beam_z = -axes_width / 2
            # Translate to the desired position
            glTranslatef(beam_x, beam_y, beam_z)
            # Scale to the desired dimensions
            glScalef(frame_d, frame_d, axes_z * axes_width + frame_d)
            # glutSolidCube(1)
            draw_box(1)
            glPopMatrix()

    # Draw the second box the cafe
    threshold = 10
    cafe_y = max(0, min(pos_y, (floors - 1) * floor_height))

    # Set cafe height in number of floors (1 or 2)
    cafe_floors = 2 if distance > threshold else 1
    if cafe_floors == 2:
        cafe_y = (cafe_y // floor_height) * floor_height  # Align to full floor height
    else:
        cafe_y = (
            floor_height / 2 + (cafe_y // floor_height) * floor_height
        )  # Align to half floor height

    # Create the Cafe
    cafe_height = cafe_floors * 4
    # Restrict cafe width to a maximum value and ensure it is not smaller than axes_width
    max_cafe_width = 4.5 * axes_width
    cafe_width = max(axes_width, min(distance, max_cafe_width))
    glPushMatrix()
    # Translate to the desired position
    glTranslatef(pos_x + 1 * axes_width, cafe_y, -(axes_z - 3.5) * axes_width)
    # Scale to the desired dimensions
    glScalef(cafe_width, cafe_height, axes_width * 2.5)
    # Set color for the cafe
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.3, 0.3, 0.8, 1))
    # glutSolidCube(1)  # Draw a unit cube scaled to the desired size
    draw_box(1)
    glPopMatrix()


def save_screenshot(display, filename="dummy_screenshot.png"):
    """Save a screenshot of the current OpenGL buffer."""
    width, height = display
    # Read the pixels from the frame buffer
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    # Create a Pygame surface from the pixel data
    image = pygame.image.fromstring(data, (width, height), "RGBA", True)
    # Flip the image vertically to correct orientation
    image = pygame.transform.flip(image, False, False)
    # Save the image as a PNG file
    pygame.image.save(image, filename)
    print(f"Screenshot saved as {filename}")

def load_texture(image_path):
    """Load an image and convert it to a texture."""
    image = pygame.image.load(image_path)
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


def draw_overlay(texture_id, tex_width, tex_height, display_size):
    """Draw the overlay image, maintaining aspect ratio."""

    # Calculate aspect ratio to maintain proportions
    display_width, display_height = display_size
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

    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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