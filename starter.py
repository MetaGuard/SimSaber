import numpy as np
import matplotlib.pyplot as plt
from Bsor import make_bsor

with open('sample.bsor', 'rb') as f:
    bsor = make_bsor(f)

ys = [frame.left_hand.y for frame in bsor.frames]

plt.plot(ys[1:3000])
plt.show()
