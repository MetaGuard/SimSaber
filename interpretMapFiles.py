from typeDefs import *
from json import load


def create_map(folderPath):
    if folderPath[-1] != "/":
        folderPath += "/"

    info_data = load(open(folderPath + "info.dat", "r"))

    map = Map()
    map.beatsPerMinute = info_data['_beatsPerMinute']
    map.beatMaps = {}

    for beat_map_set in info_data['_difficultyBeatmapSets']:
        characteristic = beat_map_set['_beatmapCharacteristicName']
        difficulties = {}

        for diff in beat_map_set['_difficultyBeatmaps']:
            beat_map = BeatMap()
            beat_map.difficulty = diff['_difficulty']
            beat_map.noteJumpMovementSpeed = diff['_noteJumpMovementSpeed']
            beat_map.noteJumpStartBeatOffset = diff['_noteJumpStartBeatOffset']
            beat_map.notes = []
            beat_map.obstacles = []

            beat_map_file = open(folderPath + diff['_beatmapFilename'], "r")
            populate_beat_map(load(beat_map_file), beat_map)

            difficulties[diff['_difficulty']] = beat_map

        map.beatMaps[characteristic] = difficulties
    return map


def populate_beat_map(JSO, beat_map: BeatMap):
    for note_data in JSO['_notes']:
        note = Note()
        note.time = note_data['_time']
        note.type = note_data['_type']
        note.lineIndex = note_data['_lineIndex']
        note.lineLayer = note_data['_lineLayer']
        note.cutDirection = note_data['_cutDirection']

        beat_map.notes.append(note)
    beat_map.notes.sort(key=lambda n: n.time)

    for obstacle_data in JSO['_obstacles']:
        obstacle = Obstacle()
        obstacle.time = obstacle_data['_time']
        obstacle.type = obstacle_data['_type']
        obstacle.lineIndex = obstacle_data['_lineIndex']
        obstacle.duration = obstacle_data['_duration']
        obstacle.width = obstacle_data['_width']

        beat_map.obstacles.append(obstacle)
    beat_map.obstacles.sort(key=lambda o: o.time)
