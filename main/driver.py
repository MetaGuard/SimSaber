from bsor.Bsor import Bsor
from interpretMapFiles import Map
from saberMovementBuffer import SaberMovementBuffer
from noteManager import NoteManager
from cutEvent import GoodCutEvent
from scoreManager import ScoreManager


def calculate_score_assuming_valid_times(map_data: Map, replay: Bsor):
    left_hand_buffer = SaberMovementBuffer()
    right_hand_buffer = SaberMovementBuffer()
    note_manager = NoteManager(map_data, replay)
    score_manager = ScoreManager()

    note_events = replay.notes[::-1]

    for frame in replay.frames:
        if len(note_events) == 0:
            break
        left_hand_buffer.add_saber_data(frame.left_hand)
        right_hand_buffer.add_saber_data(frame.right_hand)
        note_manager.update(frame)
        score_manager.update(frame)

        while note_events[-1].spawn_time > frame.time:
            event = note_events.pop()
            note_object = note_manager.get_active_note_by_id(event.note_id)
            note_object.handle_cut()
            if event.cut.saberType == 0:
                score_manager.register_cut_event(GoodCutEvent(note_object.orientation, left_hand_buffer))
            else:
                score_manager.register_cut_event(GoodCutEvent(note_object.orientation, right_hand_buffer))

    return score_manager.get_score()
