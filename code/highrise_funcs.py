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


def draw_box(size: float):
    """Draw a lit cube of side 'size'."""
    half = size / 2.0
    # 8 corners
    verts = [
        (-half, -half, half),
        (half, -half, half),
        (half, half, half),
        (-half, half, half),
        (-half, -half, -half),
        (half, -half, -half),
        (half, half, -half),
        (-half, half, -half),
    ]
    # Face indices
    faces = [
        (0, 1, 2, 3),  # front
        (5, 4, 7, 6),  # back
        (4, 0, 3, 7),  # left
        (1, 5, 6, 2),  # right
        (3, 2, 6, 7),  # top
        (4, 5, 1, 0),  # bottom
    ]
    # Normals
    normals = [(0, 0, 1), (0, 0, -1), (-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)]

    # Draw
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])
        for vi in face:
            glVertex3fv(verts[vi])
    glEnd()


def generate_grid_structure(floors=12, max_axes_x=30, max_axes_z=30, porosity=0.5):
    # floors = 12
    # axes_x = 7
    # axes_z = 7
    # Pre-generate the random grid structure for the building
    grid_structure = [
        [[random.random() < porosity for y in range(max_axes_z)] for x in range(max_axes_x)]
        for floor in range(floors)
    ]
    return grid_structure


def draw_building_structure(grid, axes_width, floors, axes_x, axes_z):
    """
    Draw the building as a collection of white cubes + frame,
    centered at x=0, z=0.
    """
    floor_height = 4.0

    # Because building is centered, we offset everything by half the building extents.
    half_w_x = axes_x * axes_width / 2.0
    half_w_z = axes_z * axes_width / 2.0

    # Draw each occupied cell
    for floor_i in range(floors):
        for x_i in range(axes_x):
            for z_i in range(axes_z):
                if grid[floor_i][x_i][z_i]:
                    glPushMatrix()
                    # center of that cell
                    world_x = (x_i * axes_width) - half_w_x + axes_width * 0.5
                    world_y = floor_i * floor_height + floor_height * 0.5
                    world_z = (z_i * axes_width) - half_w_z + axes_width * 0.5
                    glTranslatef(world_x, world_y, world_z)
                    glScalef(axes_width, floor_height, axes_width)
                    # white color
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 1, 1))
                    draw_box(1.0)
                    glPopMatrix()

    # Draw the frame (columns/beams)
    # Columns at each grid intersection
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.8, 0.0, 1.0))
    frame_d = 0.5
    building_height = floors * floor_height

    for x_i in range(axes_x + 1):
        for z_i in range(axes_z + 1):
            glPushMatrix()
            col_x = (x_i * axes_width) - half_w_x
            col_y = building_height * 0.5
            col_z = (z_i * axes_width) - half_w_z
            glTranslatef(col_x, col_y, col_z)
            glScalef(frame_d, building_height, frame_d)
            draw_box(1.0)
            glPopMatrix()

    # Horizontal beams at each floor
    for floor_i in range(1, floors + 1):
        y_level = floor_i * floor_height
        # beam in x-direction
        for z_i in range(axes_z + 1):
            glPushMatrix()
            # left edge is -half_w_x, so total width in x is axes_x*axes_width
            beam_x = -half_w_x + (axes_x * axes_width) / 2.0
            beam_y = y_level
            beam_z = (z_i * axes_width) - half_w_z
            glTranslatef(beam_x, beam_y, beam_z)
            glScalef(axes_x * axes_width + frame_d, frame_d, frame_d)
            draw_box(1.0)
            glPopMatrix()

        # beam in z-direction
        for x_i in range(axes_x + 1):
            glPushMatrix()
            beam_x = (x_i * axes_width) - half_w_x
            beam_y = y_level
            beam_z = -half_w_z + (axes_z * axes_width) / 2.0
            glTranslatef(beam_x, beam_y, beam_z)
            glScalef(frame_d, frame_d, axes_z * axes_width + frame_d)
            draw_box(1.0)
            glPopMatrix()


