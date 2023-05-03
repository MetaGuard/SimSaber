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


class AccuracyCalculator:
    def __init__(self):
        self.all_structs: list[NoteStruct] = []
        self.score: int = 0
        self.note_index: int = 0
        self.combo: int = 0
        self.max_combo: int = 0
        self.max_score: int = 0
        self.max_counter: MultiplierCounter = MultiplierCounter()
        self.normal_counter: MultiplierCounter = MultiplierCounter()

    def calculate_for_index(self, i: int):
        note = self.all_structs[i]

        score_for_max_score = 20 if note.note_event is not None and note.note_event.params.scoring_type == ScoringType.BurstSliderElement else 115
        self.max_counter.increase()
        self.max_score += self.max_counter.multiplier * score_for_max_score

        if note.note_event is None or note.note_event.event_type != EventType.Good:
            self.normal_counter.decrease()
            multiplier = self.normal_counter.multiplier
            self.combo = 0
        else:
            self.normal_counter.increase()
            self.combo += 1
            multiplier = self.normal_counter.multiplier
            self.score += multiplier * note.note_event.score.value

        if self.combo > self.max_combo:
            self.max_combo = self.combo

        note.multiplier = multiplier
        note.total_score = self.score
        note.combo = self.combo

        if note.is_block:
            note.accuracy = note.total_score / self.max_score
        else:
            note.accuracy = 0 if i == 0 else self.all_structs[i - 1].accuracy

    def add_new_note(self, note: Note):
        self.all_structs.append(NoteStruct(note.event_time, note.spawn_time, note.params.color_type != 2, note))
        self.calculate_for_index(len(self.all_structs) - 1)

    def calculate_accuracy(self, replay: Bsor):
        for note in replay.notes:
            self.all_structs.append(NoteStruct(note.event_time, note.spawn_time, note.params.color_type != 2, note))

        for wall in replay.walls:
           self. all_structs.append(NoteStruct(wall.time, wall.spawnTime))

        self.all_structs.sort(key=lambda item: item.time)

        for i in range(len(self.all_structs)):
            self.calculate_for_index(i)

        return self.all_structs[-1].total_score