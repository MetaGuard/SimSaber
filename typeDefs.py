from typing import *


class Obstacle:
    width: int
    lineIndex: int
    time: float
    type: int       # Not sure what the different type of walls mean?
    duration: float


class Note:
    time: float
    type: int
    lineIndex: int
    lineLayer: int
    cutDirection: int


class BeatMap:
    difficulty: str
    noteJumpMovementSpeed: float
    noteJumpStartBeatOffset: float
    notes: List[Note]
    obstacles: List[Obstacle]


class Map:
    beatsPerMinute: int
    beatMaps: Dict[str, Dict[str, BeatMap]]