import unittest
from geometry import Vector3, Quaternion, Orientation
from noteMotion import create_note_orientation_updater
from bsor.Bsor import make_bsor
from interpretMapFiles import create_map
import pandas as pd


class TestPosition(unittest.TestCase):
    PRECISION = 5

    def assertVectorAlmostEqual(self, v1, v2, precision):
        self.assertAlmostEqual(v1.x, v2.x, precision)
        self.assertAlmostEqual(v1.y, v2.y, precision)
        self.assertAlmostEqual(v1.z, v2.z, precision)

    def test_position_on_Bang(self):
        TESTING_PATH = './testData/Bang/'
        MOTION_FILE_NAME = '2.142857_32011.csv'

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]

        updater = create_note_orientation_updater(map_file, beat_map.notes[0], replay)

        actual = pd.read_csv(TESTING_PATH + 'motion/' + MOTION_FILE_NAME).to_numpy()
        first_time = actual[0][0] - 0.001
        last_time = actual[-1][0]

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
            updater(frame, test_block)
            observed = Vector3(*actual[index][1:4])

            self.assertVectorAlmostEqual(test_block.position, observed, self.PRECISION)


class TestRotation(unittest.TestCase):
    PRECISION = 4

    def assertQuaternionAlmostEqual(self, q1, q2, precision, msg):
        self.assertAlmostEqual(q1.x, q2.x, precision, msg)
        self.assertAlmostEqual(q1.y, q2.y, precision, msg)
        self.assertAlmostEqual(q1.z, q2.z, precision, msg)
        self.assertAlmostEqual(q1.w, q2.w, precision, msg)

    def test_rotation_on_Bang(self):
        TESTING_PATH = './testData/Bang/'
        MOTION_FILE_NAME = '2.142857_32011.csv'

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]

        updater = create_note_orientation_updater(
            map_file, beat_map.notes[0], replay)

        actual = pd.read_csv(TESTING_PATH + 'motion/' + MOTION_FILE_NAME).to_numpy()
        first_time = actual[0][0] - 0.001
        last_time = actual[-1][0]

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
            updater(frame, test_block)
            observed = Quaternion(*actual[index][4:])

            msg = 'at time {0}'.format(frame.time)
            self.assertQuaternionAlmostEqual(test_block.rotation, observed, self.PRECISION, msg)
