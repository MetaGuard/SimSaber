from Bsor import *


class NoteStruct:
    is_block: bool
    time: float
    spawn_time: float

    multiplier: float
    total_score: int
    accuracy: float
    combo: int

    note_event: Note

    def __init__(self, time: float, spawn_time: float, is_block: bool = False, note_event: Note = None):
        self.time = time
        self.spawn_time = spawn_time
        self.is_block = is_block
        self.note_event = note_event


class MultiplierCounter:
    multiplier: int = 1

    multiplier_increase_progress: int = 0
    multiplier_increase_max_progress: int = 2

    def increase(self):
        if self.multiplier >= 8:
            return
        if self.multiplier_increase_progress < self.multiplier_increase_max_progress:
            self.multiplier_increase_progress += 1
        if self.multiplier_increase_progress >= self.multiplier_increase_max_progress:
            self.multiplier *= 2
            self.multiplier_increase_progress = 0
            self.multiplier_increase_max_progress = self.multiplier * 2

    def decrease(self):
        if self.multiplier_increase_progress > 0:
            self.multiplier_increase_progress = 0
        if self.multiplier > 1:
            self.multiplier /= 2
            self.multiplier_increase_max_progress = self.multiplier * 2


def calculate_accuracy(replay: Bsor) -> list[NoteStruct]:
    all_structs: list[NoteStruct] = []

    for note in replay.notes:
        all_structs.append(NoteStruct(note.event_time, note.spawn_time, note.params.color_type != 2, note))

    for wall in replay.walls:
        all_structs.append(NoteStruct(wall.time, wall.spawnTime))

    all_structs = sorted(all_structs, key=lambda item: item.time)

    score: int = 0
    note_index: int = 0
    combo: int = 0
    max_combo: int = 0
    max_score: int = 0
    max_counter: MultiplierCounter = MultiplierCounter()
    normal_counter: MultiplierCounter = MultiplierCounter()

    for i in range(0, len(all_structs)):
        note = all_structs[i]

        score_for_max_score = 20 if note.note_event is not None and note.note_event.params.scoring_type == ScoringType.BurstSliderElement else 115
        max_counter.increase()
        max_score += max_counter.multiplier * score_for_max_score

        if note.note_event is None or note.note_event.event_type != EventType.Good:
            normal_counter.decrease()
            multiplier = normal_counter.multiplier
            combo = 0
        else:
            normal_counter.increase()
            combo += 1
            multiplier = normal_counter.multiplier
            score += multiplier * note.note_event.score.value

        if combo > max_combo:
            max_combo = combo

        note.multiplier = multiplier
        note.total_score = score
        note.combo = combo

        if note.is_block:
            note.accuracy = note.total_score / max_score
            note_index += 1
        else:
            note.accuracy = 0 if i == 0 else all_structs[i - 1].accuracy

    return all_structs