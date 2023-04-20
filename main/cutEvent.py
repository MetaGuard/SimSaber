from saberMovementBuffer import SaberMovementBuffer
from math import acos, pi as π, round
from typeDefs import SaberMovementData


class GoodCutEvent:
    def __init__(self, buffer: SaberMovementBuffer, note_orientation):
        self.note_orientation = note_orientation
        self.right_before = buffer.get_prev()
        self.right_after = buffer.get_curr()
        self.estimated_saber_data = SaberMovementData()
        self.estimated_saber_data.hiltPos = (self.right_before.hiltPos + self.right_after.hiltPos) / 2  # incorrect
        self.estimated_saber_data.tipPos = (self.right_before.tipPos + self.right_after.tipPos) / 2  # incorrect
        self.cut_time = self.right_after.time

        prev_data = self.estimated_saber_data
        self.before_cut_angle = 0

        for saber_data in buffer:
            if self.cut_time - saber_data.time > 0.4:
                break

            dot_with_cut_vec = saber_data.cutPlaneNormal.dot(self.right_after.cutPlaneNormal)
            if dot_with_cut_vec < 0:
                break

            angle_with_cut_vec = acos(dot_with_cut_vec)
            angle_segment = GoodCutEvent.angle_segment(saber_data, prev_data)

            if angle_with_cut_vec < 70:
                self.before_cut_angle += angle_segment
            else:
                self.before_cut_angle += angle_segment * (90 - angle_with_cut_vec) / 20

            if self.before_cut_angle >= 100:
                break

            prev_data = saber_data

        self.after_cut_angle = GoodCutEvent.angle_segment(self.right_after, self.estimated_saber_data)
        self.most_recent_data = self.right_after
        self.finished = False
        self.calculate_acc()

    @staticmethod
    def angle_segment(data1, data2):
        return acos((data1.tipPos - data1.hiltPos).dot(data2.tipPos - data2.hiltPos)) * 180 / π

    def update(self, saber_data: SaberMovementData):
        if self.finished:
            return False

        if self.cut_time - saber_data.time > 0.4:
            self.after_cut_rating = self.after_cut_angle / 30
            self.finished = True
            return False

        dot_with_cut_vec = saber_data.cutPlaneNormal.dot(self.right_after.cutPlaneNormal)
        if dot_with_cut_vec < 0:
            self.after_cut_rating = self.after_cut_angle / 30
            self.finished = True
            return False

        angle_with_cut_vec = acos(dot_with_cut_vec)
        angle_segment = GoodCutEvent.angle_segment(saber_data, self.most_recent_data)

        if angle_with_cut_vec >= 70:
            self.after_cut_angle += angle_segment
        else:
            self.after_cut_angle += angle_segment * (90 - angle_with_cut_vec) / 20

        if self.after_cut_angle > 70:
            self.after_cut_rating = self.after_cut_angle / 30
            self.finished = True
            return False

        self.most_recent_data = saber_data

    def calculate_acc(self):
        self.acc = 15

    def get_score(self):
        return (
            round(self.before_cut_angle / 100) * 70 +
            round(self.after_cut_angle / 70) * 30 +
            self.acc
        )
