class DoublyConnectedEdgeList(object):
    def __init__(self, lx, ly, ux, uy):
        self.lx = lx
        self.ly = ly
        self.ux = ux
        self.uy = uy

        self.vertexList = []
        self.faceList = []
        self.edgeList = []

    def ToString(self):
        return "V: " + self.vertexList.count + "E: " + self.edgeList.count + "F: " + self.faceList.count

    def GetXOfParabolaIntersectionGivenY(self, site1, site2, y):
        # using the equation of the parabola we find the x by substituting out the directix
        return (site2.x * site2.x - site1.x * site1.x + site2.y * site2.y - site1.y * site1.y - 2 * site2.y * y + 2 * site1.y * y) / (2 * (site2.x - site1.x))

    def GetYOfParabolaIntersectionGivenX(self, site1, site2, x):
        # using the equation of the parabola we find the y by substituting out the directix
        return (site1.x * site1.x - site2.x * site2.x + site1.y * site1.y - site2.y * site2.y + 2 * site2.x * x - 2 * site1.x * x) / (2 * (site1.y - site2.y))