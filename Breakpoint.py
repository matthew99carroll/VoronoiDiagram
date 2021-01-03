class Breakpoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def ToString(self):
        return '("+x+", "+y+")'
