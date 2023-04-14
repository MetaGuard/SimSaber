
from noteMovement import create_note_orientation_updater
from bsor.Bsor import make_bsor
from interpretMapFiles import create_map, load_note_movement_data
from Geometry import Quaternion, Orientation, Vector3

TESTING_PATH = './testing/Bang/'

replay = make_bsor(open(TESTING_PATH + 'replay.bsor', 'rb'))
map_file = create_map(TESTING_PATH + 'map')
beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
real_motion_data = load_note_movement_data(TESTING_PATH + 'motion/')

NOTE_INDEX = 0
updater = create_note_orientation_updater(map_file, beat_map.notes[NOTE_INDEX], replay)

first_time = real_motion_data[NOTE_INDEX].times[0] - 0.001
last_time = real_motion_data[NOTE_INDEX].times[-1]

predicted = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))
for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
    updater(frame, predicted)
    observed = real_motion_data[NOTE_INDEX].rotations[index]
    error_quat = predicted.rotation - observed
    error = error_quat.dot(error_quat)
    print("Error\t\tΔ =", round(error, 5), "\n")
