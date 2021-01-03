class Face(object):
    def __init__(self, siteEvent):
        self.siteEvent = siteEvent

        self.start = None
        self.last = None
        self.forwardList = None
        self.backwardList = None
        self.startTerminal = None
        self.endTerminal = None

    def ToString(self):
        return "F" + self.siteEvent

    def GetStartingEdge(self):
        return self.start

    def GetForwardTerminal(self):
        return self.startTerminal

    def GetBackwardTerminal(self):
        return self.endTerminal

    def AppendToForwardList(self, edge):
        edge.face = self
        edge.next = None
        edge.previous = None

        if self.forwardList is None:
            self.forwardList = edge
        else:
            self.startTerminal.next = edge
            edge.previous = self.startTerminal

        self.startTerminal = edge
    
    def PrependToBackwardList(self, edge, originOfDanglingLast):
        edge.face = self
        edge.next = None
        edge.previous = None

        if self.backwardList is None:
            self.backwardList = edge
        else:
            self.endTerminal.origin = originOfDanglingLast
            self.endTerminal.previous = edge
            edge.next = self.endTerminal

        self.endTerminal = edge

    def CreateForwardAndBackwardListsAt(self, origin, endingEdge, startingEdge):
        startingEdge.origin = origin

        self.start = startingEdge
        self.forwardList = startingEdge
        self.startTerminal = startingEdge

        self.last = endingEdge
        self.backwardList = endingEdge
        self.endTerminal = endingEdge

        endingEdge.next = startingEdge
        startingEdge.previous = endingEdge

    def ConnectBackwardAndForwardListsAt(self, originOfDanglingLast):
        self.endTerminal.origin = originOfDanglingLast
        self.startTerminal.next = self.endTerminal

    def ForwardListNotStarted(self):
        return self.forwardList is None

    def BackwardListNotStarted(self):
        return self.backwardList is None