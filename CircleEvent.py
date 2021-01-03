from Edge import Edge
from Event import Event
from Vertex import Vertex


class CircleEvent(Event):
    def __init__(self, x, y, radius, triplet):
        self.radius = radius
        self.triplet = triplet

    def Handle(self, queue, beachline, dcel):
        print("Circle Event: " + self)

        # Assertion: Middle arc will definitely have a grand parent
        grandParent = self.triplet.middle.parent.parent

        # Sibling of the middle arc
        sibling = self.triplet.middle.parent.OtherChild(self.triplet.middle)

        # One internal node always gets deleted ('middles' parent), and another internal node gets modified because of convergence
        converger = None

        convergerOnRight = None

        if sibling.IsLeaf():
            converger = grandParent

            # Check if middle's parent is left child of grandparent
            convergerOnRight = grandParent.left == self.triplet.parent
        else:
            converger = sibling

            # Check if sibling is right node of parent
            convergerOnRight = self.triplet.middle.parent.right == sibling

        # Delete middle arc and mind its parent's children
        grandParent.Replace(self.triplet.middle.parent, sibling)  # Replace child

        # Manage grandparent's site
        otherSiteEvent = self.triplet.middle.parent.otherSiteEvent(self.triplet.middle.siteEvent)

        if not grandParent.Contains(otherSiteEvent):
            grandParent.Replace(self.triplet.middle.siteEvent, otherSiteEvent)  # Replace site event (overloaded method)

        # Use the same but possibly modified converger, connect the dangling edges and start a new edge
        # from the breakpoint that has been converged at that point
        self.ConnectDanglingEdges(converger, convergerOnRight, dcel)

        # Nullify this circle event from the triplet arc
        self.triplet.middle.CircleEvent = None

        # Find consecutive triplets and if exists, add circle events in the queue
        leftSide = beachline.FindTripletOnLeftSide(self.triplet.right)

        if leftSide is not None:
            circleEvent = leftSide.ComputeCircleEvent()
            if circleEvent is not None and circleEvent.y < self.y:  # This time we want them to be strictly below th beachline, because we don't want to repeat this current event again
                circleEvent.Insert(queue)

        rightSide = beachline.FindTripletOnRightSide(self.triplet.left)

        if rightSide is not None:
            circleEvent = rightSide.ComputeCircleEvent()
            if circleEvent is not None and circleEvent.y < self.y:  # This time we want them to be strictly below th beachline, because we don't want to repeat this current event again
                circleEvent.Insert(queue)

    def ConnectDanglingEdges(self, converger, convergerOnRight, dcel):
        # Add a vertex in the DCEL and connect it to the dangling edge
        convergingPoint = Vertex(self.x, self.y + self.radius)

        if convergingPoint.y > dcel.uy:  # Above upper bound
            if convergingPoint.x < dcel.lx:  # Before left bound
                self.ClipWithTopLeftCorner(dcel)
            elif convergingPoint.x > dcel.ux:  # After right bound
                self.ClipWithTopRightCorner(dcel)
            else:  # Between left and right boundaries
                self.ClipWithTopBounds(convergingPoint, converger, convergerOnRight, dcel)
        elif convergingPoint.y < dcel.ly:  # Below Lower bound:
            if convergingPoint.x < dcel.lx:  # Before left bound
                self.ClipWithBottomLeftCorner(dcel)
            elif convergingPoint.x > dcel.ux:  # After right bound
                self.ClipWithBottomRightCorner(dcel)
            else:  # Between left and right bounds
                self.ClipWithBottomBounds(convergingPoint, converger, convergerOnRight, dcel)
        else:
            if convergingPoint.x < dcel.lx:  # Before left bound
                self.ClipWithLeftBounds(convergingPoint, converger, convergerOnRight, dcel)
            elif convergingPoint.x > dcel.ux:  # After right bound
                self.ClipWithRightBounds(convergingPoint, converger, convergerOnRight, dcel)
            else:  # Between left and right bounds
                self.JoinVertexWithinBounds(convergingPoint, converger, convergerOnRight, dcel)

        return convergingPoint

    def JoinVertexWithinBounds(self, vertex, converger, convergerOnRight, dcel):
        dcel.vertexList.Add(vertex)

        # every vertex in voronoi diagram is either the topmost or bottommost vertex of some face
        if vertex.y > self.triplet.middle.siteEvent.y:  # top vertex of middle face

            # to find the terminated edge(edge that ends on this vertex)
            terminatedEdgeNode = self.NodeForBreakpointBetween(self.triplet.left.siteEvent,
                                                               self.triplet.right.siteEvent, self.triplet.middle.parent)

            # Old existing edge of converger's parent if present should be connected
            terminatedEdge = terminatedEdgeNode.edge

            if terminatedEdge is not None:

                # if the origin of the left face's edge is not set, it means its getting clipped by the upper bounds
                if terminatedEdge.origin is None:

                    # Get the clipped point
                    y = dcel.uy  # Upper bounds of the bounding box (in our case sweepline goes from top to bottom)
                    x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent, self.triplet.right.siteEvent,
                                                              y)

                    if x < dcel.lx:
                        x = dcel.lx
                        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent,
                                                                  self.triplet.right.siteEvent, x)
                    elif x > dcel.ux:
                        x = dcel.ux
                        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent,
                                                                  self.triplet.right.siteEvent, x)

                    clippedPoint = Vertex(x, y, True)

                    # As a double edge, the original will be used on the left side
                    terminatedEdge.origin = clippedPoint

                    # Since we set origin on the edge of left face, we will append to forward list
                    self.triplet.left.siteEvent.face.AppendToForwardList(terminatedEdge)

                # For the right side, we simply prepend the twin by supplying the clipped point as the
                # point for existing back terminal, and the converging point as the origin of the twin
                terminatedEdge.twin.origin = vertex
                self.triplet.siteEvent.face.PrependToBackwardList(terminatedEdge.twin, terminatedEdge.origin)

            # Get edge of grand parent
            existingEdge = converger.edge

            # A new divergent edge (dangling) will be added to the parent of the convergent
            divergent = Edge()
            dcel.edgeList.Add(divergent)
            dcel.edgeList.Add(divergent.twin)
            converger.parent.edge = divergent

            if convergerOnRight:  # Existing edge right of divergent edge's twin
                self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(vertex, divergent.twin, existingEdge)

                # Add the original divergent to the forward list of the left site's face
                divergent.origin = vertex
                self.triplet.siteEvent.face.AppendToForwardList(divergent)

                # Prepend the twin of the existing edge (which is another divergent) to the right face's backward list
                self.triplet.right.siteEvent.face.PrependToBackwardList(existingEdge.twin, vertex)
            else:  # Existing edge left of diverging edge

                self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(vertex, existingEdge.twin, divergent)

                # A dd the original divergent to the forward list of the left site's face
                existingEdge.origin = vertex
                self.triplet.left.siteEvent.face.AppendToForwardList(existingEdge)

                # prepend the twin of the divergent to the right face's backward list
                self.triplet.right.siteEvent.face.PrependToBackwardList(divergent.twin, vertex)
        else:  # Bottom vertex of middle face

            # if forward list hasn't started, instantiate and clip with upper bounds
            if self.triplet.middle.siteEvent.face.ForwardListNotStarted():
                # this happens when the middle face is situated near the top bounds
                self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right, dcel)

            # if backward list hasn't started, instantiate and  clip with upper bounds
            if self.triplet.middle.siteEvent.face.BackwardListNotStarted():
                # this happens when the middle face is situated near the top bounds
                self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.left, self.triplet.middle, dcel)

            self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(vertex)

            # a new divergent edge(dangling) will be added to the convergent
            convergent = Edge()
            convergent.origin = vertex
            dcel.edgeList.Add(convergent)
            dcel.edgeList.Add(convergent.twin)

            converger.edge = convergent

            # as a double edge, the original gets used for the left side and its twin for the right
            self.triplet.left.siteEvent.face.AppendToForwardList(convergent)
            self.triplet.right.siteEvent.face.PrependToBackwardList(convergent.twin, vertex)

    """
    Geometrically only a top vertex event can happen here
    """

    def ClipWithTopBounds(self, outside, converger, convergerOnRight, dcel):
        y = dcel.uy
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, y)
        leftPoint = Vertex(x, y, True)
        dcel.vertexList.Add(leftPoint)

        y = dcel.uy
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent, self.triplet.right.siteEvent, y)
        rightPoint = Vertex(x, y, True)
        dcel.vertexList.Add(rightPoint)

        pseudoEdge = Edge(leftPoint, True)
        dcel.edgeList.Add(pseudoEdge)

        # get edge of grand parent
        existingEdge = converger.edge

        # a new divergent edge(dangling) will be added to the parent of the convergent
        divergent = Edge()
        dcel.edgeList.Add(divergent)
        dcel.edgeList.Add(divergent.twin)
        converger.parent.edge = divergent

        if convergerOnRight:  # existing edge right of divergent edge's twin
            self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(leftPoint, divergent.twin, existingEdge)

            # add the original divergent to the forward list of the left site's face
            divergent.origin = leftPoint
            self.triplet.left.siteEvent.face.AppendToForwardList(divergent)

            # prepend the twin of the existing edge(which is another divergent) to the right face's backward list
            self.triplet.right.siteEvent.face.PrependToBackwardList(existingEdge.twin, leftPoint)
        else:  # existing edge left of divergent edge

            self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(leftPoint, existingEdge.twin, divergent)

            # add the original divergent to the forward list of the left site's face
            existingEdge.origin = rightPoint
            self.triplet.left.siteEvent.face.AppendToForwardList(existingEdge)

        # prepend the twin of the divergent to the right face's backward list
        self.triplet.right.siteEvent.face.PrependToBackwardList(divergent.twin, rightPoint)

    """
        Geometrically only a bottom vertex event can happen here
    """

    def ClipWithBottomBounds(self, outside, converger, convergerOnRight, dcel):

        # if forward list hasn't started, instantiate and clip with upper bounds
        if self.triplet.middle.siteEvent.face.ForwardListNotStarted():
            # this happens when the middle face is situated near the top bounds
            self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right, dcel)

        # if backward list hasn't started, instantiate and  clip with upper bounds
        if self.triplet.middle.siteEvent.face.BackwardListNotStarted():
            # this happens when the middle face is situated near the top bounds
            self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.left, self.triplet.middle, dcel)

        y = dcel.uy
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, y)
        leftPoint = Vertex(x, y, True)
        dcel.vertexList.Add(leftPoint)

        y = dcel.uy
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent, self.triplet.right.siteEvent, y)
        rightPoint = Vertex(x, y, True)
        dcel.vertexList.Add(rightPoint)

        pseudoEdge = Edge(rightPoint, True)
        dcel.edgeList.Add(pseudoEdge)

        # append the clipped section and close at the left point
        self.triplet.middle.siteEvent.face.AppendToForwardList(pseudoEdge)
        self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(leftPoint)

    def ClipWithLeftBounds(self, outside, converger, convergerOnRight, dcel):

        if outside.y > self.triplet.middle.siteEvent.y:  # Top vertex of middle face

            # Find the clipping with elft bounds between left and middle
            x = dcel.lx
            y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, x)
            leftClipBetweenLeftMiddle = Vertex(x, y, True)
            dcel.vertexList.Add(leftClipBetweenLeftMiddle)

            # Find the clipping with left bounds between middle and right
            x = dcel.lx
            y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent, x)
            leftClipBetweenMiddleRight = Vertex(x, y, True)
            dcel.vertexList.Add(leftClipBetweenMiddleRight)

            # Create a psuedo edge for the clipped section
            psuedoEdge = Edge(leftClipBetweenLeftMiddle,
                              True)  # Middle-right will always be the upper on the left bound
            dcel.edgeList.Add(psuedoEdge)

            # Get edge of grand parent
            existingEdge = converger.edge

            # Create the lists for middle face and set the existing edge's twin on the right face after setting its clipping point
            self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(leftClipBetweenMiddleRight, psuedoEdge,
                                                                               existingEdge)
            self.triplet.right.siteEvent.face.PrependToBackwardList(existingEdge.twin, leftClipBetweenMiddleRight)

            # A new divergent edge (dangling) will be added to the parent of the convergent
            divergent = Edge()
            dcel.edgeList.Add(divergent)
            dcel.edgeList.Add(divergent.twin)
            converger.parent.edge = divergent

            # This divergent will also be between left and middle faces
            self.triplet.middle.siteEvent.face.PrependToBackwardList(divergent.twin, leftClipBetweenLeftMiddle)
            divergent.origin = leftClipBetweenLeftMiddle
            self.triplet.left.siteEvent.face.AppendToForwardList(divergent)
        else:  # Bottom vertex of middle face

            # If middle is above both left and right, it needs to be handled differently
            if self.triplet.middle.siteEvent.y > self.triplet.left.siteEvent.y and self.triplet.middle.siteEvent > self.triplet.right.siteEvent.y:

                # Find the clipping with left bounds
                x = dcel.lx
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent,
                                                          x)
                leftClip = Vertex(x, y, True)
                dcel.vertexList.Add(leftClip)

                # Append a pseudo edge
                psuedoEdge = Edge(leftClip, True)
                dcel.edgeList.Add(psuedoEdge)
                self.triplet.middle.siteEvent.face.AppendToForwardList(psuedoEdge)

                # Find the lower clipped point
                x = dcel.lx
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.right.siteEvent, self.triplet.left.siteEvent, x)
                lowerClip = Vertex(x, y, True)
                dcel.vertexList.Add(lowerClip)

                # Convergent will emerge on the other side and will get clipped when its other endpoint is encountered
                convergent = Edge()
                convergent.origin = lowerClip
                dcel.edgeList.Add(convergent)
                dcel.edgeList.Add(convergent.twin)
                converger.edge = convergent

                # We will add this convergent to the left face
                self.triplet.siteEvent.face.AppendToForwardList(convergent)

                # For the right face, create antoher psuedo edge taht will close it for the right face
                closeRightFace = Edge(lowerClip, True)
                dcel.edgeList.Add(closeRightFace)
                self.triplet.right.siteEvent.face.PrependToBackwardList(closeRightFace, leftClip)
                self.triplet.right.siteEvent.face.PrependToBackwardList(convergent.twin, lowerClip)
            else:
                # Find the clipping with left bounds between left and middle
                x = dcel.lx
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, x)
                leftClipBetweenLeftMiddle = Vertex(x, y, True)
                dcel.vertexList.Add(leftClipBetweenLeftMiddle)

                # Find the clipping with left bounds between middle and right
                x = dcel.lx
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent,
                                                          x)
                leftClipBetweenMiddleRight = Vertex(x, y, True)
                dcel.vertexList.Add(leftClipBetweenMiddleRight)

                # If forward list hasn't started, instantiate and clip with upper bounds
                if self.triplet.middle.siteEvent.face.ForwardListNotStarted():
                    # This happens when the middle face is situated near the top bounds
                    self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right, dcel)

                # If backward list hasn't started, instantiate and clip with upper bounds
                if self.triplet.middle.siteEvent.face.BackwardListNotStarted():
                    # This happens when the middle face is situated near the top bounds
                    self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.left, self.triplet.middle, dcel)

                # Create a psuedo edge for the clipped section
                psuedoEdge = Edge(True)
                dcel.edgeList.Add(psuedoEdge)

                # Prepend the psuedo edge and connect using middle-right (which is always to be the lower on the left bound)
                self.triplet.middle.siteEvent.face.PrependToBackwardList(psuedoEdge, leftClipBetweenLeftMiddle)
                self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(leftClipBetweenMiddleRight)

    def ClipWithRightBounds(self, outside, converger, convergerOnRight, dcel):

        if outside.y > self.triplet.middle.siteEvent.y:  # Top vertex of middle face

            # Find the clipping with elft bounds between left and middle
            x = dcel.ux
            y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, x)
            rightClipBetweenLeftMiddle = Vertex(x, y, True)
            dcel.vertexList.Add(rightClipBetweenLeftMiddle)

            # Find the clipping with left bounds between middle and right
            x = dcel.ux
            y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent, x)
            rightClipBetweenMiddleRight = Vertex(x, y, True)
            dcel.vertexList.Add(rightClipBetweenMiddleRight)

            # Create a psuedo edge for the clipped section
            psuedoEdge = Edge(rightClipBetweenLeftMiddle,
                              True)  # Middle-right will always be the upper on the left bound
            dcel.edgeList.Add(psuedoEdge)

            # Get edge of grand parent
            existingEdge = converger.edge

            # Create the lists for middle face and set the existing edge's twin on the left face after setting its clipping point
            self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(rightClipBetweenLeftMiddle,
                                                                               existingEdge.twin, psuedoEdge)
            existingEdge.origin = rightClipBetweenLeftMiddle
            self.triplet.left.siteEvent.face.AppendToForwardList(existingEdge)

            # A new divergent edge (dangling) will be added to the parent of the convergent
            divergent = Edge()
            dcel.edgeList.Add(divergent)
            dcel.edgeList.Add(divergent.twin)
            converger.parent.edge = divergent

            # This divergent will also be between right and middle faces
            self.triplet.right.siteEvent.face.PrependToBackwardList(divergent.twin, rightClipBetweenMiddleRight)
            divergent.origin = rightClipBetweenMiddleRight
            self.triplet.middle.siteEvent.face.AppendToForwardList(divergent)
        else:  # Bottom vertex of middle face

            # If middle is above both left and right, it needs to be handled differently
            if self.triplet.middle.siteEvent.y > self.triplet.left.siteEvent.y and self.triplet.middle.siteEvent > self.triplet.right.siteEvent.y:

                # Find the clipping with left bounds
                x = dcel.ux
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent,
                                                          x)
                rightClip = Vertex(x, y, True)
                dcel.vertexList.Add(rightClip)

                # Append a pseudo edge
                psuedoEdge = Edge(rightClip, True)
                dcel.edgeList.Add(psuedoEdge)
                self.triplet.middle.siteEvent.face.PrependToBackwardList(psuedoEdge, rightClip)

                # Find the lower clipped point
                x = dcel.lx
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.right.siteEvent, self.triplet.left.siteEvent, x)
                lowerClip = Vertex(x, y, True)
                dcel.vertexList.Add(lowerClip)

                # Convergent will emerge on the other side and will get clipped when its other endpoint is encountered
                convergent = Edge()
                convergent.origin = lowerClip
                dcel.edgeList.Add(convergent)
                dcel.edgeList.Add(convergent.twin)
                converger.edge = convergent

                # We will add this convergent to the left face
                self.triplet.right.siteEvent.face.PrependToBackwardList(convergent.twin, lowerClip)

                # For the left face, create another psuedo edge taht will close it for the left face
                closeLeftFace = Edge(rightClip, True)
                dcel.edgeList.Add(closeLeftFace)
                self.triplet.left.siteEvent.face.AppendToForwardList(closeLeftFace)
                self.triplet.left.siteEvent.face.AppendToForwardList(convergent)
            else:

                # Find the clipping with left bounds between left and middle
                x = dcel.ux
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, x)
                rightClipBetweenLeftMiddle = Vertex(x, y, True)
                dcel.vertexList.Add(rightClipBetweenLeftMiddle)

                # Find the clipping with left bounds between middle and right
                x = dcel.ux
                y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.right.siteEvent,
                                                          x)
                rightClipBetweenMiddleRight = Vertex(x, y, True)
                dcel.vertexList.Add(rightClipBetweenMiddleRight)

                # If forward list hasn't started, instantiate and clip with upper bounds
                if self.triplet.middle.siteEvent.face.ForwardListNotStarted():
                    # This happens when the middle face is situated near the top bounds
                    self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right, dcel)

                # If backward list hasn't started, instantiate and clip with upper bounds
                if self.triplet.middle.siteEvent.face.BackwardListNotStarted():
                    # This happens when the middle face is situated near the top bounds
                    self.ClipClosingEdgeCrossingBoundsBetween(self.triplet.left, self.triplet.middle, dcel)

                # Create a psuedo edge for the clipped section
                psuedoEdge = Edge(rightClipBetweenMiddleRight, True)
                dcel.edgeList.Add(psuedoEdge)

                # Prepend the psuedo edge and connect using middle-right (which is always to be the lower on the left bound)
                self.triplet.middle.siteEvent.face.AppendToForwardList(psuedoEdge)
                self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(rightClipBetweenLeftMiddle)

    """
    Geometrically it is only possible to get top vertex case here
    """

    def ClipWithTopLeftCorner(self, dcel):

        # Create another top left vertex
        topLeftCorner = Vertex(dcel.lx, dcel.uy, True)
        dcel.vertexList.Add(topLeftCorner)

        # Create two psuedo edges for the clips for the middle face
        cornerTop = Edge(topLeftCorner, True)
        cornerLeft = Edge(True)
        dcel.edgeList.Add(cornerTop)
        dcel.edgeList.Add(cornerLeft)

        self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(topLeftCorner, cornerLeft, cornerTop)

    """
    Geometrically it is only possible to get top vertex case here
    """

    def ClipWithTopRightCorner(self, dcel):

        # Create another top right vertex
        topRightCorner = Vertex(dcel.ux, dcel.uy, True)
        dcel.vertexList.Add(topRightCorner)

        # Create two psuedo edges for the clips for the middle face
        cornerTop = Edge(True)
        cornerRight = Edge(topRightCorner, True)
        dcel.edgeList.Add(cornerTop)
        dcel.edgeList.Add(cornerRight)

        self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(topRightCorner, cornerTop, cornerRight)

    """
    Geometrically its only possible to get bottom vertex case here.
    """

    def ClipWithBottomRightCorner(self, dcel):

        # find clipping points
        x = dcel.ux
        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.middle.siteEvent, x)
        rightClip = Vertex(x, y)
        dcel.vertexList.Add(rightClip)

        y = dcel.ly
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent, self.triplet.left.siteEvent, y)
        bottomClip = Vertex(x, y)
        dcel.vertexList.Add(bottomClip)

        # create two pseudo edges for the clips for the middle face
        cornerRight = Edge(rightClip, True)
        cornerBottom = Edge(True)
        dcel.edgeList.Add(cornerRight)
        dcel.edgeList.Add(cornerBottom)

        self.triplet.middle.siteEvent.face.AppendToForwardList(cornerRight)
        self.triplet.middle.siteEvent.face.PrependToBackwardList(cornerBottom, bottomClip)

        # create another bottom right vertex
        bottomRightCorner = Vertex(dcel.ux, dcel.ly, True)
        dcel.vertexList.Add(bottomRightCorner)
        self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(bottomRightCorner)

    """
    Geometrically its only possible to get bottom vertex case here.
    """

    def ClipWithBottomLeftCorner(self, dcel):

        # find clipping points
        x = dcel.lx
        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.middle.siteEvent, self.triplet.middle.siteEvent, x)
        leftClip = Vertex(x, y)
        dcel.vertexList.Add(leftClip)

        y = dcel.ly
        x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent, self.triplet.left.siteEvent, y)
        bottomClip = Vertex(x, y)
        dcel.vertexList.Add(bottomClip)

        # create two pseudo edges for the clips for the middle face
        cornerLeft = Edge(True)
        cornerBottom = Edge(bottomClip, True)
        dcel.edgeList.Add(cornerLeft)
        dcel.edgeList.Add(cornerBottom)

        self.triplet.middle.siteEvent.face.AppendToForwardList(cornerBottom)
        self.triplet.middle.siteEvent.face.PrependToBackwardList(cornerLeft, leftClip)

        # create another bottom left vertex
        bottomLeftCorner = Vertex(dcel.lx, dcel.ly, True)
        dcel.vertexList.Add(bottomLeftCorner)
        self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(bottomLeftCorner)

    def ClipClosingEdgeCrossingBoundsBetween(self, leftSide, rightSide, dcel):

        # find the clipped point with the upper bounds
        y = dcel.uy
        x = dcel.GetXOfParabolaIntersectionGivenY(leftSide.siteEvent, rightSide.siteEvent, y)

        if x < dcel.lx:
            x = dcel.lx
            y = dcel.GetYOfParabolaIntersectionGivenX(leftSide.siteEvent, rightSide.siteEvent, x)
        elif (x > dcel.ux):
            x = dcel.ux
            y = dcel.GetYOfParabolaIntersectionGivenX(leftSide.siteEvent, rightSide.siteEvent, x)

        clippedPoint = Vertex(x, y, True)
        dcel.vertexList.Add(clippedPoint)

        # get the edge whose endpoint this breakpoint is(create if needed)
        breakpoint = self.NodeForBreakpointBetween(leftSide.siteEvent, rightSide.siteEvent, self.triplet.middle.parent)
        terminatedEdge = None
        if (breakpoint.edge is None):
            terminatedEdge = Edge()
            dcel.edgeList.Add(terminatedEdge)
            dcel.edgeList.Add(terminatedEdge.twin)
            breakpoint.edge = terminatedEdge
        else:
            terminatedEdge = breakpoint.edge

        # set the clipped point as the origin of the left face(middle in this case)
        terminatedEdge.origin = clippedPoint

        # add to forward and backward lists of left and right sides respectively
        leftSide.siteEvent.face.AppendToForwardList(terminatedEdge)
        rightSide.siteEvent.face.PrependToBackwardList(terminatedEdge.twin, terminatedEdge.origin)

        return terminatedEdge

    def NodeForBreakpointBetween(self, site1, site2, fromParent):

        # Keep going up from the given parent until you reach a (left, right) breakpoint
        breakpointNode = fromParent

        while breakpointNode is not None and breakpointNode.IsBreakpointBetween(self.triplet.left.siteEvent,
                                                                                self.triplet.right.siteEvent):
            breakpointNode = breakpointNode.parent

        return breakpointNode

    """
    Removes the circle event from priority queue and removes its references from the arc(only if they were set).
    Returns true if deleted from queue, false otherwise (in case it wasn't already in queue)
    """

    def Delete(self, queue):

        # nullify the references to this circle event in the triplet arcs(only if it is currently set to this)
        if self.triplet.middle.circleEvent is self:
            self.triplet.middle.circleEvent = None

        return queue.Delete(self)

    """
    Inserts this circle event in the queue and sets this event as a references in the triplet arcs.
    Also removes the circle event if existed in any of the triplet arc
    Return false if no existing event was found, true otherwise
    """

    def Insert(self, queue):

        queue.Push(self)

        # Remove existing event
        existingCircleEventPresent = False

        if self.triplet.middle.circleEvent is not self and self.triplet.middle.circleEvent is not None:
            self.triplet.middle.circleEvent.Delete(queue)
            existingCircleEventPresent = True

        # set the references
        self.triplet.middle.circleEvent = self

        return existingCircleEventPresent
