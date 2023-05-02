
from noteMotion.noteMovement import create_note_orientation_updater
from Bsor import make_bsor
from interpretMapFiles import create_map, load_note_movement_data
from geometry import Quaternion, Orientation, Vector3

TESTING_PATH = './testData/Bang/'

replay = make_bsor(open(TESTING_PATH + 'replay.bsor', 'rb'))
map_file = create_map(TESTING_PATH + 'map')
beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
real_motion_data = load_note_movement_data(TESTING_PATH + 'motion/')

NOTE_INDEX = 2
updater = create_note_orientation_updater(map_file, beat_map.notes[NOTE_INDEX], replay)

first_time = real_motion_data[NOTE_INDEX].times[0] - 0.001
last_time = real_motion_data[NOTE_INDEX].times[-1]

predicted_orientation = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))
for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
    updater(frame, predicted_orientation)
    predicted = predicted_orientation.rotation
    observed = real_motion_data[NOTE_INDEX].rotations[index]
    error_quat = predicted - observed
    error = error_quat.dot(error_quat)
    print("Predicted\tt =", round(frame.time, 5), "\t", round(predicted.x, 5), round(predicted.y, 5), round(predicted.z, 5), round(predicted.w, 5))
    print("Observed\tt =", round(real_motion_data[NOTE_INDEX].times[index], 5), "\t", round(observed.x, 5), round(observed.y, 5), round(observed.z, 5), round(observed.w, 5))
    print("Error\t\tΔ =", round(error, 5), "\n")
