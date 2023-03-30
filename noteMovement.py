from typeDefs import *
from typing import *


def create_note_position_function(map: Map, note: Note) -> function:
    jump_duration = 1
    note_time = note.time * map.beatsPerMinute
    start_pos = Vector3(0, 0, 0)
    end_pos = Vector3(1, 2, 3)

    def position(time: float) -> Union(Vector3, None):
        percentage_of_jump = (time - note_time)/jump_duration
        if 0 <= percentage_of_jump <= 1:
            return start_pos + (end_pos - start_pos) * percentage_of_jump

    return position
