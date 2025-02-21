#!/usr/bin/env python3

"""
Single-file example using PyOpenGL + pygame to animate a highrise building.
It uses keyframed states (x, y, size, axes_width) with ease-in/ease-out.
The building stays centered; only the blue "glass box" cafe moves.
"""

import math
import random
import os
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from highrise_funcs import (
    # draw_scene,
    # generate_grid_structure,
    # save_screenshot,
    setup_projection_and_lighting,
)

# -----------------------------------------------------------
# Utility / drawing code
# -----------------------------------------------------------


def ease_in_out_quad(t: float) -> float:
    """
    Standard easeInOutQuad function.
    t is in [0,1], returns adjusted t with smooth acceleration.
    """
    if t < 0.5:
        return 2.0 * t * t
    else:
        return -1.0 + (4.0 - 2.0 * t) * t


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


def save_screenshot(display_size, filename="frame.png"):
    """Save the current OpenGL framebuffer as a PNG screenshot."""
    width, height = display_size
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    pixels = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    surf = pygame.image.fromstring(pixels, (width, height), "RGBA", True)
    # Flip vertical if needed
    surf = pygame.transform.flip(surf, False, False)
    pygame.image.save(surf, filename)


def generate_grid_structure(floors, max_axes_x, max_axes_z, porosity=0.5):
    """
    Generate a random True/False 3D array for floors x axes_x x axes_z,
    up to a maximum dimension. We'll fill everything with random.
    """
    return [
        [
            [random.random() < porosity for _ in range(max_axes_z)]
            for _ in range(max_axes_x)
        ]
        for _ in range(floors)
    ]


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
    cafe_height = min(size,10)
    # The blue cafe box is drawn with center at (0,0,0) after translation+scaling,
    # so its world extents are:
    cafe_min_x = adjusted_x - cafe_size/2
    cafe_max_x = adjusted_x + cafe_size/2
    cafe_min_y = adjusted_y - cafe_height/2
    cafe_max_y = adjusted_y + cafe_height/2
    cafe_min_z = adjusted_z - cafe_size/2
    cafe_max_z = adjusted_z + cafe_size/2

    # Now draw the "blue cafe" box
    glPushMatrix()
    glTranslatef(adjusted_x, adjusted_y, adjusted_z)
    glScalef(size, min(size,10), size)
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


def interpolate_keyframes(frame, total_frames, states):
    """
    We have a list of keyframe states, each a list [x, y, size, axes_width].
    We'll loop from 0->1->2->...->(n-1)->0 over total_frames with ease-in/out.
    """
    n = len(states)
    # how many transitions? = n
    frames_per_segment = total_frames // n
    seg_i = frame // frames_per_segment  # which segment
    seg_i_next = (seg_i + 1) % n

    # local t in [0,1]
    seg_start_frame = seg_i * frames_per_segment
    seg_end_frame = seg_start_frame + frames_per_segment
    if seg_end_frame > total_frames:
        seg_end_frame = total_frames
    seg_local = float(frame - seg_start_frame) / float(frames_per_segment)
    if seg_local < 0:
        seg_local = 0.0
    if seg_local > 1:
        seg_local = 1.0

    t_eased = ease_in_out_quad(seg_local)

    s0 = states[seg_i]
    s1 = states[seg_i_next]

    # param wise interpolation
    out = []
    for i in range(len(s0)):
        val0 = s0[i]
        val1 = s1[i]
        val = val0 + (val1 - val0) * t_eased
        out.append(val)

    return out  # [x, y, size, axes_width]


def main():
    pygame.init()
    window_scale = 0.75
    screen_width, screen_height = 2560, 1600
    disp_w, disp_h = int(screen_width * window_scale), int(screen_height * window_scale)
    display = (disp_w, disp_h)
    pygame.display.set_caption("GenAI_render_Animation")

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    setup_projection_and_lighting()
    # Force a white background
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Pre-generate a big grid so we can handle up to e.g. 30 axes
    floors = 12
    max_axes = 30
    random.seed(42)
    grid = generate_grid_structure(floors, max_axes, max_axes, porosity=0.5)

    # Let's define our keyframe states: [x, y, size, axes_width]
    # We'll do 4 states, total 600 frames, so 4 segments of 150 frames each.
    states_v1 = [
        # near left, small cafe, building axes=3 
        [-13.0, 0.0, 5.0, 3.0],
        # further right, bigger cafe, same axes_width=3
        [2.0, 22.0, 12.0, 10.0],
        # center, medium cafe, building axes_width=1.5 => ~30 wide
        [-10, 30.0, 20.0, 2],
        # left, small cafe, building axes_width=5 
        [-5.0, 20.0, 5.0, 5.0],
    ]
    states_v2 = [
        
        # left, small cafe, building axes_width=5 
        [0.0, 8.0, 5.0, 5.0],
        # further right, bigger cafe, same axes_width=3
        [-13.0, 22.0, 12.0, 10.0],
        # center, medium cafe, building axes_width=1.5 => ~30 wide
        [-10, 30.0, 20.0, 2],
        # near left, small cafe, building axes=3 
        [8.0, 0.0, 4.0, 3.0],
    ]
    states = states_v2
    total_frames = 600

    frame = 0
    clock = pygame.time.Clock()
    running = True

    # Make a folder for screenshots if you want
    out_dir = "screenshots"
    os.makedirs(out_dir, exist_ok=True)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
        print(f"Frame {frame:03d} / {total_frames}")
        

        # compute interpolated parameters
        x, y, cafe_size, axes_w = interpolate_keyframes(frame, total_frames, states)
        print(
            f"Frame {frame:03d}: x={x:.2f}, y={y:.2f}, size={cafe_size:.2f}, axes_w={axes_w:.2f}"
        )

        # draw
        draw_scene(x, y, cafe_size, axes_w, grid, floors)
        

        # optionally save screenshot
        fname = os.path.join(out_dir, f"frame_{frame:03d}.png")
        save_screenshot((disp_w, disp_h), fname)

        pygame.display.flip()

        frame += 1
        if frame == total_frames:
            # loop forever or just exit?
            running = False
            # Let's just loop around.
            # frame = 0

    pygame.quit()


if __name__ == "__main__":
    main()
