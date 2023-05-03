from Bsor import make_bsor, Bsor, save_replay_to_file
from AccuracyCalculator import AccuracyCalculator
from interpretMapFiles import create_map, Map

from Saber import Saber
from NoteCutter import NoteCutter
from noteManager import NoteManager

import requests
import zipfile
import io
import json
import urllib.request
import os

def recalculate_replay(map_data: Map, replay: Bsor) -> int:
    left_saber = Saber(0)
    right_saber = Saber(1)

    note_cutter = NoteCutter()
    note_manager = NoteManager(map_data, replay)
    accuracy_calculator = AccuracyCalculator()
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
        print(f"{count} / {len(frames)}", end='\r')
            

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
                    if round(predicted.cut.cutDistanceToCenter, 2) != round(real.cut.cutDistanceToCenter, 2) or round(predicted.cut.beforeCutRating, 2) != round(real.cut.beforeCutRating, 2):
                        counter += 1
                        print(f"Acc: {real.cut.cutDistanceToCenter:.2f} -> {predicted.cut.cutDistanceToCenter:.2f} Pre: {real.cut.beforeCutRating:.2f} -> {predicted.cut.beforeCutRating:.2f} After: {real.cut.afterCutRating:.2f} -> {predicted.cut.afterCutRating:.2f} ")
                    elif round(predicted.cut.cutPoint[2], 2) != round(real.cut.cutPoint[2], 2):
                        counter += 1
                        print(f"Cut point: {real.cut.cutPoint[2]:.2f} -> {predicted.cut.cutPoint[2]:.2f}")
                break
    
    print(f"Wrong events: {counter} / {len(replay.notes)}")
    replay.notes = events

    return accuracy_calculator.calculate_accuracy(replay)

import sys, getopt

def check_score(score_id: int):
    MAPS_PATH = '.\\maps\\'

    print("Score ID:", score_id)

    # Download file from API with Score ID
    url = f"https://api.beatleader.xyz/score/{score_id}"
    data = json.loads(requests.get(url).text)
    replay_link = data["replay"]

    # Download replay file from link
    replay_path = '.\\replays\\' + str(score_id) + '.bsor'
    if not os.path.isfile(replay_path):
        # add headers to download file
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(replay_link, replay_path)

    with open(replay_path, 'rb') as f:
        replay = make_bsor(f)
        f.close()

    map_hash = replay.info.songHash

    # Check if map is already downloaded
    map_path = MAPS_PATH + map_hash
    if not os.path.isfile(map_path):
        # Download map zip from BeatSaver
        url = f"https://beatsaver.com/api/maps/hash/{map_hash}"
        data = json.loads(requests.get(url).text)
        map_link = data["versions"][0]["downloadURL"]

        r = requests.get(map_link)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(map_path)

    mapFile = create_map(map_path)

    print("Calculated score:", recalculate_replay(mapFile, replay))
    print("Actual score:", replay.info.score)

    save_replay_to_file(replay, ".\\generatedReplays\\generatedwithscore.bsor")

def main(argv):
    score_id = 0
    try:
        opts, args = getopt.getopt(argv, "h", ["scoreId="])
    except getopt.GetoptError:
        print('main.py [--scoreId=<scoreId>]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('main.py [--scoreId=<scoreId>]')
            sys.exit()
        elif opt == '--scoreId':
            score_id = int(arg)

    if not score_id and args:
        try:
            score_id = int(args[0])
        except ValueError:
            print('Invalid scoreId provided.')
            sys.exit(2)
            
    check_score(score_id)


if __name__ == "__main__":
   main(sys.argv[1:])