import numpy as np

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

# Example Usage
ray_origin = np.array([0, 0, 0])            # Ray starting point
ray_direction = np.array([0, 1, 0])            # Ray direction (should be normalized)
dome_center = np.array([0, 0, 0])              # Center of the dome
dome_radius = 5.0                              # Radius of the dome
dome_up_direction = np.array([0, 1, 0])        # The "up" direction of the dome's open side

# Normalize the ray direction
ray_direction = ray_direction / np.linalg.norm(ray_direction)

intersection = ray_dome_intersection(ray_origin, ray_direction, dome_center, dome_radius, dome_up_direction)
print("Intersection Point:", intersection)