def draw_scene(x, y, size, axes_width, grid, floors):
    """
    Clear screen, then draw building (aligned by closest-to-camera facade) plus a moving "cafe" box at (x,y,0)
    """
    # Clear
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    # Force a white background
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Decide how many axes we have, to keep total width ~ 45
    target_width = 21.0  # 45.0
    axes_x = max(1, round(target_width / axes_width))
    axes_z = axes_x  # keep symmetrical

    # Adjust building position to align its closest-to-camera facade
    building_x_offset = 0  # Adjust if needed
    # building_z_offset = -(axes_z - 3.5) * axes_width  # Align closest facade
    # Choose a constant depth for the building's front facade.
    # desired_front_z = -15.0  # Adjust this value as needed
    # building_z_offset = desired_front_z + (axes_z * axes_width / 2.0)
    desired_front_z = -15.0
    building_depth = axes_z * axes_width
    building_z_offset = desired_front_z + building_depth / 2.0

    # Draw ground plane
    glPushMatrix()
    glTranslatef(0, -1, 0)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.95, 0.95, 0.95, 1.0))
    plane_size = 1000.0
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-plane_size, 0, -plane_size)
    glVertex3f(-plane_size, 0, plane_size)
    glVertex3f(plane_size, 0, plane_size)
    glVertex3f(plane_size, 0, -plane_size)
    glEnd()
    glPopMatrix()

    # Draw building with given axes_width, axes_x, axes_z, adjusting its position
    glPushMatrix()
    glTranslatef(building_x_offset, 0, building_z_offset)
    draw_building_structure(grid, axes_width, floors, axes_x, axes_z)
    glPopMatrix()

    # Adjust cafe position to align its left-bottom-closest-to-camera corner
    # Decide how far the cafe should protrude from the building
    cafe_protrusion = 2.0  # how many meters forward from the front face
    cafe_front_z = desired_front_z - cafe_protrusion

    adjusted_x = x + size / 2.0
    adjusted_y = y + size / 2.0
    # Then later, instead of adjusted_z = building_z_offset + size/2.0 - 12:
    cafe_min_z = cafe_front_z
    cafe_center_z = cafe_min_z + (size / 2.0)
    adjusted_z = cafe_center_z
    # adjusted_z = building_z_offset + size / 2.0 - 12

    cafe_size = size
    cafe_height = min(size, 10)
    # The blue cafe box is drawn with center at (0,0,0) after translation+scaling,
    # so its world extents are:
    cafe_min_x = adjusted_x - cafe_size / 2
    cafe_max_x = adjusted_x + cafe_size / 2
    cafe_min_y = adjusted_y - cafe_height / 2
    cafe_max_y = adjusted_y + cafe_height / 2
    cafe_min_z = adjusted_z - cafe_size / 2
    cafe_max_z = adjusted_z + cafe_size / 2

    # Now draw the "blue cafe" box
    glPushMatrix()
    glTranslatef(adjusted_x, adjusted_y, adjusted_z)
    glScalef(size, min(size, 10), size)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.3, 0.3, 0.8, 1.0))
    draw_box(1.0)
    glPopMatrix()

    # Now draw the yellow frame around the cafe.
    frame_d = 0.5
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.8, 0.0, 1.0))

    # Draw vertical columns at the four corners.
    for cx in [cafe_min_x, cafe_max_x]:
        for cz in [cafe_min_z, cafe_max_z]:
            glPushMatrix()
            # Place the column so its center is midway vertically.
            glTranslatef(cx, (cafe_min_y + cafe_max_y) / 2.0, cz)
            glScalef(frame_d, cafe_height, frame_d)
            draw_box(1.0)
            glPopMatrix()

    # Draw horizontal beams along the x-direction (front and back edges) at top and bottom.
    for y_level in [cafe_min_y, cafe_max_y]:
        for z_coord in [cafe_min_z, cafe_max_z]:
            glPushMatrix()
            # Center along x is the middle of the cafe box.
            glTranslatef((cafe_min_x + cafe_max_x) / 2.0, y_level, z_coord)
            glScalef(cafe_size + frame_d, frame_d, frame_d)
            draw_box(1.0)
            glPopMatrix()

    # Draw horizontal beams along the z-direction (left and right edges) at top and bottom.
    for y_level in [cafe_min_y, cafe_max_y]:
        for x_coord in [cafe_min_x, cafe_max_x]:
            glPushMatrix()
            glTranslatef(x_coord, y_level, (cafe_min_z + cafe_max_z) / 2.0)
            glScalef(frame_d, frame_d, cafe_size + frame_d)
            draw_box(1.0)
            glPopMatrix()


def draw_scene_old(pos_x, pos_y, distance, grid_structure):
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
