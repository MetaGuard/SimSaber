# As of this commit, a lot needs to change in this code. A lot of
# function and variable definitions are incorrect or not filled in.
# Also, special care should be taken to cast between C# floats and doubles
# (in numpy 'single' and 'double') in the same way that the source does.

from typeDefs import *
from typing import *
from math import cos, sin, pi as π
from numpy import single
from Geometry import Vector3, Quaternion


def lerp_unclamped(a, b, t):
    return a + (b - a) * t


def lerp(a, b, t):
    if t < 0:
        t = 0
    if t > 1:
        t = 1
    return a + (b - a) * t


def quadratic_in_out(t):
    if t < 0.5:
        return 2 * t * t
    return (4 - 2 * t) * t - 1


def move_towards_head(a, b, q, t):
    return a


def quat_slerp(p, q, t):
    return lerp(p, q, t)   # This is incorrect


def look_rotation(forwards, up):
    return Quaternion(0, 0, 0, 1)


def create_note_position_function(map: Map, note: Note):
    note_time = note.time * map.beatsPerMinute
    floor_movement_start_pos = Vector3(0, 0, 0)  # ###
    floor_movement_end_pos = Vector3(1, 2, 3)  # ###
    jump_end_pos = Vector3(2, 0, 0)  # ###
    gravity = 9.8  # ###
    jump_duration = 1  # ###
    move_duration = 1  # ###
    movement_start_time = note_time - move_duration - jump_duration / 2
    jump_start_time = note_time - jump_duration / 2
    start_vertical_velocity = gravity * jump_duration / 2
    y_avoidance = 0  # ###
    start_rotation = 0  # ###
    middle_rotation = 0  # ###
    end_rotation = 0  # ###
    rotate_towards_player = True
    world_rotation = Quaternion(0, 0, 0, 1)
    inverse_world_rotation = Quaternion(0, 0, 0, 1)  # ###
    world_to_player_rotation = Quaternion(0, 0, 0, 1)
    rotated_object_up = Vector3(0, 1, 0)
    end_distance_offset = 0  # ###

    def position(time: float) -> Union(Vector3, None):
        relative_time = time - movement_start_time  # Called num1 in source

        # Called floor movement in code
        if relative_time < move_duration:
            return lerp(floor_movement_start_pos, floor_movement_end_pos, relative_time / move_duration)

        relative_time = time - jump_start_time  # Called num1 in source
        start_pos = floor_movement_end_pos
        end_pos = jump_end_pos
        percentage_of_jump = relative_time / jump_duration  # Called t in source

        local_pos = Vector3(0, 0, 0)  # Called localPosition in source

        if start_pos.x == end_pos.x:
            local_pos.x = start_pos.x
        elif percentage_of_jump >= 0.25:
            local_pos.x = end_pos.x
        else:
            local_pos.x = lerp_unclamped(start_pos, end_pos, quadratic_in_out(percentage_of_jump * 4))

        local_pos.y = start_pos.y + start_vertical_velocity * relative_time - gravity * relative_time * relative_time
        local_pos.z = move_towards_head(start_pos.z, end_pos.z, inverse_world_rotation, percentage_of_jump)

        if y_avoidance != 0 and percentage_of_jump < 0.25:
            local_pos.y += (0.5 - cos(percentage_of_jump * 8 * π)) * y_avoidance

        if percentage_of_jump < 0.5:
            if percentage_of_jump >= 0.25:
                a = quat_slerp(middle_rotation, end_rotation, sin((percentage_of_jump - 0.125) * π * 2))
            else:
                a = quat_slerp(start_rotation, middle_rotation, sin((percentage_of_jump * π * 4)))

            if rotate_towards_player:
                head_pseudo_location = Vector3(0, 0, 0)  # ###
                head_pseudo_location.y = lerp(head_pseudo_location.y, local_pos.y, 0.8)
                normalized = (local_pos - inverse_world_rotation * head_pseudo_location)
                vector3 = world_to_player_rotation * rotated_object_up
                b = look_rotation(normalized, inverse_world_rotation * vector3)
                rotated_object_local_rotation = lerp(a, b, percentage_of_jump * 2)
            else:
                rotated_object_local_rotation = a

        if percentage_of_jump >= 0.75:
            num2 = (percentage_of_jump - 0.75) / 0.25
            local_pos.z -= lerp_unclamped(0, end_distance_offset * num2 * num2 * num2)

        return world_rotation * local_pos

    return position
