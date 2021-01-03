import math

from Breakpoint import Breakpoint
from Node import Node


class InternalNode(Node):
    def __init__(self, site1, site2, parent):
        self.parent = parent
        self.site1 = site1
        self.site2 = site2

    def IsLeaf(self):
        return False

    def SiteToString(self):
        return "S" + self.site1 + " " + self.site2

    def ToString(self):
        if self.left is None:
            leftSide = "Left:null"
        elif self.left.IsLeaf():
            leftSide = "Left:" + self.left
        else:
            leftSide = "Left:" + self.left.SiteToString()

        if self.right is None:
            rightSide = "Right:null"
        elif self.right.IsLeaf():
            rightSide = "Right:" + self.right
        else:
            rightSide = "Right:" + self.right.SiteToString()

        return self.SiteToString() + " " + leftSide + " " + rightSide

    def Traverse(self, x, y):
        breakPointX = self.ComputeBreakPointAt(y)

        if x > breakPointX:
            return self.right
        else:
            return self.left

    def Contains(self, siteEvent):
        return self.site1 is siteEvent or self.site2 is siteEvent

    def OtherChild(self, child):
        if self.left is child:
            return self.right
        elif self.right is child:
            return self.left
        else:
            return None

    def OtherSiteEvent(self, siteEvent):
        if siteEvent is self.site1:
            return self.site2
        elif siteEvent is self.site2:
            return self.site1
        else:
            return None

    def Replace(self, siteEvent, siteEventOther):
        if self.site1 is siteEvent:
            self.site1 = siteEventOther
            return True
        elif self.site2 is siteEvent:
            self.site2 = siteEventOther
            return True
        else:
            return False

    def Replace(self, node, nodeOther):
        if self.left is node:
            self.left = nodeOther
            nodeOther.parent = self
            return True
        elif self.right is node:
            self.right = nodeOther
            nodeOther.parent = self
            return True
        else:
            return False

    def IsBreakpointBetween(self, site1, site2):
        return self.site1 is site1 and self.site2 is site2

    """
		 Uses the circle technique to compute the breakpoint.(Deprecated because it only gives one breakpoint)
		 Breakpoint is retrived from the center of the circle touching the two sites and being tangent to the sweep line.
    """

    def ComputeBreakpointUsingCircleTechnique(self, y):
        # by substituting site1 and site 2 in the equation of the circle and substituting the y value of the sweepline
        # we can get the x value of the point at which the circle touches the sweep line or in otherwords the x of the center
        x = ((self.site2.x * self.site2.x) + (self.site2.y * self.site2.y) - (self.site1.x * self.site1.x) - (
                    self.site1.y * self.site1.y) + 2 * (self.site1.y) * y - 2 * (self.site2.y) * y) / (
                        2 * (self.site2.x - self.site1.x))

        # now we use the x value in the equation of the perpendicular bisector between the two sites to get the y of the center
        site = self.site1

        if self.site1.x == x:
            # to prevent divide by zero error while calculating slope
            site = self.site2  # assuming the perpendicular bisector will never be a vertical line with infinite slope

        mx = (site.x + x) / 2
        my = (site.y + y) / 2
        slope = (site.y - y) / (site.x - x)
        inverseSlope = -1 / slope
        c = my - inverseSlope * mx

        # perpendicular bisector of a chord will always pass through the center of a circle
        centerY = inverseSlope * x + c

        return Breakpoint(x, centerY)

    """
    Uses the equation of parabola to compute the x value of the breakpoint.
    """

    def ComputeBreakpointAt(self, y):

        # we use the equation of the parabola to get the intersection of the two arcs
        d = 2 * (self.site1.y - y)
        a1 = 1 / d
        b1 = -2 * self.site1.x / d
        c1 = y + d / 4 + self.site1.x * self.site1.x / d

        d = 2 * (self.site2.y - y)
        a2 = 1 / d
        b2 = -2 * self.site2.x / d
        c2 = y + d / 4 + self.site2.x * self.site2.x / d  # minor adjustment

        a = a1 - a2
        b = b1 - b2
        c = c1 - c2

        # since this is a quadratic equation, so it will have 2 solutions
        discremenant = b * b - 4 * a * c
        x1 = (-b + math.sqrt(discremenant)) / (2 * a)
        x2 = (-b - math.sqrt(discremenant)) / (2 * a)

        # the two solutions are basically the left and the right breakpoint values (just x)
        if self.site1.x <= self.site2.x:
            return math.min(x1, x2)
        else:
            return math.max(x1, x2)
