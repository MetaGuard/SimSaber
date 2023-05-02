from typeDefs import *
from typing import *
from Bsor import Bsor


def calculate_score(map: Map, replay: Bsor) -> int:
    """
    Pseudo-code Outline:

    energy = Energybar()
    combo = Combo()
    score = 0
    active_notes
    active_obstacles

    for frame in replay.frames:
        process new saber and head positions
    
        add new notes/bombs/obstacle objects to active_notes and active_obstacles

        check for collision between sabers and active notes
        check for collision between head and obstacles

        for each collision:
            update energy
            update combo
            calculate score and update it
    
    return score

    """
    return 0
