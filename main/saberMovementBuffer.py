from typing import *
from typeDefs import SaberMovementData
from bsor.Bsor import VRObject
from geometry import Vector3, Quaternion
from math import acos, pi

BUFFER_SIZE = 500


class SaberMovementBuffer:
    data: List[SaberMovementData]
    nextAddIndex: int

    def __init__(self):
        self.data = [None] * BUFFER_SIZE
        self.nextAddIndex = 0

    def get_curr(self) -> SaberMovementData:
        return self.data[(self.nextAddIndex - 1) % BUFFER_SIZE]

    def get_prev(self) -> SaberMovementData:
        return self.data[(self.nextAddIndex - 2) % BUFFER_SIZE]

    def add_saber_data(self, hand_object: VRObject, time: float):
        new_data = SaberMovementData()
        curr_data = self.get_curr()
        self.data[self.nextAddIndex] = new_data
        self.nextAddIndex = (self.nextAddIndex + 1) % BUFFER_SIZE

        new_data.hiltPos = Vector3(hand_object.x, hand_object.y, hand_object.z)
        new_data.tipPos = Vector3(0, 1, 0).rotate(
            Quaternion(hand_object.x_rot, hand_object.y_rot, hand_object.z_rot, hand_object.w_rot)
        )
        new_data.time = time

        if curr_data is None:
            new_data.cutPlaneNormal = 0
            return
        new_data.cutPlaneNormal = (new_data.hiltPos - new_data.tipPos).cross(
            new_data.hiltPos - (curr_data.tipPos + curr_data.hiltPos) / 2
        ).normal()

    class BufferIterator:
        def __init__(self, buffer):
            self.buffer = buffer
            self.relativeIndex = 0

        def __next__(self) -> SaberMovementData:
            if self.relativeIndex >= BUFFER_SIZE:
                raise StopIteration

            output = self.buffer.data[(self.buffer.nextAddIndex - self.relativeIndex) % BUFFER_SIZE]

            if output is None:
                raise StopIteration

            self.relativeIndex += 1
            return output

    def __iter__(self):
        return self.BufferIterator(self)

    def calculate_swing_rating(self, override=None):
        i = iter(self)
        first_data = next(i)
        first_normal = first_data.cutPlaneNormal
        first_time = first_data.time
        prev_time = first_time
        swing_rating = (first_data.segmentAngle if override is None else override) / 100

        for saber_data in i:
            if first_time - prev_time > 0.4:
                break

            angle_with_normal = first_normal.angle(saber_data.cutPlaneNormal)
            if angle_with_normal >= 90:
                break

            prev_time = saber_data.time

            if angle_with_normal < 75:
                swing_rating += saber_data.segmentAngle / 100
            else:
                swing_rating += saber_data.segmentAngle * (90 - angle_with_normal) / 15 / 100

            if swing_rating > 1:
                return 1

        return swing_rating
