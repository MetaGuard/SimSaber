from typing import *
from enum import Enum
import typing
import struct

MAGIC_HEX = '0x442d3d69'


def decode_int(fa: typing.BinaryIO) -> int:
    bytes = fa.read(4)
    return int.from_bytes(bytes, 'little')


def decode_long(fa: typing.BinaryIO) -> int:
    bytes = fa.read(8)
    return int.from_bytes(bytes, 'little')


def decode_byte(fa: typing.BinaryIO) -> int:
    bytes = fa.read(1)
    return int.from_bytes(bytes, 'little')


def decode_bool(fa: typing.BinaryIO) -> bool:
    return 1 == decode_byte(fa)


def decode_string(fa: typing.BinaryIO) -> str:
    length = decode_int(fa)
    if length == 0:
        return ''
    result = fa.read(length)
    result = result.decode("utf-8")
    return result


# thanks https://github.com/Metalit/Replay/commit/3d63185c7a5863c1e3964e8e228f2d9dd8769168
def decode_string_maybe_utf16(fa: typing.BinaryIO) -> str:
    length = decode_int(fa)
    if length == 0:
        return ''
    result = list(fa.read(length))

    next_string_len= decode_int(fa)
    while next_string_len < 0 or next_string_len > 100:
        fa.seek(-4, 1)
        result.append(decode_byte(fa))
        next_string_len= decode_int(fa)
    fa.seek(-4, 1)

    result = bytes(result).decode("utf-8")
    return result


def decode_float(fa: typing.BinaryIO) -> float:
    bytes = fa.read(4)
    try:
        result = struct.unpack('f', bytes)
    except:
        raise
    return result[0]


def decode_list(f, m) -> List:
    cnt = decode_int(f)
    return [m(f) for _ in range(cnt)]


class BSException(BaseException):
    pass


class Info:
    version: str
    gameVersion: str
    timestamp: str

    playerId: str
    playerName: str
    platform: str

    trackingSystem: str
    hmd: str
    controller: str

    songHash: str
    songName: str
    mapper: str
    difficulty: str

    score: int
    mode: str
    environment: str
    modifiers: str
    jumpDistance: float
    leftHanded: bool
    height: float

    startTime: float
    failTime: float
    speed: float


def make_info(f) -> Info:
    info_start = decode_byte(f)

    if info_start != 0:
        raise BSException('info doesnt start with 0: %d' % info_start)
    info = Info()
    info.version = decode_string(f)
    info.gameVersion = decode_string(f)
    info.timestamp = decode_string(f)

    info.playerId = decode_string(f)
    info.playerName = decode_string_maybe_utf16(f)
    info.platform = decode_string(f)

    info.trackingSystem = decode_string(f)
    info.hmd = decode_string(f)
    info.controller = decode_string(f)

    info.songHash = decode_string(f)
    info.songName = decode_string_maybe_utf16(f)
    info.mapper = decode_string_maybe_utf16(f)
    info.difficulty = decode_string(f)

    info.score = decode_int(f)
    info.mode = decode_string(f)
    info.environment = decode_string(f)
    info.modifiers = decode_string(f)
    info.jumpDistance = decode_float(f)

    info.leftHanded = decode_bool(f)
    info.height = decode_float(f)

    info.startTime = decode_float(f)
    info.failTime = decode_float(f)
    info.speed = decode_float(f)

    return info


class VRObject:
    x: float
    y: float
    z: float
    x_rot: float
    y_rot: float
    z_rot: float
    w_rot: float

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_rot = 0
        self.y_rot = 0
        self.z_rot = 0
        self.w_rot = 0


    def to_array(self, height = 0):
        return [self.x, self.y - height, self.z, self.w_rot, self.x_rot, self.y_rot, self.z_rot]


def make_vr_object(f) -> VRObject:
    v = VRObject()
    v.x = decode_float(f)
    v.y = decode_float(f)
    v.z = decode_float(f)
    v.x_rot = decode_float(f)
    v.y_rot = decode_float(f)
    v.z_rot = decode_float(f)
    v.w_rot = decode_float(f)
    return v


class Frame:
    time: float
    fps: int
    head: VRObject
    left_hand: VRObject
    right_hand: VRObject

    def __init__(self):
        self.time = 0
        self.fps = 0
        self.head = VRObject()
        self.left_hand = VRObject()
        self.right_hand = VRObject()

    def to_array(self, previous_frame, height = 0):
        input_features = [self.time - previous_frame.time]
        input_features.extend(self.head.to_array(height))
        input_features.extend(self.left_hand.to_array(height))
        input_features.extend(self.right_hand.to_array(height))

        return  input_features


