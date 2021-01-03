class Parabola(Node):
    def __init__(self, siteEvent, parent):
        self.circleEvent = None
        self.siteEvent = siteEvent

    def IsLeaf(self):
        return True

    def Traverse(self, x, y):
        return self

    def ToString(self):
        return "P" + self.siteEvent