from interpretMapFiles import Map
import Bsor
from geometry import Orientation, Vector3, Quaternion, Plane, Hitbox
import Saber as sb
from noteMotion import create_note_orientation_updater
import SaberSwingRatingCounter as ssrc
from typeDefs import Note
import math

class NoteCutDirection:
    Up = 0
    Down = 1
    Left = 2
    Right = 3
    UpLeft = 4
    UpRight = 5
    DownLeft = 6
    DownRight = 7
    Any = 8
    NoneDirection = 9


kMinBladeSpeedForCut = 2.0
def get_basic_cut_info(note_transform: Orientation, color_type: int, cut_direction: NoteCutDirection, saber_type: int, saber_blade_speed: float, cut_dir_vec: Vector3, cut_angle_tolerance: float):
    cut_dir_vec = note_transform.inverse_transform_vector(cut_dir_vec)
    flag = abs(cut_dir_vec.z) > 10 * abs(cut_dir_vec.x) and abs(cut_dir_vec.z) > 10 * abs(cut_dir_vec.y)
    cut_dir_angle = math.atan2(cut_dir_vec.y, cut_dir_vec.x) * 57.29578
    
    direction_ok = (not flag and -90 - cut_angle_tolerance < cut_dir_angle < cut_angle_tolerance - 90) or (cut_direction == NoteCutDirection.Any)
    speed_ok = saber_blade_speed > kMinBladeSpeedForCut
    saber_type_ok = saber_type == color_type
    cut_dir_deviation = 90 if flag else cut_dir_angle + 90

    if cut_dir_deviation > 180:
        cut_dir_deviation -= 360

    return direction_ok, speed_ok, saber_type_ok, cut_dir_deviation, cut_dir_angle

cut_angle_tolerance = 60 # 40 for strict angles

