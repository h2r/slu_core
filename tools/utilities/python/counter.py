class Counter:
    def __init__(self):
        self.cnt = 0
    def pp(self):
        ret = self.cnt
        self.cnt += 1
        return ret
