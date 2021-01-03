from Edge import Edge
from Event import Event

class SiteEvent(Event):
    def __init__(self, x, y):
        self.face = None
        self.x = x
        self.y = y

    def Handle(self, queue, beachline, dcel):
        print("Site Event: " + str(self))
        
        above = beachline.GetParabolaFor(self.x, self.y)

        if above is None: # Check if the beachline tree contains Nothing
            beachline.InsertRootParabola(self)
        else:
            if(above.circleEvent is not None):
                # Delete circle event from priority queue and remove references
                above.circleEvent.Delete(queue)

            # Insert new site's arc under the arc above
            newParabola = beachline.InsertAndSplit(self, above)
            self.AddEdgeForTheNewlyCreatedInternalNode(newParabola, dcel)

            # Find consecutive triplets and if exists, add circle events in the queue
            leftSide = beachline.FindTripletOnLeftSide(newParabola)

            if leftSide is not None:
                circleEvent = leftSide.ComputeCircleEvent()
                if(circleEvent is not None and circleEvent.y <= self.y):
                    circleEvent.Insert(queue)

            rightSide = beachline.FindTripletOnRightSide(newParabola)

            if rightSide is not None:
                circleEvent = rightSide.ComputeCircleEvent()
                if(circleEvent is not None and circleEvent.y <= self.y):
                    circleEvent.Insert(queue)

    def AddEdgeForTheNewlyCreatedInternalNode(self, newArc, dcel):
        edgeForSite = Edge()
        grandParent = newArc.parent.parent
        grandParent.edge = edgeForSite
        dcel.edgeList.append(edgeForSite)
        dcel.edgeList.append(edgeForSite.twin)
    