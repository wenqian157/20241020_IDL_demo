import numpy as np

def screen_boundary(w, h):
    # x boundary -4 ~ 4
    # y boundary 0 ~ 5
    if w > 4:
        w = 4
    elif w < -4:
        w = -4
    if h > 5:
        h = 5
    elif h < 0:
        h = 0
    return [w, h]

def project_pt_2_screen(point_3d):
    w = point_3d[0]
    h = point_3d[1]
    w, h = screen_boundary(w, h)
    return [w, h]

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
    projected_point = project_pt_2_screen(intersection_point)
    
    return projected_point

def ray_sphere_intersection(ray_origin, ray_direction, sphere_center, sphere_radius):
    # Vector from the ray origin to the sphere center
    oc = ray_origin - sphere_center

    # Quadratic coefficients
    a = np.dot(ray_direction, ray_direction)
    b = 2.0 * np.dot(oc, ray_direction)
    c = np.dot(oc, oc) - sphere_radius**2

    # Discriminant
    discriminant = b**2 - 4 * a * c

    # Check if there are real roots (intersection exists)
    if discriminant < 0:
        return None  # No intersection

    # Compute the two intersection points (t1 and t2)
    t1 = (-b - np.sqrt(discriminant)) / (2 * a)
    t2 = (-b + np.sqrt(discriminant)) / (2 * a)

    # Return the nearest positive intersection point
    if t1 >= 0 and t2 >= 0:
        return ray_origin + min(t1, t2) * ray_direction
    elif t1 >= 0:
        return ray_origin + t1 * ray_direction
    elif t2 >= 0:
        return ray_origin + t2 * ray_direction
    else:
        return None  # Intersection is behind the ray origin

def ray_dome_intersection(ray_origin, ray_direction, dome_center, dome_radius, dome_up_direction):
    ray_direction = ray_direction / np.linalg.norm(ray_direction)

    # Find intersection with the full sphere
    intersection_point = ray_sphere_intersection(ray_origin, ray_direction, dome_center, dome_radius)
    if intersection_point is None:
        return None  # No intersection with the sphere

    # Check if the intersection point is within the hemisphere
    to_point = intersection_point - dome_center
    if np.dot(to_point, dome_up_direction) >= 0:
        return intersection_point  # Intersection within the dome's hemisphere
    else:
        return None  # Intersection is in the opposite hemisphere

def process_tracked_poses(rigid_body_0, rigid_body_1):
    # create ray from trakced 2 poses
    ray_origin = np.array([rigid_body_0.pos[0], rigid_body_0.pos[1], rigid_body_0.pos[2]])
    ray_end = np.array([rigid_body_1.pos[0], rigid_body_1.pos[1], rigid_body_1.pos[2]])
    ray_direction = ray_origin - ray_end
    distance = np.linalg.norm(ray_end - ray_origin)

    # intersect with screen
    # fixed plane
    plane_point = np.array([0, 0, 2.7])
    plane_normal = np.array([0, 0, 1])
    
    pt_screen = ray_plane_intersection(
        ray_origin, ray_direction, plane_point, plane_normal
    )

    # intersect with dome
    # fixed dome in the space
    dome_center = np.array([0, 0, 0])              
    dome_radius = 4.0                             
    dome_up_direction = np.array([0, 1, 0])

    pt_dome = ray_dome_intersection(
        ray_origin, ray_direction, dome_center, dome_radius, dome_up_direction
        )
    
    return pt_screen, pt_dome, distance

def map_point_2_holophonix(x, y, z):
    x = -x
    y = z
    z = y
    return x, y, z

def map_range(value, old_min, old_max, new_min, new_max):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def map_point_2_pygame_window(x, y):
    window_size = (1280, 800)
    x = map_range(x, 4, -4, 0, window_size[0])
    y = map_range(y, 5, 0, 0, window_size[1])
    return x, y