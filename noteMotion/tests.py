import unittest
from geometry import Vector3, Quaternion, Orientation
from noteMotion import create_note_orientation_updater
from Bsor import make_bsor
from interpretMapFiles import create_map, load_note_movement_data
from matplotlib import pyplot as plt
import numpy as np


class TestPosition(unittest.TestCase):
    PRECISION = 5

    def assertVectorAlmostEqual(self, v1, v2, precision, msg):
        self.assertAlmostEqual(v1.x, v2.x, precision, msg)
        self.assertAlmostEqual(v1.y, v2.y, precision, msg)
        self.assertAlmostEqual(v1.z, v2.z, precision, msg)

    @unittest.skip
    def test_y_over_time_plot(self):
        TESTING_PATH = './testData/Bang/'
        NOTE_INDEX = 4

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
        observed_data = load_note_movement_data(TESTING_PATH + 'motion/')[NOTE_INDEX]
        updater = create_note_orientation_updater(map_file, beat_map.notes[NOTE_INDEX], replay)
        first_time = observed_data.times[0] - 0.001
        last_time = observed_data.times[-1]

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        diffs = []
        observed_ys = []
        predicted_ys = []
        times = []

        for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
            updater(frame, test_block)
            observed = observed_data.positions[index]
            times.append(frame.time)
            observed_ys.append(observed.y)
            predicted_ys.append(test_block.position.y)
            diffs.append(test_block.position.y - observed.y)

        fig, ax = plt.subplots()
        # ax.plot(times, diffs, linewidth=2.0)
        ax.plot(times, observed_ys, linewidth=2.0)  # blue
        ax.plot(times, predicted_ys, linewidth=2.0)  # orange

        plt.show()

    def test_position_on_Bang(self):
        TESTING_PATH = './testData/Bang/'

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
        observed_data = load_note_movement_data(TESTING_PATH + 'motion/')
        for note_index in range(10):
            note_data = observed_data[note_index]
            updater = create_note_orientation_updater(map_file, beat_map.notes[note_index], replay)

            first_time = note_data.times[0] - 0.001
            last_time = note_data.times[-1]

            test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

            for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
                updater(frame, test_block)
                observed = note_data.positions[index]

                with self.subTest(note_index=note_index, frame_index=index):
                    wrong_pos_msg = '\n' + str(test_block.position) + ' ' + str(observed) + '\n' +\
                        str(beat_map.notes[note_index].lineLayer) + ' ' + str(frame.time)
                    wrong_time_msg = 'index: {0}, observed: {1}, frame: {2}'.format(
                        index, note_data.times[index], frame.time)
                    self.assertAlmostEqual(frame.time, note_data.times[index], 5, wrong_time_msg)
                    self.assertVectorAlmostEqual(test_block.position, observed, self.PRECISION, wrong_pos_msg)


