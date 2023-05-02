from typing import List, Optional, Callable
from geometry import Vector3, Plane, Ray
from SaberSwingRating import SaberSwingRating
import SaberMovementData as md

class SaberSwingRatingCounter:
    _saber_movement_data: md.SaberMovementData
    _did_change_receivers = []
    _did_finish_receivers = []

    def __init__(self, saber_movement_data: md.SaberMovementData, note, rate_before_cut = True, rate_after_cut = True):
        note_position = note.orientation.position
        note_rotation = note.orientation.rotation
        self._note = note 

        self._finished = False
        self._note_plane_was_cut = False
        last_added_data = saber_movement_data.last_added_data
        self._cut_plane_normal = last_added_data.segment_normal
        self._cut_time = last_added_data.time
        self._rate_before_cut = rate_before_cut
        self._rate_after_cut = rate_after_cut
        self._before_cut_rating = 1 if not rate_before_cut else saber_movement_data.compute_swing_rating()
        self._after_cut_rating = 1 if not rate_after_cut else 0
        self._note_plane_center = note_position
        self._note_plane = Plane(note_rotation.multiply_point(Vector3(0.0, 1, 0.0)), self._note_plane_center)
        self._note_forward = note_rotation.multiply_point(Vector3(0.0, 0.0, 1))
        self._saber_movement_data = saber_movement_data
        self._saber_movement_data.add_data_processor(self)
        self._saber_movement_data.request_last_data_processing(self)

    @property
    def before_cut_rating(self):
        return self._before_cut_rating

    @property
    def after_cut_rating(self):
        return self._after_cut_rating

    def process_new_data(self, new_data: md.BladeMovementDataElement, prev_data: md.BladeMovementDataElement, prev_data_are_valid: bool):
        if new_data.time - self._cut_time > 0.4:
            self.finish()
        else:
            if not prev_data_are_valid:
                return

            if not self._note_plane_was_cut:
                self._new_plane_normal = self._cut_plane_normal.cross(self._note_forward)
                self._note_plane = Plane(self._new_plane_normal, self._note_plane_center)

            if not self._note_plane_was_cut and not self._note_plane.same_side(new_data.top_pos, prev_data.top_pos):
                self._before_cut_top_pos = prev_data.top_pos
                self._before_cut_bottom_pos = prev_data.bottom_pos
                self._after_cut_top_pos = new_data.top_pos
                self._after_cut_bottom_pos = new_data.bottom_pos
                ray = Ray(prev_data.top_pos, new_data.top_pos - prev_data.top_pos)
                _, enter = self._note_plane.raycast(ray)
                self._cut_top_pos = ray.get_point(enter)
                self._cut_bottom_pos = (prev_data.bottom_pos + new_data.bottom_pos) * 0.5
                override_segment_angle = Vector3.angle(self._cut_top_pos - self._cut_bottom_pos, self._before_cut_top_pos - self._before_cut_bottom_pos)
                angle_diff = Vector3.angle(self._cut_top_pos - self._cut_bottom_pos, self._after_cut_top_pos - self._after_cut_bottom_pos)
                self._cut_time = new_data.time

                if self._rate_before_cut:
                    self._before_cut_rating = self._saber_movement_data.compute_swing_rating(override_segment_angle)

                if self._rate_after_cut:
                    self._after_cut_rating = SaberSwingRating.after_cut_step_rating(angle_diff, 0.0)

                self._note_plane_was_cut = True

            else:
                normal_diff = Vector3.angle(new_data.segment_normal, self._cut_plane_normal)

                if normal_diff > 90.0:
                    self.finish()
                    return

                if self._rate_after_cut:
                    self._after_cut_rating += SaberSwingRating.after_cut_step_rating(new_data.segment_angle, normal_diff)

    def finish(self):
        self._saber_movement_data.remove_data_processor(self)
        self._note.finish_cut(self.after_cut_rating, self.before_cut_rating)
        self._finished = True

