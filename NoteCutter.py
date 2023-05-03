import numpy as np
from geometry import three_points_to_box, Vector3, Quaternion, Matrix3
from Saber import Saber
from noteManager import NoteObject, NoteManager, Orientation, Hitbox
import functools
import Bsor

def overlap_box(center: Vector3, half_extents: Vector3, orientation: Quaternion, boxes: list[NoteObject]) -> list[tuple[NoteObject, bool]]:
    # Helper function to check if two OBBs overlap
    def obb_overlap(box1: Hitbox, box2: Hitbox) -> bool:
        def separating_axis_exists(axis: Vector3, box1: Hitbox, box2: Hitbox) -> bool:
            projection1 = box1.project_onto_axis(axis)
            projection2 = box2.project_onto_axis(axis)
            return projection1[1] < projection2[0] or projection2[1] < projection1[0]

        box1_axes = box1.get_axes()
        box2_axes = box2.get_axes()

        # Check for separating axis among box1's axes
        for axis in box1_axes:
            if separating_axis_exists(axis, box1, box2):
                return False

        # Check for separating axis among box2's axes
        for axis in box2_axes:
            if separating_axis_exists(axis, box1, box2):
                return False

        # Check for separating axis among cross products of box1's and box2's axes
        for axis1 in box1_axes:
            for axis2 in box2_axes:
                cross_axis = axis1.cross(axis2)
                if cross_axis.magnitude() == 0:
                    continue
                cross_axis = Vector3.normalize(cross_axis)
                if separating_axis_exists(cross_axis, box1, box2):
                    return False
                
        return True

    # Create the reference box
    reference_box = Hitbox(half_extents * 2, 0)
    reference_box.update(Orientation(center, orientation))

    # Find and store overlapping boxes
    overlapping_boxes = []
    for box in boxes:
        if obb_overlap(reference_box, box.big_cuttable):
            overlapping_boxes.append((box, False))
        if obb_overlap(reference_box, box.small_cuttable):
            overlapping_boxes.append((box, True))

    return overlapping_boxes

class CuttableBySaberSortParams:
    cuttable_by_saber: tuple[NoteObject, bool]
    pos: Vector3

    def __init__(self):
        self.cuttable_by_saber = None
        self.distance = 0
        self.pos = None

def compare(bySaberSortParams1: CuttableBySaberSortParams, bySaberSortParams2: CuttableBySaberSortParams):
    if bySaberSortParams1.distance > bySaberSortParams2.distance:
        return 1
    if bySaberSortParams1.distance < bySaberSortParams2.distance:
        return -1
    if bySaberSortParams1.pos.x < bySaberSortParams2.pos.x:
        return 1
    if bySaberSortParams1.pos.x > bySaberSortParams2.pos.x:
        return -1
    if bySaberSortParams1.pos.y < bySaberSortParams2.pos.y:
        return 1
    if bySaberSortParams1.pos.y > bySaberSortParams2.pos.y:
        return -1
    if bySaberSortParams1.pos.z < bySaberSortParams2.pos.z:
        return 1
    if bySaberSortParams1.pos.z > bySaberSortParams2.pos.z:
        return -1

    return 0

class NoteCutter:
    kMaxNumberOfColliders = 16

    cuttable_by_saber_sort_params: list[CuttableBySaberSortParams]

    def __init__(self):
        self.cuttable_by_saber_sort_params = [CuttableBySaberSortParams() for _ in range(self.kMaxNumberOfColliders)]

    def cut(self, saber: Saber, note_manager: NoteManager, replay: Bsor.Bsor):
        saber_blade_top_pos = saber.saber_blade_top_pos
        saber_blade_bottom_pos = saber.saber_blade_bottom_pos
        prev_added_data = saber.movement_data.prev_added_data
        top_pos = prev_added_data.top_pos
        bottom_pos = prev_added_data.bottom_pos
        success, center, half_size, orientation = three_points_to_box(saber_blade_top_pos, saber_blade_bottom_pos, (bottom_pos + top_pos) * 0.5)

        if not success:
            return

        def cut_note(note: tuple[NoteObject, bool]):
            note_object = note[0] 
            cuttable_by_saber = note[1]

            event_note = None
            for note in replay.notes:
                if note_object.id == note.note_id and abs(note_object.spawn_time - note.spawn_time) < 0.001:
                    event_note = note
                    break
            note_object.cut(saber, center, orientation, saber_blade_top_pos - top_pos, cuttable_by_saber, event_note)
        

        self.colliders = overlap_box(center, half_size, orientation, note_manager.get_active_notes())
        length = len(self.colliders)

        if length == 0:
            pass
        elif length == 1:
            cut_note(self.colliders[0])
        else:
            for i in range(length):
                component = self.colliders[i][0]
                small_collider = self.colliders[i][1]

                radius = component.small_cuttable.radius() if small_collider else component.big_cuttable.radius()
                position = component.orientation.position

                cuttable_by_saber_sort_param = self.cuttable_by_saber_sort_params[i]
                cuttable_by_saber_sort_param.cuttable_by_saber = self.colliders[i]
                cuttable_by_saber_sort_param.distance = (top_pos - position).sqr_mag() - radius * radius

                cuttable_by_saber_sort_param.pos = position

            sorted_cuttable_by_saber_sort_params = sorted(self.cuttable_by_saber_sort_params[:length], key=functools.cmp_to_key(compare))

            for cuttable_by_saber_sort_param in sorted_cuttable_by_saber_sort_params:
                cut_note(cuttable_by_saber_sort_param.cuttable_by_saber)



