
from noteMovement import create_note_position_function
from bsor.Bsor import make_bsor
from interpretMapFiles import create_map, load_note_movement_data
from Geometry import Quaternion

TESTING_PATH = './testing/Bang/'

replay = make_bsor(open(TESTING_PATH + 'replay.bsor', 'rb'))
map_file = create_map(TESTING_PATH + 'map')
beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
real_motion_data = load_note_movement_data(TESTING_PATH + 'motion/')

NOTE_INDEX = 0
pos_fn = create_note_position_function(map_file, beat_map.notes[NOTE_INDEX], replay)

first_time = real_motion_data[NOTE_INDEX].times[0] - 0.001
last_time = real_motion_data[NOTE_INDEX].times[-1]


for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
    predicted: Quaternion = pos_fn(frame.time, frame)[1]
    observed = real_motion_data[NOTE_INDEX].rotations[index]
    error_quat = predicted - observed
    error = error_quat.dot(error_quat)
    # print("Predicted\tt =", round(frame.time, 5), "\t", round(predicted.x, 5), round(predicted.y, 5), round(predicted.z, 5))
    # print("Observed\tt =", round(actual[index][0], 5), "\t", round(observed.x, 5), round(observed.y, 5), round(observed.z, 5))
    print("Error\t\tΔ =", round(error, 5), "\n")