def make_frames(f) -> List[Frame]:
    frames_start = decode_byte(f)
    if frames_start != 1:
        raise BSException('frames dont start with 1')
    result = decode_list(f, make_frame)
    return result


def make_frame(f) -> Frame:
    fr = Frame()
    fr.time = decode_float(f)
    fr.fps = decode_int(f)
    fr.head = make_vr_object(f)
    fr.left_hand = make_vr_object(f)
    fr.right_hand = make_vr_object(f)
    return fr


class Cut:
    speedOK: bool
    directionOk: bool
    saberTypeOk: bool
    wasCutTooSoon: bool
    saberSpeed: float
    saberDirection: typing.List
    saberType: int
    timeDeviation: float
    cutDeviation: float
    cutPoint: typing.List
    cutNormal: typing.List
    cutDistanceToCenter: float
    cutAngle: float
    beforeCutRating: float
    afterCutRating: float


class EventType(Enum):
    Good = 0
    Bad = 1
    Miss = 2
    Bomb = 3


class ScoringType(Enum):
    Normal1 = 0
    Ignore = 1
    NoScore = 2
    Normal2 = 3
    SliderHead = 4
    SliderTail = 5
    BurstSliderHead = 6
    BurstSliderElement = 7


class NoteParams:
    scoring_type: ScoringType
    line_index: int
    note_line_layer: int
    color_type: int
    cut_direction: int

    def __init__(self, note_id: int):
        if note_id < 100000:
            self.scoring_type = ScoringType(note_id // 10000)
            note_id -= self.scoring_type.value * 10000

            self.line_index = note_id // 1000
            note_id -= self.line_index * 1000

            self.note_line_layer = note_id // 100
            note_id -= self.note_line_layer * 100

            self.color_type = note_id // 10
            self.cut_direction = note_id - self.color_type * 10
        else:
            self.scoring_type = ScoringType(note_id // 10000000)
            note_id -= self.scoring_type.value * 10000000

            self.line_index = note_id // 1000000
            note_id -= self.line_index * 1000000

            self.note_line_layer = note_id // 100000
            note_id -= self.note_line_layer * 100000

            self.color_type = note_id // 10
            self.cut_direction = note_id - self.color_type * 10


class Score:
    pre_score: int
    post_score: int
    acc_score: int
    value: int

    def __init__(self, pre_score: int, post_score: int, acc_score: int):
        self.pre_score = pre_score
        self.post_score = post_score
        self.acc_score = acc_score
        self.value = pre_score + post_score + acc_score


class Note:
    note_id: int
    params: NoteParams
    event_time: float
    spawn_time: float
    event_type: EventType
    cut: Cut
    score: Score


def make_notes(f) -> List[Note]:
    notes_starter = decode_byte(f)
    if notes_starter != 2:
        raise BSException('notes_magic dont start with 2')

    result = decode_list(f, make_note)
    return result


def make_note(f) -> Note:
    n = Note()
    n.note_id = decode_int(f)
    n.params = NoteParams(n.note_id)
    n.event_time = decode_float(f)
    n.spawn_time = decode_float(f)
    n.event_type = EventType(decode_int(f))
    if n.event_type in [EventType.Good, EventType.Bad]:
        n.cut = make_cut(f)
        n.score = calc_note_score(n.cut, n.params.scoring_type)
    else:
        n.score = Score(0, 0, 0)

    return n


def clamp(n, smallest, largest):
    return sorted([smallest, n, largest])[1]


def round_half_up(f: float) -> int:
    a = f % 1
    if a < 0.5:
        return int(f)
    else:
        return int(f+1)


def calc_note_score(cut: Cut, scoring_type: ScoringType) -> Score:
    if not cut.directionOk or not cut.saberTypeOk or not cut.speedOK:
        return Score(0, 0, 0)
    before_cut_raw_score = 0
    if scoring_type != ScoringType.BurstSliderElement:
        if scoring_type == ScoringType.SliderTail:
            before_cut_raw_score = 70
        else:
            before_cut_raw_score = 70 * cut.beforeCutRating
            before_cut_raw_score = round_half_up(before_cut_raw_score)
            before_cut_raw_score = clamp(before_cut_raw_score, 0, 70)

    after_cut_raw_score = 0
    if scoring_type != ScoringType.BurstSliderElement:
        if scoring_type == ScoringType.BurstSliderHead:
            after_cut_raw_score = 0
        elif scoring_type == ScoringType.SliderHead:
            after_cut_raw_score = 30
        else:
            after_cut_raw_score = 30 * cut.afterCutRating
            after_cut_raw_score = round_half_up(after_cut_raw_score)
            after_cut_raw_score = clamp(after_cut_raw_score, 0, 30)

    if scoring_type == ScoringType.BurstSliderElement:
        cut_distance_raw_score = 20
    else:
        cut_distance_raw_score = cut.cutDistanceToCenter / 0.3
        cut_distance_raw_score = 1-clamp(cut_distance_raw_score, 0, 1)
        cut_distance_raw_score = round_half_up(15 * cut_distance_raw_score)

    return Score(before_cut_raw_score, after_cut_raw_score, cut_distance_raw_score)


def make_cut(f) -> Cut:
    c = Cut()
    c.speedOK = decode_bool(f)
    c.directionOk = decode_bool(f)
    c.saberTypeOk = decode_bool(f)
    c.wasCutTooSoon = decode_bool(f)
    c.saberSpeed = decode_float(f)
    c.saberDirection = [decode_float(f) for _ in range(3)]
    c.saberType = decode_int(f)
    c.timeDeviation = decode_float(f)
    c.cutDeviation = decode_float(f)
    c.cutPoint = [decode_float(f) for _ in range(3)]
    c.cutNormal = [decode_float(f) for _ in range(3)]
    c.cutDistanceToCenter = decode_float(f)
    c.cutAngle = decode_float(f)
    c.beforeCutRating = decode_float(f)
    c.afterCutRating = decode_float(f)
    return c


class Wall:
    id: int
    energy: float
    time: float
    spawnTime: float


def make_walls(f) -> List[Wall]:
    wall_magic = decode_byte(f)
    if wall_magic != 3:
        raise BSException('walls_magic not 3')
    return decode_list(f, make_wall)


def make_wall(f) -> Wall:
    w = Wall()
    w.id = decode_int(f)
    w.energy = decode_float(f)
    w.time = decode_float(f)
    w.spawnTime = decode_float(f)
    return w


class Height:
    height: float
    time: float


def make_heights(f) -> List[Height]:
    magic = decode_byte(f)
    if magic != 4:
        raise BSException('height_magic not 4')
    return decode_list(f, make_height)


def make_height(f) -> Height:
    h = Height()
    h.time = decode_float(f)
    h.height = decode_float(f)
    return h


class Pause:
    duration: int
    time: float


def make_pauses(f) -> List[Pause]:
    magic = decode_byte(f)
    if magic != 5:
        raise BSException('pause_magic not 5')
    return decode_list(f, make_pause)


def make_pause(f) -> Pause:
    p = Pause()
    p.duration = decode_long(f)
    p.time = decode_float(f)
    return p


class Bsor:
    magic_numer: int
    file_version: int
    info: Info
    frames: List[Frame]
    notes: List[Note]
    walls: List[Wall]
    heights: List[Height]
    pauses: List[Pause]


def make_bsor(f: typing.BinaryIO) -> Bsor:
    m = Bsor()

    m.magic_numer = decode_int(f)
    if hex(m.magic_numer) != MAGIC_HEX:
        raise BSException('File Magic number doesnt match (is %s, should be %s)' % (hex(m.magic_numer), MAGIC_HEX))
    m.file_version = decode_byte(f)
    if m.file_version != 1:
        raise BSException('version %d not supported' % m.file_version)
    m.info = make_info(f)
    m.frames = make_frames(f)
    m.notes = make_notes(f)
    m.walls = make_walls(f)
    m.heights = make_heights(f)
    m.pauses = make_pauses(f)

    return m

import struct
from typing import List


def encode(replay, stream):
    stream.write(struct.pack('<I', 0x442d3d69))
    stream.write(struct.pack('<B', 1))

    for a in range(7):  # StructType enum has 7 elements
        struct_type = a
        stream.write(struct.pack('<B', a))

        if struct_type == 0:
            encode_info(replay.info, stream)
        elif struct_type == 1:
            encode_frames(replay.frames, stream)
        elif struct_type == 2:
            encode_notes(replay.notes, stream)
        elif struct_type == 3:
            encode_walls(replay.walls, stream)
        elif struct_type == 4:
            encode_heights(replay.heights, stream)
        elif struct_type == 5:
            encode_pauses(replay.pauses, stream)


def encode_info(info, stream):
    encode_string(info.version, stream)
    encode_string(info.gameVersion, stream)
    encode_string(info.timestamp, stream)
    encode_string(info.playerId, stream)

    encode_string(info.playerName, stream)
    encode_string(info.platform, stream)
    encode_string(info.trackingSystem, stream)
    encode_string(info.hmd, stream)

    encode_string(info.controller, stream)
    encode_string(info.songHash, stream)
    encode_string(info.songName, stream)
    encode_string(info.mapper, stream)
    encode_string(info.difficulty, stream)

    stream.write(struct.pack('<I', info.score))

    encode_string(info.mode, stream)
    encode_string(info.environment, stream)
    encode_string(info.modifiers, stream)

    stream.write(struct.pack('<f', info.jumpDistance))
    stream.write(struct.pack('<B', info.leftHanded))
    stream.write(struct.pack('<f', info.height))

    stream.write(struct.pack('<f', info.startTime))
    stream.write(struct.pack('<f', info.failTime))
    stream.write(struct.pack('<f', info.speed))


def encode_frames(frames, stream):
    stream.write(struct.pack('<I', len(frames)))
    for frame in frames:
        stream.write(struct.pack('<f', frame.time))
        stream.write(struct.pack('<I', frame.fps))

        for vector in [frame.head,
                       frame.left_hand,
                       frame.right_hand]:
            encode_vector(vector, stream)


def encode_notes(notes, stream):
    stream.write(struct.pack('<I', len(notes)))
    for note in notes:
        stream.write(struct.pack('<I', note.note_id))
        stream.write(struct.pack('<f', note.event_time))
        stream.write(struct.pack('<f', note.spawn_time))
        stream.write(struct.pack('<i', note.event_type.value))

        if note.event_type in [EventType.Good, EventType.Bad]:
            encode_note_info(note.cut, stream)


def encode_walls(walls, stream):
    stream.write(struct.pack('<I', len(walls)))
    for wall in walls:
        stream.write(struct.pack('<I', wall.id))
        stream.write(struct.pack('<f', wall.energy))
        stream.write(struct.pack('<f', wall.time))
        stream.write(struct.pack('<f', wall.spawnTime))


def encode_heights(heights, stream):
    stream.write(struct.pack('<I', len(heights)))
    for height in heights:
        stream.write(struct.pack('<f', height.height))
        stream.write(struct.pack('<f', height.time))


def encode_pauses(pauses, stream):
    stream.write(struct.pack('<I', len(pauses)))
    for pause in pauses:
        stream.write(struct.pack('<f', pause.duration))
        stream.write(struct.pack('<f', pause.time))


def encode_note_info(info, stream):
    stream.write(struct.pack('<B', info.speedOK))
    stream.write(struct.pack('<B', info.directionOk))
    stream.write(struct.pack('<B', info.saberTypeOk))
    stream.write(struct.pack('<B', info.wasCutTooSoon))
    stream.write(struct.pack('<f', info.saberSpeed))
    encode_vector3(info.saberDirection, stream)
    stream.write(struct.pack('<I', info.saberType))
    stream.write(struct.pack('<f', info.timeDeviation))
    stream.write(struct.pack('<f', info.cutDeviation))
    encode_vector3(info.cutPoint, stream)
    encode_vector3(info.cutNormal, stream)
    stream.write(struct.pack('<f', info.cutDistanceToCenter))
    stream.write(struct.pack('<f', info.cutAngle))
    stream.write(struct.pack('<f', info.beforeCutRating))
    stream.write(struct.pack('<f', info.afterCutRating))


def encode_string(value, stream):
    value = value or ''
    encoded_str = value.encode('utf-8')
    stream.write(struct.pack('<i', len(encoded_str)))
    stream.write(encoded_str)


def encode_vector3(vector, stream):
    stream.write(struct.pack('<f', vector[0]))
    stream.write(struct.pack('<f', vector[1]))
    stream.write(struct.pack('<f', vector[2]))


def encode_vector(vector, stream):
    stream.write(struct.pack('<f', vector.x))
    stream.write(struct.pack('<f', vector.y))
    stream.write(struct.pack('<f', vector.z))
    stream.write(struct.pack('<f', vector.x_rot))
    stream.write(struct.pack('<f', vector.y_rot))
    stream.write(struct.pack('<f', vector.z_rot))
    stream.write(struct.pack('<f', vector.w_rot))


import io

def save_replay_to_file(replay: Bsor, output_filename: str):
    with open(output_filename, "wb") as output_file:
        stream = io.BytesIO()
        encode(replay, stream)

        # Write the binary data to the output file
        output_file.write(stream.getvalue())


