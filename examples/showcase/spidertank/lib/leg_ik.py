# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import math
from collections import namedtuple

Limits = namedtuple("Limits", ("min", "max"))


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, vector):
        return Vector3(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    def __sub__(self, vector):
        return Vector3(self.x - vector.x, self.y - vector.y, self.z - vector.z)


def clamp(value, limits):
    if value > limits.max:
        return limits.max
    if value < limits.min:
        return limits.min
    return value


def rotate_y(vector, angle):
    # Rotate the vector by the specified angle
    angle_rad = math.radians(angle)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)

    newX = (cos_angle * vector.x) + (sin_angle * vector.z)
    newZ = (cos_angle * vector.z) - (sin_angle * vector.x)

    return Vector3(newX, vector.y, newZ)


def heading_of(vector):
    return math.degrees(math.atan2(vector.x, vector.z))


def inclination_of(vector):
    return math.degrees(math.atan2(vector.y, vector.z))


def vertical_magnitude_of(vector):
    return math.sqrt(vector.y * vector.y + vector.z * vector.z)


def calculate_ik_3dof(origin_to_target, coxa_length, femur_length, tibia_length,
                      coxa_limits, femur_limits, tibia_limits):
    coxa_angle = heading_of(origin_to_target)
    coxa_angle = clamp(coxa_angle, coxa_limits)

    femur_to_target = rotate_y(origin_to_target, -coxa_angle)
    femur_to_target.z -= coxa_length

    femur_angle, tibia_angle = calculate_ik_vertical_2dof(femur_to_target, femur_length, tibia_length,
                                                          femur_limits, tibia_limits)

    return coxa_angle, femur_angle, tibia_angle


def calculate_ik_vertical_2dof(femur_to_target, femur_length, tibia_length,
                               femur_limits, tibia_limits):
    # Useful links
    # https://www.calculator.net/triangle-calculator.html
    # https://www.mathsisfun.com/algebra/trig-solving-sas-triangles.html

    femur_inclination = inclination_of(femur_to_target)
    femur_to_target_length = vertical_magnitude_of(femur_to_target)

    femur_sqr_length = femur_length * femur_length
    tibia_sqr_length = tibia_length * tibia_length
    femur_to_target_sqr_length = femur_to_target_length * femur_to_target_length

    # Is the target not too far?
    if femur_length + tibia_length > femur_to_target_length:
        # Is the target not too close?
        if femur_to_target_length > abs(femur_length - tibia_length):
            # Calculate the femur elevation and tibia angle using the Laws of Cosine
            femur_elevation = math.degrees(math.acos((femur_sqr_length + femur_to_target_sqr_length - tibia_sqr_length) / (2 * femur_length * femur_to_target_length)))
            tibia_angle = math.degrees(math.acos((femur_sqr_length + tibia_sqr_length - femur_to_target_sqr_length) / (2 * femur_length * tibia_length)))
        else:
            # The target is too near, so fully contract the leg
            femur_elevation = 0.0
            tibia_angle = 0.0
    else:
        # Target is too far, so fully extend the leg
        femur_elevation = 0.0
        tibia_angle = 180.0

    # Is the tibia angle outside the allowed range?
    if tibia_angle < tibia_limits.min or tibia_angle > tibia_limits.max:

        tibia_angle = clamp(tibia_angle, tibia_limits)   # Clamp the angle

        # Recalculate the femur elevation, to remain close to the target
        clamped_femur_to_target = math.sqrt(femur_sqr_length + tibia_sqr_length - (2 * femur_length * tibia_length * math.cos(math.radians(tibia_angle))))
        femur_elevation = math.degrees(math.asin((tibia_length * math.sin(math.radians(tibia_angle))) / clamped_femur_to_target))

    # Calculate the femur angle
    femur_angle = femur_inclination + femur_elevation

    # If the femur angle outside the allowed range?
    if femur_angle < femur_limits.min or femur_angle > femur_limits.max:
        # If the femur angle above the allowed range?
        if femur_angle > femur_limits.max:
            # Modify the femur elevation and clamp the angle
            femur_elevation -= femur_angle - femur_limits.max
            femur_angle = femur_limits.max

        # If the femur angle below the allowed range?
        elif femur_angle < femur_limits.min:
            # Modify the femur elevation and clamp the angle
            femur_elevation -= femur_angle - femur_limits.min
            femur_angle = femur_limits.min

        # Recalculate the tibia angle, to remain close to the target
        tibia_to_target = math.sqrt(femur_sqr_length + femur_to_target_sqr_length - (2 * femur_length * femur_to_target_length * math.cos(math.radians(femur_elevation))))
        tibia_angle = math.degrees(math.acos((femur_sqr_length + (tibia_to_target * tibia_to_target) - femur_to_target_sqr_length) / (2 * femur_length * tibia_to_target)))

        # Invert and wrap the tibia angle if the femur elevation became negative
        if femur_elevation < 0.0:
            tibia_angle = 360.0 - tibia_angle

    # Reclamp the tibia angle
    tibia_angle = clamp(tibia_angle, tibia_limits)

    # print(str(femur_inclination) + ", " + str(femur_elevation) + ", " + str(tibia_angle))

    return femur_angle, tibia_angle