class TestRotation(unittest.TestCase):
    PRECISION = 4

    def assertQuaternionAlmostEqual(self, q1, q2, precision, msg):
        self.assertAlmostEqual(q1.x, q2.x, precision, msg)
        self.assertAlmostEqual(q1.y, q2.y, precision, msg)
        self.assertAlmostEqual(q1.z, q2.z, precision, msg)
        self.assertAlmostEqual(q1.w, q2.w, precision, msg)

    def setUp(self):
        TESTING_PATH = './testData/Bang/'
        NOTE_INDEX = 0

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            self.replay = make_bsor(f)
            f.close()

        self.map_file = create_map(TESTING_PATH + 'map')
        self.beat_map = self.map_file.beatMaps[self.replay.info.mode][self.replay.info.difficulty]
        self.observed_data = load_note_movement_data(TESTING_PATH + 'motion/')[NOTE_INDEX]
        self.updater = create_note_orientation_updater(self.map_file, self.beat_map.notes[NOTE_INDEX], self.replay)

    @unittest.skip
    def test_plot_diff_over_time(self):
        TESTING_PATH = './testData/Bang/'
        NOTE_INDEX = 0

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
        observed_data = load_note_movement_data(
            TESTING_PATH + 'motion/')[NOTE_INDEX]
        updater = create_note_orientation_updater(
            map_file, beat_map.notes[NOTE_INDEX], replay)
        first_time = observed_data.times[0] - 0.001
        last_time = observed_data.times[-1]

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        diffs = []
        times = []

        for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
            updater(frame, test_block)
            observed = observed_data.rotations[index]
            times.append(frame.time)
            diff = test_block.rotation - observed
            diffs.append(diff.dot(diff))

        fig, ax = plt.subplots()
        ax.plot(times, diffs, linewidth=2.0)

        plt.show()

    def test_plot_3D_rotation(self):
        TESTING_PATH = './testData/Bang/'
        NOTE_INDEX = 0
        fig_to_show = 0
        show_sphere = False

        with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
            replay = make_bsor(f)
            f.close()

        map_file = create_map(TESTING_PATH + 'map')
        beat_map = map_file.beatMaps[replay.info.mode][replay.info.difficulty]
        observed_data = load_note_movement_data(
            TESTING_PATH + 'motion/')[NOTE_INDEX]
        updater = create_note_orientation_updater(
            map_file, beat_map.notes[NOTE_INDEX], replay)
        first_time = observed_data.times[0] - 0.001
        last_time = observed_data.times[-1]

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        predicted_rots = []
        observed_rots = []
        quotients1 = []
        quotients2 = []
        eighth_jump = 1.7667321349893297

        for index, frame in enumerate([frame for frame in replay.frames if first_time <= frame.time <= last_time]):
            updater(frame, test_block)
            observed = observed_data.rotations[index]
            predicted_rots.append(test_block.rotation)
            observed_rots.append(observed)
            if frame.time < eighth_jump:
                quotients1.append(observed.conjugate() * test_block.rotation)
            else:
                quotients2.append(observed.conjugate() * test_block.rotation)

        def split_vec_list(vec_list):
            return ([v.x for v in vec_list], [v.y for v in vec_list], [v.z for v in vec_list])

        ax = plt.figure().add_subplot(projection='3d')
        # ax.scatter(*split_vec_list([Vector3(0, 1, 0).rotate(q) for q in observed_rots]))
        # ax.scatter(*split_vec_list([Vector3(0, 0, 1).rotate(q) for q in observed_rots]))
        # ax.scatter(*split_vec_list([Vector3(0, 1, 0).rotate(q) for q in predicted_rots]))
        # ax.scatter(*split_vec_list([Vector3(0, 0, 1).rotate(q) for q in predicted_rots]))
        # ax.scatter(*split_vec_list([Vector3(0, 1, 0).rotate(q) for q in quotients]))
        # ax.scatter(*split_vec_list([Vector3(0, 0, 1).rotate(q) for q in quotients]))
        ax.plot(*split_vec_list([Vector3(0, 1, 0).rotate(q) for q in quotients1]), color='cornflowerblue')
        ax.plot(*split_vec_list([Vector3(0, 0, 1).rotate(q) for q in quotients1]), color='red')
        ax.plot(*split_vec_list([Vector3(0, 1, 0).rotate(q) for q in quotients2]), color='blue')
        ax.plot(*split_vec_list([Vector3(0, 0, 1).rotate(q) for q in quotients2]), color='orangered')

        if show_sphere:
            # sphere
            u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:30j]
            x = np.cos(u)*np.sin(v)
            y = np.sin(u)*np.sin(v)
            z = np.cos(v)

            ax.plot_wireframe(x, y, z, color="r", linewidth=0.1)

        if fig_to_show == 0:
            zoom = .0001
            # ups
            ax.set_xlim(-zoom, zoom)
            ax.set_ylim(1 - zoom, 1 + zoom)
            ax.set_zlim(-zoom / 5, zoom / 5)
        elif fig_to_show == 1:
            zoom = .0001
            # forwards
            ax.set_xlim(-zoom, zoom)
            ax.set_ylim(-zoom/10, zoom/10)
            ax.set_zlim(1 - zoom, 1 + zoom)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

    def test_first_eight_rotation_on_Bang(self):
        first_time = self.observed_data.times[0] - 0.001
        last_time = 1.7667321349893297

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        for index, frame in enumerate([frame for frame in self.replay.frames if first_time <= frame.time <= last_time]):
            self.updater(frame, test_block)
            observed = self.observed_data.rotations[index]

            msg = 'at time {0}'.format(frame.time)
            wrong_time_msg = 'index: {0}, observed: {1}, frame: {2}'.format(
                index, self.observed_data.times[index], frame.time)

            with self.subTest(index=index):
                self.assertAlmostEqual(frame.time, self.observed_data.times[index], 6, wrong_time_msg)
                self.assertQuaternionAlmostEqual(test_block.rotation, observed, self.PRECISION, msg)

    def test_rest_of_first_half_rotation_on_Bang(self):
        first_time = 1.7667321349893297
        last_time = min(2.142857142857143, self.observed_data.times[-1])
        index_offset = 11

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        for index, frame in enumerate([frame for frame in self.replay.frames if first_time <= frame.time <= last_time]):
            index += index_offset
            self.updater(frame, test_block)
            observed = self.observed_data.rotations[index]

            msg = 'at time {0}'.format(frame.time)
            wrong_time_msg = 'index: {0}, observed: {1}, frame: {2}'.format(
                index, self.observed_data.times[index], frame.time)

            with self.subTest(index=index):
                self.assertAlmostEqual(frame.time, self.observed_data.times[index], 5, wrong_time_msg)
                self.assertQuaternionAlmostEqual(test_block.rotation, observed, self.PRECISION, msg)

    def test_second_half_rotation(self):
        first_time = 2.142857142857143
        last_time = self.observed_data.times[-1]
        index_offset = 0

        test_block = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        for index, frame in enumerate([frame for frame in self.replay.frames if first_time <= frame.time <= last_time]):
            index += index_offset
            self.updater(frame, test_block)
            observed = self.observed_data.rotations[index]

            msg = 'at time {0}'.format(frame.time)
            wrong_time_msg = 'index: {0}, observed: {1}, frame: {2}'.format(
                index, self.observed_data.times[index], frame.time)

            self.subTest(index=index)
            self.assertAlmostEqual(frame.time, self.observed_data.times[index], 5, wrong_time_msg)
            self.assertQuaternionAlmostEqual(test_block.rotation, observed, self.PRECISION, msg)
