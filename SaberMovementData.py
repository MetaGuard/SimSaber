from typing import Optional
from geometry import Vector3
from SaberSwingRating import SaberSwingRating


class BladeMovementDataElement:
    top_pos: Vector3
    bottom_pos: Vector3
    segment_normal: Vector3

    def __init__(self):
        self.top_pos = Vector3(0, 0, 0)
        self.bottom_pos = Vector3(0, 0, 0)
        self.time = 0.0
        self.segment_normal = Vector3(0, 0, 0)
        self.segment_angle = 0.0

class SaberMovementData:
    kOutOfRangeBladeSpeed = 100
    kSmoothUpBladeSpeedCoef = 24
    kSmoothDownBladeSpeedCoef = 2

    _data: list[BladeMovementDataElement]

    def __init__(self):
        self._data = [BladeMovementDataElement() for _ in range(500)]
        self._next_add_index = 0
        self._valid_count = 0
        self._blade_speed = 0
        self._data_processors = []

    @property
    def blade_speed(self):
        return self._blade_speed

    @property
    def last_added_data(self):
        index = self._next_add_index - 1
        if index < 0:
            index += len(self._data)
        return self._data[index]

    @property
    def prev_added_data(self):
        index = self._next_add_index - 2
        if index < 0:
            index += len(self._data)
        return self._data[index]

    def add_data_processor(self, data_processor):
        self._data_processors.append(data_processor)

    def remove_data_processor(self, data_processor):
        self._data_processors.remove(data_processor)

    def request_last_data_processing(self, data_processor):
        if self._valid_count <= 0:
            return
        length = len(self._data)
        index1 = self._next_add_index - 1
        if index1 < 0:
            index1 += length
        index2 = index1 - 1
        if index2 < 0:
            index2 += length
        data_processor.process_new_data(self._data[index1], self._data[index2], self._valid_count > 1)

    def add_new_data(self, top_pos: Vector3, bottom_pos: Vector3, time: float):
        length = len(self._data)
        next_add_index = self._next_add_index
        index = next_add_index - 1
        if index < 0:
            index += length
        if self._valid_count > 0:
            dt = time - self._data[index].time
            if dt > 1e-4:
                b = ((top_pos - self._data[index].top_pos) / dt).magnitude()
                if b > 100:
                    b = 100
                self._blade_speed = self._blade_speed + (b - self._blade_speed) * (dt * (self.kSmoothDownBladeSpeedCoef if b < self._blade_speed else self.kSmoothUpBladeSpeedCoef))
        self._data[next_add_index].top_pos = top_pos
        self._data[next_add_index].bottom_pos = bottom_pos
        self._data[next_add_index].time = time
        
        self._data[next_add_index].segment_normal, self._data[next_add_index].segment_angle = self.compute_additional_data(self._data[next_add_index].top_pos, self._data[next_add_index].bottom_pos, 0)

        self._next_add_index = (self._next_add_index + 1) % length
        if self._valid_count < len(self._data):
            self._valid_count += 1
        for data_processor in self._data_processors:
            data_processor.process_new_data(self._data[next_add_index], self._data[index], self._valid_count > 1)

    def compute_additional_data(self, top_pos, bottom_pos, idx_offset):
        length = len(self._data)
        index1 = self._next_add_index + idx_offset
        index2 = index1 - 1
        if index2 < 0:
            index2 += length
        if self._valid_count > 0:
            topPos1 = self._data[index1].top_pos
            bottomPos1 = self._data[index1].bottom_pos
            topPos2 = self._data[index2].top_pos
            bottomPos2 = self._data[index2].bottom_pos

            segment_normal = self.compute_plane_normal(topPos1, bottomPos1, topPos2, bottomPos2)
            segment_angle = (topPos2 - bottomPos2).angle(topPos1 - bottomPos1)
        else:
            segment_normal = Vector3(0, 0, 0)
            segment_angle = 0.0

       
        return (segment_normal, segment_angle)

    def compute_plane_normal(self, tip: Vector3, hilt: Vector3, prev_tip: Vector3, prev_hilt: Vector3) -> Vector3:
        return (tip - hilt).cross((prev_tip + prev_hilt) / 2 - hilt).normal()
    
    def compute_cut_plane_normal(self):
        length = len(self._data)
        index1 = self._next_add_index - 1
        if index1 < 0:
            index1 += length
        index2 = index1 - 1
        if index2 < 0:
            index2 += length
        return self.compute_plane_normal(self._data[index1].top_pos, self._data[index1].bottom_pos, self._data[index2].top_pos, self._data[index2].bottom_pos)

    def compute_swing_rating(self, override_segment_angle: Optional[float] = None):
        if self._valid_count < 2:
            return 0.0
        length = len(self._data)
        index = self._next_add_index - 1
        if index < 0:
            index += length
        time = self._data[index].time
        num1 = time
        num2 = 0.0
        segment_normal1 = self._data[index].segment_normal
        angle_diff = override_segment_angle if override_segment_angle is not None else self._data[index].segment_angle
        num3 = 2
        swing_rating = num2 + SaberSwingRating.before_cut_step_rating(angle_diff, 0.0)
        while (time - num1) < 0.4 and num3 < self._valid_count:
            num3 += 1
            index -= 1
            if index < 0:
                index += length
            segment_normal2 = self._data[index].segment_normal
            segment_angle = self._data[index].segment_angle
            to = segment_normal1
            normal_diff = Vector3.angle(segment_normal2, to)
            if normal_diff <= 90:
                swing_rating += SaberSwingRating.before_cut_step_rating(segment_angle, normal_diff)
                num1 = self._data[index].time
            else:
                break
        return swing_rating