class Vertex(object):
    def __init__(self, x, y, isLyingOnBounds):
        self.x = x
        self.y = y
        self.isLyingOnBounds = isLyingOnBounds

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.isLyingOnBounds = False

    def ToString(self):
        return '("+x+", "+y+")'
