import numpy as np


def ray_plane_intersection(ray_start, ray_end, plane_point, plane_normal):
    #normalize
    ray_direction = ray_end - ray_start
    ray_direction = ray_direction / np.linalg.norm(ray_direction)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)

    # calculate dot product 
    dot_product = np.dot(ray_direction, plane_normal)
    if np.isclose(dot_product, 0):
        return None
    
    # caldulate parameter t
    t = np.dot(plane_point - ray_start, plane_normal) / dot_product
    if t < 0:
        return None
    
    #calculate thte intersection point
    intersection_point = ray_start + ray_direction
    
    return intersection_point


if __name__ == "__main__":

    ray_start = np.array([0, 0, 0])
    ray_end = np.array([0, 0, 1])
    plane_point = np.array([0, 0, 5])
    plane_normal = np.array([0, 0, 1])
    