from main import calculate_score_assuming_valid_times
from Bsor import make_bsor
from interpretMapFiles import create_map


TESTING_PATH = './testData/motion/'

with open(TESTING_PATH + 'replay.bsor', 'rb') as f:
    replay = make_bsor(f)
    f.close()

mapFile = create_map(TESTING_PATH + 'map')

print("Calculated score:", calculate_score_assuming_valid_times(mapFile, replay))
print("Actual score:", replay.info.score)
