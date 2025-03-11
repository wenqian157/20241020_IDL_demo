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


def draw_box_with_frame(
    cx,
    cy,
    cz,
    sx,
    sy,
    sz,
    body_color=(1.0, 1.0, 1.0, 1.0),
    frame_color=(1.0, 1.0, 1.0, 1.0),
    frame_thickness=0.5,
):
    """
    Draws a solid box (centered at cx,cy,cz) of size (sx, sy, sz)
    with a frame around it.
    """
    # Compute bounding box corners
    min_x = cx - sx / 2
    max_x = cx + sx / 2
    min_y = cy - sy / 2
    max_y = cy + sy / 2
    min_z = cz - sz / 2
    max_z = cz + sz / 2

    # 1. Draw solid box
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glScalef(sx, sy, sz)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, body_color)
    draw_box(1.0)  # Assumes a draw_box function is defined elsewhere
    glPopMatrix()

    # 2. Draw frame
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, frame_color)

    # Vertical columns at corners
    for corner_x in [min_x, max_x]:
        for corner_z in [min_z, max_z]:
            glPushMatrix()
            glTranslatef(corner_x, (min_y + max_y) / 2.0, corner_z)
            glScalef(frame_thickness, sy, frame_thickness)
            draw_box(1.0)
            glPopMatrix()

    # Horizontal beams (x-direction) at top & bottom
    for y_level in [min_y, max_y]:
        for z_coord in [min_z, max_z]:
            glPushMatrix()
            glTranslatef((min_x + max_x) / 2.0, y_level, z_coord)
            glScalef(sx + frame_thickness, frame_thickness, frame_thickness)
            draw_box(1.0)
            glPopMatrix()

    # Horizontal beams (z-direction) at top & bottom
    for y_level in [min_y, max_y]:
        for x_coord in [min_x, max_x]:
            glPushMatrix()
            glTranslatef(x_coord, y_level, (min_z + max_z) / 2.0)
            glScalef(frame_thickness, frame_thickness, sz + frame_thickness)
            draw_box(1.0)
            glPopMatrix()


def generate_grid_structure(floors=12, max_axes_x=30, max_axes_z=30, porosity=0.5):
    # floors = 12
    # axes_x = 7
    # axes_z = 7
    # Pre-generate the random grid structure for the building
    grid_structure = [
        [
            [random.random() < porosity for y in range(max_axes_z)]
            for x in range(max_axes_x)
        ]
        for floor in range(floors)
    ]
    return grid_structure


def draw_building_structure(grid, axes_width, floors, axes_x, axes_z, floor_height = 4.0):
    """
    Draws the building as a collection of white cubes plus a frame,
    centered at x=0, z=0.
    """
    

    # Because building is centered, we offset everything by half the building extents.
    half_w_x = axes_x * axes_width / 2.0
    half_w_z = axes_z * axes_width / 2.0

    # 1. Draw each occupied cell
    for floor_i in range(floors):
        for x_i in range(axes_x):
            for z_i in range(axes_z):
                if grid[floor_i][x_i][z_i]:
                    glPushMatrix()
                    # Center of that cell
                    world_x = (x_i * axes_width) - half_w_x + axes_width * 0.5
                    world_y = floor_i * floor_height + floor_height * 0.5
                    world_z = (z_i * axes_width) - half_w_z + axes_width * 0.5
                    glTranslatef(world_x, world_y, world_z)
                    glScalef(axes_width, floor_height, axes_width)
                    # White color
                    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 1, 1, 1))
                    draw_box(1.0)
                    glPopMatrix()

    # 2. Draw the frame (columns and beams)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.8, 0.0, 1.0))
    frame_d = 0.5
    building_height = floors * floor_height

    # Columns at each grid intersection
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
        # Beams along x-direction
        for z_i in range(axes_z + 1):
            glPushMatrix()
            beam_x = -half_w_x + (axes_x * axes_width) / 2.0
            beam_y = y_level
            beam_z = (z_i * axes_width) - half_w_z
            glTranslatef(beam_x, beam_y, beam_z)
            glScalef(axes_x * axes_width + frame_d, frame_d, frame_d)
            draw_box(1.0)
            glPopMatrix()

        # Beams along z-direction
        for x_i in range(axes_x + 1):
            glPushMatrix()
            beam_x = (x_i * axes_width) - half_w_x
            beam_y = y_level
            beam_z = -half_w_z + (axes_z * axes_width) / 2.0
            glTranslatef(beam_x, beam_y, beam_z)
            glScalef(frame_d, frame_d, axes_z * axes_width + frame_d)
            draw_box(1.0)
            glPopMatrix()


def draw_cafe(cx, cy, cz, size):
    """
    Draws the café by calling 'draw_box_with_frame' with typical café dimensions
    (square footprint = size x size, height = min(size, 10)).
    """
    cafe_size = size
    cafe_height = min(size, 10)

    body_color = (0.3, 0.3, 0.8, 1.0)  # Blue
    frame_color = (1.0, 0.8, 0.0, 1.0)  # Yellow
    frame_d = 0.5

    draw_box_with_frame(
        cx,
        cy,
        cz,
        cafe_size,
        cafe_height,
        cafe_size,
        body_color=body_color,
        frame_color=frame_color,
        frame_thickness=frame_d,
    )


def draw_scene(x, y, size, axes_width, grid, floors, floor_height = 4.0):
    """
    Clears screen, sets up camera, draws ground plane,
    then draws the building plus a moving 'café' box.
    """
    # 1. Clear/initialize
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # 2. Decide how many axes in building to keep total width ~21
    target_width = 21.0
    axes_x = max(1, round(target_width / axes_width))
    axes_z = axes_x  # keep symmetrical

    # 3. Compute building offsets
    desired_front_z = -15.0
    building_depth = axes_z * axes_width
    building_z_offset = desired_front_z + building_depth / 2.0
    building_x_offset = 0.0

    # 4. Draw ground plane
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

    # 5. Draw building
    glPushMatrix()
    glTranslatef(building_x_offset, 0, building_z_offset)
    draw_building_structure(grid, axes_width, floors, axes_x, axes_z)
    glPopMatrix()

    # 6. Compute café position (just an example offset relative to building)
    cafe_protrusion = 2.0
    cafe_front_z = desired_front_z - cafe_protrusion
    # Shift x, y so the café's lower-left corner is at (x,y)
    adjusted_cx = x + size / 2.0
    adjusted_cy = y + size / 2.0
    # Front face goes at cafe_front_z, so center is half 'size' behind that
    adjusted_cz = cafe_front_z + size / 2.0

    # 7. Draw café
    draw_cafe(adjusted_cx, adjusted_cy, adjusted_cz, size)


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
