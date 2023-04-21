from bsor.Bsor import Bsor
from interpretMapFiles import Map
from .saberMovementBuffer import SaberMovementBuffer
from .noteManager import NoteManager
from .cutEvent import GoodCutEvent
from .scoreManager import ScoreManager
from geometry import Vector3


def calculate_score_assuming_valid_times(map_data: Map, replay: Bsor):
    left_hand_buffer = SaberMovementBuffer()
    right_hand_buffer = SaberMovementBuffer()
    note_manager = NoteManager(map_data, replay)
    score_manager = ScoreManager()

    note_events = replay.notes[::-1]

    print(len(replay.frames))

    count = 0

    for frame in replay.frames[1:]:
        count += 1
        if count % 1000 == 0:
            print(count)
        if len(note_events) == 0:
            break
        left_hand_buffer.add_saber_data(frame.left_hand, frame.time)
        right_hand_buffer.add_saber_data(frame.right_hand, frame.time)
        note_manager.update(frame)
        score_manager.update(frame)

        while note_events[-1].event_time < frame.time:
            event = note_events.pop()
            note_object = note_manager.get_active_note_by_id(event.note_id)
            if note_object is None:
                print(event.note_id, [note.id for note in note_manager.active])
                continue
            print("observed:", note_object.orientation.position)
            print("real:", Vector3(*event.cut.cutPoint))
            print((note_object.orientation.position - Vector3(*event.cut.cutPoint)).mag(), event.cut.cutDistanceToCenter)
            print()
            note_object.handle_cut()
            if event.cut.saberType == 0:
                score_manager.register_cut_event(GoodCutEvent(left_hand_buffer, note_object.orientation))
            else:
                score_manager.register_cut_event(GoodCutEvent(right_hand_buffer, note_object.orientation))

            if len(note_events) == 0:
                break

    print(score_manager.get_avg())
    return score_manager.get_score()
