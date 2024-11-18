from NatNetClient import NatNetClient
import numpy as np
from pythonosc import udp_client
import socket
import struct


def ray_plane_intersection(ray_origin, ray_direction, plane_point, plane_normal):
    #normalize
    ray_direction = ray_direction / np.linalg.norm(ray_direction)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)

    # calculate dot product 
    dot_product = np.dot(ray_direction, plane_normal)
    if np.isclose(dot_product, 0):
        return None
    
    # caldulate parameter t
    t = np.dot(plane_point - ray_origin, plane_normal) / dot_product
    if t < 0:
        return None
    
    #calculate thte intersection point
    intersection_point = ray_origin + t * ray_direction
    
    return intersection_point

plane_point = np.array([0, 0, 2.7])
plane_normal = np.array([0, 0, 1])

ray_origin = np.array([-4, 1, 0])
ray_end = np.array([-4, 1.2, -0.2])
ray_direction = ray_origin - ray_end

pt_intersection = ray_plane_intersection(ray_origin, ray_direction, plane_point, plane_normal)
print(pt_intersection)