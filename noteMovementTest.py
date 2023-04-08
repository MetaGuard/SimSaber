from noteMovement import create_note_position_function
from typeDefs import Map as MAP, BeatMap, Note
from bsor.Bsor import Bsor, make_bsor

mapFile = MAP()
mapFile.beatsPerMinute = 120
mapFile.beatMaps = {}
mapFile.beatMaps["Standard"] = {}
mapFile.beatMaps["Standard"]["Easy"] = BeatMap()

testBeatMap = mapFile.beatMaps["Standard"]["Easy"]
testBeatMap.difficulty = "Easy"
testBeatMap.noteJumpMovementSpeed = 5
testBeatMap.noteJumpStartBeatOffset = 0
testBeatMap.notes = []
testBeatMap.notes.append(Note())

testNote = testBeatMap.notes[0]
testNote.time = 2
testNote.type = 0
testNote.lineIndex = 2
testNote.lineLayer = 1
testNote.cutDirection = 0

testBsor = Bsor()
testBsor.file_version = 0

filename = './sample.bsor'
with open(filename, 'rb') as f:
    m = make_bsor(f)

create_note_position_function(mapFile, testNote, m)