class NoteObject:
    can_be_cut: bool = True
    finished: bool = False
    event: Bsor.Note

    orientation: Orientation
    big_cuttable: Hitbox
    small_cuttable: Hitbox

    note_data: Note
    id: int
    spawn_time: float

    def __init__(self, map, note, replay, manager):
        self.id = 30000 + note.lineIndex*1000 + note.lineLayer*100 + note.type*10 + note.cutDirection
        self.note_data = note
        self.spawn_time = manager.get_note_time(note)
        self.updater = create_note_orientation_updater(map, note, replay)
        
        self.orientation = Orientation(Vector3(0, 0, 0), Quaternion(0, 0, 0, 1))

        if self.note_data.type == 0 or self.note_data.type == 1:
            if self.note_data.cutDirection == 8:
                self.big_cuttable = Hitbox(Vector3(0.8, 0.8, 1.0), 0.25)
            else:
                self.big_cuttable = Hitbox(Vector3(0.8, 0.5, 1.0), 0.25)
            self.small_cuttable = Hitbox(Vector3(0.35, 0.35, 0.35), 0)
        else:
            self.big_cuttable = Hitbox(Vector3(0.3, 0.3, 0.3), 0)
            self.small_cuttable = Hitbox(Vector3(0.3, 0.3, 0.3), 0)

        self.manager = manager

    def update(self, frame):
        self.updater(frame, self.orientation)
        self.big_cuttable.update(self.orientation)
        self.small_cuttable.update(self.orientation)

    def cut(self, 
            saber: sb.Saber, 
            cut_point: Vector3, 
            orientation: Quaternion, 
            cut_dir_vec: Vector3, 
            allow_bad_cut = True,
            original: Bsor.Note = None):
    
        if not self.can_be_cut:
            return
        
        time_diff = self.spawn_time - saber.time
        direction_ok, speed_ok, saber_type_ok, cut_dir_deviation, cut_dir_angle = get_basic_cut_info(
            self.orientation, 
            self.note_data.type, 
            self.note_data.cutDirection, 
            saber.saber_type, 
            saber.blade_speed, 
            cut_dir_vec, 
            cut_angle_tolerance
        )

        # print(f"{cut_dir_angle}")

        if not (direction_ok and speed_ok and saber_type_ok) and not allow_bad_cut:
            return
        
        if not direction_ok:
            print(f"NOT OK {self.orientation.rotation.to_Euler()}")
            print(f"NOT OK {cut_dir_angle} {saber.time}")

        in_normal = orientation.multiply_point(Vector3(0.0, 1, 0.0))
        plane = Plane(in_normal, cut_point)
        position = self.orientation.position
        distance = abs(plane.get_distance_to_point(position))
        cut_point1 = plane.closest_point_on_plane(self.orientation.position)

        n = Bsor.Note()
        n.note_id = self.id
        n.params = Bsor.NoteParams(n.note_id)
        n.event_time = saber.time
        n.spawn_time = self.spawn_time
        if self.note_data.type == 0 or self.note_data.type == 1:
            n.event_type = Bsor.EventType.Good if (direction_ok and speed_ok and saber_type_ok) else Bsor.EventType.Bad
        else:
            n.event_type = Bsor.EventType.Bomb
        if n.event_type in [Bsor.EventType.Good, Bsor.EventType.Bad]:
            cut = Bsor.Cut()
            cut.speedOK = speed_ok
            cut.directionOk = direction_ok
            cut.saberTypeOk = saber_type_ok
            cut.wasCutTooSoon = False
            cut.saberSpeed = saber.blade_speed
            cut.saberDirection = [cut_dir_vec.x, cut_dir_vec.y, cut_dir_vec.z]
            cut.saberType = saber.saber_type
            cut.timeDeviation = time_diff
            cut.cutDeviation = cut_dir_deviation
            cut.cutPoint = [cut_point1.x, cut_point1.y, cut_point1.z]
            cut.cutNormal = [in_normal.x, in_normal.y, in_normal.z]
            cut.cutDistanceToCenter = distance
            cut.cutAngle = cut_dir_angle
            n.cut = cut
            self.swing_counter = ssrc.SaberSwingRatingCounter(saber.movement_data, self)
        else:
            n.score = Bsor.Score(0, 0, 0)

        self.event = n
        self.can_be_cut = False
        self.manager.active.remove(self)

        # print(f"ot: {original.event_time} pt: {self.event.event_time}")

        # if hasattr(original, "cut") and original.event_type == Bsor.EventType.Good:
        #     print(f"od: {original.cut.saberDirection} pd: {self.event.cut.saberDirection}")
            # print(f"np: {self.orientation.position.z} cp: {cut_point1.z} ocp: {original.cut.cutPoint[2]} oa: {original.cut.afterCutRating} ob: {original.cut.beforeCutRating} dis: {distance} odis: {original.cut.cutDistanceToCenter}")

        if n.event_type not in [Bsor.EventType.Good, Bsor.EventType.Bad]:
            self.finish_cut(0, 0)

    def finish_cut(self, afterCutRating: float, beforeCutRating: float):
        if self.event.event_type in [Bsor.EventType.Good, Bsor.EventType.Bad]:
            self.event.cut.afterCutRating = afterCutRating
            self.event.cut.beforeCutRating = beforeCutRating
            self.event.score = Bsor.calc_note_score(self.event.cut, self.event.params.scoring_type)
        self.manager.finished.append(self)

    def miss(self, time: float):
        n = Bsor.Note()
        n.note_id = self.id
        n.params = Bsor.NoteParams(n.note_id)
        n.event_time = time
        n.spawn_time = self.spawn_time
        n.event_type = Bsor.EventType.Miss
        n.score = Bsor.Score(0, 0, 0)

        self.event = n
        self.can_be_cut = False
        self.manager.active.remove(self)
        self.manager.finished.append(self)


class NoteManager:
    def __init__(self, map_data: Map, replay: Bsor):
        self.active: list[NoteObject] = []
        self.finished: list[NoteObject] = []
        self.beatmap = map_data.beatMaps[replay.info.mode][replay.info.difficulty]
        self.notes = self.beatmap.notes[::-1]
        self.map = map_data
        self.replay = replay
        self.spawn_ahead_time = 1 + self.replay.info.jumpDistance / self.beatmap.noteJumpMovementSpeed * 0.5

    def update(self, frame):
        while len(self.notes) > 0 and frame.time >= self.get_spawn_time(self.notes[-1]):
            new_note = NoteObject(self.map, self.notes.pop(), self.replay, self)
            self.active.append(new_note)

        for note_object in self.active:
            note_object.update(frame)
            if note_object.orientation.position.z < -2:
                if note_object.note_data.type == 0 or note_object.note_data.type == 1:
                    note_object.miss(frame.time)
                else:
                    note_object.can_be_cut = False
                    self.active.remove(note_object)

    def get_note_time(self, note):
        return (note.time * 60 / self.map.beatsPerMinute)

    def get_spawn_time(self, note):
        return (self.get_note_time(note) - self.spawn_ahead_time)
    
    def get_active_notes(self) -> list[NoteObject]:
        result = []
        for note_object in self.active:
            if note_object.can_be_cut and note_object.orientation.position.y > 0:
                result.append(note_object)
        return result
    
    def get_events(self) -> list[Bsor.Note]:
        result = []
        for note_object in self.finished:
            result.append(note_object.event)
        return result

    def get_active_note_by_id(self, id) -> NoteObject:
        for note_object in self.active:
            if note_object.id == id:
                return note_object
        return None
