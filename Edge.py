class Edge(object):
    # Private so that it is only used internally and doesn't become recursive
    def _edge(self, twin):
        self.twin = twin

    def __init__(self, origin = None, dontCreateTwin = False):
        if (not dontCreateTwin):
            self.twin = self._edge(self)
        self.origin = origin

    def ForFace(self, face):
        if self.face is face:
            return self
        elif self.twin.face is face:
            return self.twin
        else:
            return None

    def ToString(self):
        return "E" + self.face + " " + self.origin