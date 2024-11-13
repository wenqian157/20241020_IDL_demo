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


if __name__ == "__main__":

    # fixed plane
    plane_point = np.array([0, 0, 2.7])
    plane_normal = np.array([0, 0, 1])
    
    # replace with traced rigid body position
    ray_origin = np.array([0, 0, 0])
    ray_end = np.array([1, 2, 1])
    ray_direction = ray_end - ray_origin
    

    pt = ray_plane_intersection(
        ray_origin, ray_direction, plane_point, plane_normal
    )
    print(pt)

    # fixed dome in the space
    dome_center = np.array([0, 0, 0])              
    dome_radius = 5.0                             
    dome_up_direction = np.array([0, 1, 0])  

    # replace with traced rigid body 
    ray_origin = np.array([0, 0, 0])
    ray_end = np.array([1, 2, 0])            
    ray_direction = ray_end - ray_origin         

    intersection = ray_dome_intersection(ray_origin, ray_direction, dome_center, dome_radius, dome_up_direction)
    # print("Intersection Point:", intersection)
