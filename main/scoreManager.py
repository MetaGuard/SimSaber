

class ComboManager:
    def __init__(self):
        self.meter = 0

    def multiplier(self):
        if self.meter == 0:
            return 1
        if self.meter < 5:
            return 2
        if self.meter < 13:
            return 4
        return 8

    def __rmul__(self, x):
        return x * self.multiplier()

    def __mul__(self, x):
        return x * self.multiplier()

    def increment(self):
        self.meter += 1

    def decrement(self):
        if self.meter < 5:
            self.meter = 0
        if self.meter < 13:
            self.meter = 1
        self.meter = 5


class ScoreManager:
    def __init__(self):
        self.combo = ComboManager()
        self.active_cut_events = []
        self.score = 0

    def register_cut_event(self, cut_event):
        self.active_cut_events.append(cut_event)

    def update(self, frame):
        for cut_event in self.active_cut_events:
            cut_event.update(frame)
            if cut_event.finished:
                self.combo.increment()
                self.score += cut_event.get_score() * self.combo

    def get_score(self):
        return self.score
