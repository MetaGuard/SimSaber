from noteMovement import create_note_position_function, MovementData, NoteData
from typeDefs import Map as MAP, BeatMap, Note
from Bsor import Bsor, make_bsor
from matplotlib import pyplot as plt
import numpy as np
from interpretMapFiles import create_map
from Geometry import Vector3


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
testBeatMap.notes.append(Note())
testBeatMap.notes.append(Note())


for i in range(3):
    testNote = testBeatMap.notes[i]
    testNote.time = 4
    testNote.type = 0
    testNote.lineIndex = 1
    testNote.lineLayer = i
    testNote.cutDirection = 0

testBsor = Bsor()
testBsor.file_version = 0

filename = './sample.bsor'
with open(filename, 'rb') as f:
    m = make_bsor(f)

mapFolderPath = './2b69a (As It Was - Taddus)/'
mapFile = create_map(mapFolderPath)
testBeatMap = mapFile.beatMaps['Standard']['Normal']

NUM_NOTES = 4
position_funtions = [create_note_position_function(mapFile, testBeatMap.notes[i], m)
                     for i in range(NUM_NOTES)]



# for frame in m.frames[100:110]:
#     print(frame.time, position_function(frame.time, frame))

ax = plt.figure().add_subplot(projection='3d')

START_FRAME = 0
END_FRAME = 900


# NoteMovementInfo = MovementData(mapFile, )

def distance(x, y):
    return (x - y).mag()


for i in range(NUM_NOTES):
    points = [position_funtions[i](frame.time, frame) for frame in m.frames[START_FRAME:END_FRAME]]
    points = np.array([[pos.x, pos.y, pos.z] for pos in points])
    ax.scatter(points[:, 0], points[:, 1], points[:, 2])

NOTE_INDEX = 3

cut_points = np.array([m.notes[i].cut.cutPoint for i in range(NUM_NOTES)])

cut_point_vector = Vector3(*cut_points[NOTE_INDEX])
#frame = min(m.frames, key=lambda f: abs(f.time - m.notes[NOTE_INDEX].event_time))
frame = min(m.frames, key=lambda f: distance(position_funtions[NOTE_INDEX](f.time, f), cut_point_vector))

# print('time difference: ', frame.time - m.notes[NOTE_INDEX].event_time)
# print(position_funtions[NOTE_INDEX](frame.time, frame))
# print('distance: ', (Vector3(*cut_points[NOTE_INDEX]) - position_funtions[NOTE_INDEX](frame.time, frame)).mag())
# print(m.notes[NOTE_INDEX].cut.cutDistanceToCenter)
print("-----")
print(cut_point_vector - position_funtions[NOTE_INDEX](frame.time, frame))


distances_for_closest_time_frames = []
for i in range(NUM_NOTES):
    frame = min(m.frames, key=lambda f: abs(f.time - m.notes[i].event_time))
    distances_for_closest_time_frames.append(
        distance(position_funtions[i](frame.time, frame), Vector3(*cut_points[i]))
        )
print(distances_for_closest_time_frames)
avg_z_dist = sum(distances_for_closest_time_frames)/NUM_NOTES
max_adjusted_distance = max((a - avg_z_dist for a in distances_for_closest_time_frames))

diff_vector = cut_point_vector - position_funtions[NOTE_INDEX](frame.time, frame)
diff_vector.z -= .25 # max_adjusted_distance
print('distance between predicted note position and cutPoint: ', diff_vector.mag())
print('cutDistanceToCenter: ', m.notes[NOTE_INDEX].cut.cutDistanceToCenter)
print('diff: ', diff_vector.mag() - m.notes[NOTE_INDEX].cut.cutDistanceToCenter)

ax.scatter(cut_points[:, 0], cut_points[:, 1], cut_points[:, 2], s=200)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.set_xlim(-1, 1)
ax.set_ylim(0, 2)
ax.set_zlim(-1, 10)

ax.view_init(roll=90)
# ax.set_box_aspect(1, 1, 2)

# plt.show()
