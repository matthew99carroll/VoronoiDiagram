import Point


class PerpindicularBisector(object):
    def __init__(self, x1, y1, x2, y2):
        self.m = None
        self.c = None
        self.horizontalLine = False
        self.verticalLine = False
        self.level = None

        if x1 - x2 is 0:
            self.horizontalLine = True
            self.level = (y1 + y2) / 2
        elif (y1 - y2 is 0):
            self.verticalLine = True
            self.level = (x1 + x2) / 2
        else:
            # Midpoint
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            # Inverse slope
            normalSlope = (y1 - y2) / (x1 - x2)
            m = -(1 / normalSlope)

            # Substitute midpoint to get c
            c = my - self.m * mx

    def GetIntersectionPoint(self, lineEquation):
        x = None
        y = None

        if self.horizontalLine:
            if lineEquation.verticalLine:
                x = lineEquation.level
                y = self.level
            elif lineEquation.horizontalLine:
                return None
            else:
                y = self.level
                x = (y - lineEquation.c) / lineEquation.m
        elif self.verticalLine:
            if lineEquation.verticalLine:
                return None
            elif lineEquation.horizontalLine:
                x = self.level
                y = lineEquation.level
            else:
                y = self.level
                x = (y - lineEquation.c) / lineEquation.m
        else:
            if lineEquation.verticalLine:
                x = lineEquation.level
                y = self.m * x + self.c
            elif lineEquation.horizontalLine:
                y = lineEquation.level
                x = (y - self.c) / self.m
            else:
                x = (self.c - lineEquation.c) / (lineEquation.m - self.m)
                y = self.m * x + self.c

        return Point(x, y)

    def ToString(self):
        return self.left + " " + self.middle + " " + self.right
