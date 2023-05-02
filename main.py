from Bsor import make_bsor, Bsor, save_replay_to_file
from AccuracyCalculator import calculate_accuracy
from interpretMapFiles import create_map, Map

from Saber import Saber
from NoteCutter import NoteCutter
from noteManager import NoteManager
from scoreManager import ScoreManager

def calculate_score(map_data: Map, replay: Bsor) -> int:
    left_saber = Saber(0)
    right_saber = Saber(1)

    note_cutter = NoteCutter()
    note_manager = NoteManager(map_data, replay)

    print("# frames:", len(replay.frames))

    count = 0

    frames = replay.frames

    for frame in frames:
        
        if count > 0:
            note_cutter.cut(left_saber, note_manager, replay)
            note_cutter.cut(right_saber, note_manager, replay)

        left_saber.manual_update(frame.left_hand, frame.time)
        right_saber.manual_update(frame.right_hand, frame.time)

        

        note_manager.update(frame)

        

        count += 1
        if count % 1000 == 0:
            print("Processed Frame:", count)

    events = note_manager.get_events()
    counter = 0

    for real in replay.notes:
        for predicted in events:
            if predicted.note_id == real.note_id and abs(predicted.spawn_time - real.spawn_time) < 0.01:
                if predicted.event_type != real.event_type or predicted.event_time != real.event_time:
                    # print(f"Predicted: {predicted.score.value}, Real: {real.score.value}. {predicted.cut.cutPoint} {real.cut.cutPoint}")
                    print(f"Time: {real.event_time} -> {predicted.event_time} Event: {real.event_type} -> {predicted.event_type}")
                    counter += 1
                elif hasattr(predicted, 'cut') and hasattr(real, 'cut'):
                    if round(predicted.cut.cutDistanceToCenter, 2) != round(real.cut.cutDistanceToCenter, 2):
                        counter += 1
                        print(f"Acc: {real.cut.cutDistanceToCenter:.2f} -> {predicted.cut.cutDistanceToCenter:.2f} Pre: {real.cut.beforeCutRating:.2f} -> {predicted.cut.beforeCutRating:.2f} After: {real.cut.afterCutRating:.2f} -> {predicted.cut.afterCutRating:.2f} ")
                    elif round(predicted.cut.cutPoint[2], 2) != round(real.cut.cutPoint[2], 2):
                        counter += 1
                        print(f"Cut point: {real.cut.cutPoint[2]:.2f} -> {predicted.cut.cutPoint[2]:.2f}")
                break
    
    print(f"Wrong events: {counter} / {len(replay.notes)}")
    replay.notes = events

    return calculate_accuracy(replay)[-1].total_score

MAP_PATH = '.\\generatedReplays\\1677a (Bang! - BrightKnight)'
REPLAY_PATH = '.\\generatedReplays\\replay.bsor'

with open(REPLAY_PATH, 'rb') as f:
    replay = make_bsor(f)
    f.close()

# replay.info.playerId = '19573' # PP bot ID

mapFile = create_map(MAP_PATH)

print("Calculated score:", calculate_score(mapFile, replay))
print("Actual score:", replay.info.score)

save_replay_to_file(replay, ".\\generatedReplays\\generatedwithscore.bsor")