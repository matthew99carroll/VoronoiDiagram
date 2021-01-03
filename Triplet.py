import Parabola
import PerpindicularBisector
import CircleEvent
import math

class Triplet(object):
    def __init__(self, left, middle, right):
        self.left = left
        self.middle = middle
        self.right = right

    def ComputeCircleEvent(self):

        # Make sure the three arcs have distinct site events
        if (self.left.siteEvent is self.right.siteEvent) or (self.left.siteEvent is self.middle.siteEvent) or (self.middle.siteEvent is self.right.siteEvent):
            return None

        # Its possible that the three parabola nodes considered are not consecutive because one outlier's(left or right) site event 
		# is situated over on the other side, in which case, the the middle arc is not formed "at" the beachline but within it.
		# For this purpose we make a simple check. if left-> middle-> right is counter clockwise, then we return null.
        if (self.left.siteEvent.y - self.middle.siteEvent.y) * (self.right.siteEvent.x - self.middle.siteEvent.x) >= (self.left.siteEvent.x-self.middle.siteEvent.x)*(self.right.siteEvent.y-self.middle.siteEvent.y):
            return None

        # Get the equations of the two perpindicular bisectors
        p1 = PerpindicularBisector(self.left.siteEvent.x, self.left.siteEvent.y, self.middle.siteEvent.x, self.middle.siteEvent.y)
        p2 = PerpindicularBisector(self.right.siteEvent.x, self.right.siteEvent.y, self.middle.siteEvent.x, self.middle.siteEvent.y)

        # Find out the intersection point of the perpindicular bisectors to get the center of the circle
        center = p1.GetIntersectionPoint(p2)

        # Get the radius by finding the difference between any point and the center
        radius = math.sqrt((center.x-self.left.siteEvent.x)*(center.x-self.left.siteEvent.x)+(center.y-self.left.siteEvent.y)*(center.y-self.left.siteEvent.y))
        return CircleEvent(center.x, center.y, radius, self)