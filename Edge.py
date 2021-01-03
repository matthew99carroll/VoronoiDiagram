class Edge(object):
    # Private so that it is only used internally and doesn't become recursive
    def _edge(self, twin):
        self.twin = twin

    def __init__(self):
        self.twin = Edge(self)

    def __init__(self, origin):
        self.origin = origin
        self.twin = Edge(self)

    def __init__(self, origin, dontCreateTwin):
        self.origin = origin
        if(not dontCreateTwin):
            self.twin = Edge(self)

    def ForFace(self, face):
        if self.face is face:
            return self
        elif self.twin.face is face:
            return twin
        else:
            return null

    def ToString(self):
        return "E" + self.face + " " + self.origin