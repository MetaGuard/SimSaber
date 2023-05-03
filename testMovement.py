from noteMotion.noteMovement import create_note_orientation_updater, MovementData, NoteData
from typeDefs import Map as MAP, BeatMap, Note
from Bsor import Bsor, make_bsor
from matplotlib import pyplot as plt
import numpy as np
from interpretMapFiles import create_map
from geometry import Vector3, Orientation, Quaternion
import pandas as pd
import glob

TESTING_PATH = './testData/Bang/'

with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
    m = make_bsor(f)

mapFile = create_map(TESTING_PATH + 'map')
testBeatMap = mapFile.beatMaps[m.info.mode][m.info.difficulty]

test_files = glob.glob(TESTING_PATH + "motion/*.csv")
test_files.sort(key=lambda x: float(x.split('_')[0].split('\\')[-1]))

MOTION_FILE_INDEX = 217
SUM_TEST = True

position_error_sum = 0
rotation_error_sum = 0

for i in range(len(test_files) if SUM_TEST else 1):
    orientation = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))
    note = testBeatMap.notes[i if SUM_TEST else MOTION_FILE_INDEX]
    position_function = create_note_orientation_updater(mapFile, note, m)

    filename = test_files[i if SUM_TEST else MOTION_FILE_INDEX]
    print(f"Testing file: {filename}")
    if not SUM_TEST:
        print(f"Note line_index {note.lineIndex}, line_layer {note.lineLayer}, type {note.type}, cut_direction {note.cutDirection}")
    else:
        print(i)
    actual = pd.read_csv(filename).to_numpy()
    first_time = actual[0][0] - 0.001
    last_time = actual[-1][0]


    for index, frame in enumerate([frame for frame in m.frames if first_time <= frame.time <= last_time]):
        position_function(frame, orientation)
        predicted = orientation.position
        
        observed = Vector3(actual[index][1], actual[index][2], actual[index][3])
        error = Vector3.distance(predicted, observed)
        if not SUM_TEST:
            print("Position:")
            print("Predicted\tt =", round(frame.time, 5), "\t", round(predicted.x, 5), round(predicted.y, 5), round(predicted.z, 5))
            print("Observed\tt =", round(actual[index][0], 5), "\t", round(observed.x, 5), round(observed.y, 5), round(observed.z, 5))
            print("Error\t\tΔ =", round(error, 5), "\n")

        position_error_sum += error

        predicted2 = orientation.rotation.to_Euler()
        observed2 = Quaternion(actual[index][4], actual[index][5], actual[index][6], actual[index][7]).to_Euler()
        error2 = Vector3.distance(predicted2, observed2)
        if not SUM_TEST:
            print("Rotation:")
            print("Predicted\tt =", round(frame.time, 5), "\t", round(predicted2.x, 5), round(predicted2.y, 5), round(predicted2.z, 5))
            print("Observed\tt =", round(actual[index][0], 5), "\t", round(observed2.x, 5), round(observed2.y, 5), round(observed2.z, 5))
            print("Error\t\tΔ =", round(error2, 5), "\n")

        rotation_error_sum += error2

    print("Position error sum:", position_error_sum)
    print("Rotation error sum:", rotation_error_sum)

# NUM_NOTES = 1
# position_funtions = [create_note_position_function(mapFile, testBeatMap.notes[i], m)
#                      for i in range(NUM_NOTES)]
#
#
#
# # for frame in m.frames[100:110]:
# #     print(frame.time, position_function(frame.time, frame))
#
# ax = plt.figure().add_subplot(projection='3d')
#
# START_FRAME = 0
# END_FRAME = 900
#
#
# # NoteMovementInfo = MovementData(mapFile, )
#
#
# for i in range(NUM_NOTES):
#     points = [position_funtions[i](frame.time, frame) for frame in m.frames[START_FRAME:END_FRAME]]
#     points = np.array([[pos.x, pos.y, pos.z] for pos in points])
#     ax.scatter(points[:, 0], points[:, 1], points[:, 2])
#
# NOTE_INDEX = 3
#
# cut_points = np.array([m.notes[i].cut.cutPoint for i in range(NUM_NOTES)])
#
# cut_point_vector = Vector3(*cut_points[NOTE_INDEX])
# #frame = min(m.frames, key=lambda f: abs(f.time - m.notes[NOTE_INDEX].event_time))
# frame = min(m.frames, key=lambda f: distance(position_funtions[NOTE_INDEX](f.time, f), cut_point_vector))
#
# # print('time difference: ', frame.time - m.notes[NOTE_INDEX].event_time)
# # print(position_funtions[NOTE_INDEX](frame.time, frame))
# # print('distance: ', (Vector3(*cut_points[NOTE_INDEX]) - position_funtions[NOTE_INDEX](frame.time, frame)).mag())
# # print(m.notes[NOTE_INDEX].cut.cutDistanceToCenter)
# print("-----")
# print(cut_point_vector - position_funtions[NOTE_INDEX](frame.time, frame))
#
#
# distances_for_closest_time_frames = []
# for i in range(NUM_NOTES):
#     frame = min(m.frames, key=lambda f: abs(f.time - m.notes[i].event_time))
#     distances_for_closest_time_frames.append(
#         distance(position_funtions[i](frame.time, frame), Vector3(*cut_points[i]))
#         )
# print(distances_for_closest_time_frames)
# avg_z_dist = sum(distances_for_closest_time_frames)/NUM_NOTES
# max_adjusted_distance = max((a - avg_z_dist for a in distances_for_closest_time_frames))
#
# diff_vector = cut_point_vector - position_funtions[NOTE_INDEX](frame.time, frame)
# diff_vector.z -= .25 # max_adjusted_distance
# print('distance between predicted note position and cutPoint: ', diff_vector.mag())
# print('cutDistanceToCenter: ', m.notes[NOTE_INDEX].cut.cutDistanceToCenter)
# print('diff: ', diff_vector.mag() - m.notes[NOTE_INDEX].cut.cutDistanceToCenter)
#
# ax.scatter(cut_points[:, 0], cut_points[:, 1], cut_points[:, 2], s=200)
#
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')
#
# ax.set_xlim(-1, 1)
# ax.set_ylim(0, 2)
# ax.set_zlim(-1, 10)
#
# ax.view_init(roll=90)
# # ax.set_box_aspect(1, 1, 2)
#
# # plt.show()
