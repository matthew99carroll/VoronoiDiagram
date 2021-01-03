from PriorityQueue import PriorityQueue
from BeachLine import BeachLine
from DoublyConnectedEdgeList import DoublyConnectedEdgeList
from SiteEvent import SiteEvent
from Face import Face

# Input
input = [[20, 80], [40, 60], [20, 30], [70, 70], [60, 50]]

# Make the event queue
queue = PriorityQueue()
beachline = BeachLine()
dcel = DoublyConnectedEdgeList(0, 0, 100, 100)

for i in range(0, len(input) // 2):
    # Create a new site for this point
    siteEvent = SiteEvent(input[i][0], input[i][1])
    queue.Push(siteEvent)

    # Instantiate and add the face object in the dcel here
    siteEvent.face = Face(siteEvent)
    dcel.faceList.append(siteEvent.face)

while not queue.IsEmpty():
    thisEvent = queue.Pop()
    if thisEvent is not None:
        thisEvent.Handle(queue, beachline, dcel)
    else:
        break

# Complete incomplete faces that may have dangling edges that need to get clipped by the bounds
for face in dcel.faceList:
    face.CompleteFaceIfIncomplete(dcel)

print("Finished computing Voronoi Diagram")