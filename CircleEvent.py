import Vertex
import Edge
import Event

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
        grandParent.Replace(self.triplet.middle.parent, sibling) # Replace child

        # Manage grandparent's site
        otherSiteEvent = self.triplet.middle.parent.otherSiteEvent(self.triplet.middle.siteEvent)

        if not grandParent.Contains(otherSiteEvent):
            grandParent.Replace(self.triplet.middle.siteEvent, otherSiteEvent) # Replace site event (overloaded method)

        # Use the same but possibly modified converger, connect the dangling edges and start a new edge
        # from the breakpoint that has been converged at that point
        ConnectDanglingEdges(converger, convergerOnRight, dcel)

        # Nullify this circle event from the triplet arc
        self.triplet.middle.CircleEvent = None

        # Find consecutive triplets and if exists, add circle events in the queue
        leftSide = beachline.FindTripletOnLeftSide(self.triplet.right)
        
        if leftSide is not None:
            circleEvent = leftSide.ComputeCircleEvent()
            if circleEvent is not None and circleEvent.y < y: # This time we want them to be strictly below th beachline, because we don't want to repeat this current event again
                circleEvent.Insert(queue)
        
        rightSide = beachline.FindTripletOnRightSide(self.triplet.left)

        if rightSide is not None:
            circleEvent = rightSide.ComputeCircleEvent()
            if circleEvent is not None and circleEvent.y < y: # This time we want them to be strictly below th beachline, because we don't want to repeat this current event again
                circleEvent.Insert(queue)

    def ConnectDanglingEdges(self, converger, convergerOnRight, dcel):
        # Add a vertex in the DCEL and connect it to the dangling edge
        convergingPoint = Vertex(self.x, self.y + self.radius)

        if convergingPoint.y > dcel.uy: # Above upper bound
            if convergingPoint.x < dcel.lx: # Before left bound
                ClipWithTopLeftCorner(dcel)
            elif convergingPoint.x > dcel.ux: # After right bound
                ClipWithTopRightCorner(dcel)
            else: # Between left and right boundaries
                ClipWithTopBounds(convergingPoint, converger, convergerOnRight, dcel)
        elif convergingPoint.y < dcel.ly: # Below Lower bound:
            if convergingPoint.x < dcel.lx: # Before left bound
                ClipWithBottomLeftCorner(dcel)
            elif convergingPoint.x > dcel.ux: # After right bound
                ClipWithBottomRightCorner(dcel)
            else: # Between left and right bounds
                ClipWithBottomBounds(convergingPoint, converger, convergerOnRight, dcel)
        else:
            if convergingPoint.x < dcel.lx: # Before left bound
                ClipWithLeftBounds(convergingPoint, converger, convergerOnRight, dcel)
            elif convergingPoint.x > dcel.ux: # After right bound
                ClipWithRightBounds(convergingPoint, converger, convergerOnRight, dcel)
            else: # Between left and right bounds
                JoinVertexWithinBounds(convergingPoint, converger, convergerOnRight, dcel)
        
        return convergingPoint

    def JoinVertexWithinBounds(self, vertex, converger, convergerOnRight, dcel):
        dcel.vertexList.Add(vertex)

        # every vertex in voronoi diagram is either the topmost or bottommost vertex of some face
        if vertex.y > self.triplet.middle.siteEvent.y: # top vertex of middle face

            # to find the terminated edge(edge that ends on this vertex)
            terminatedEdgeNode = NodeForBreakpointBetween(self.triplet.left.siteEvent, self.triplet.right.siteEvent, self.triplet.middle.parent)

            # Old existing edge of converger's parent if present should be connected
            terminatedEdge = terminatedEdgeNode.edge

            if terminatedEdge is not None:

                # if the origin of the left face's edge is not set, it means its getting clipped by the upper bounds
                if terminatedEdge.origin is None:

                    # Get the clipped point
                    y = dcel.uy # Upper bounds of the bounding box (in our case sweepline goes from top to bottom)
                    x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent, self.triplet.right.siteEvent, y)

                    if x < dcel.lx:
                        x = dcel.lx
                        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.right.siteEvent, x)
                    elif x > dcel.ux:
                        x = dcel.ux
                        y = dcel.GetYOfParabolaIntersectionGivenX(self.triplet.left.siteEvent, self.triplet.right.siteEvent, x)

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

            if convergerOnRight: # Existing edge right of divergent edge's twin
                self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(vertex, divergent.twin, existingEdge)

                # Add the original divergent to the forward list of the left site's face
                divergent.origin = vertex
                self.triplet.siteEvent.face.AppendToForwardList(divergent)

                # Prepend the twin of the existing edge (which is another divergent) to the right face's backward list
                self.triplet.right.siteEvent.face.PrependToBackwardList(existingEdge.twin, vertex)
            else: # Existing edge left of diverging edge
                
                self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(vertex,existingEdge.twin,divergent)

                #A dd the original divergent to the forward list of the left site's face
                existingEdge.origin = vertex
                self.triplet.left.siteEvent.face.AppendToForwardList(existingEdge)

                #prepend the twin of the divergent to the right face's backward list
                self.triplet.right.siteEvent.face.PrependToBackwardList(divergent.twin,vertex)
        else: # Bottom vertex of middle face

            # if forward list hasn't started, instantiate and clip with upper bounds 
            if self.triplet.middle.siteEvent.face.ForwardListNotStarted():

                #this happens when the middle face is situated near the top bounds
                ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right,dcel)
            

            #if backward list hasn't started, instantiate and  clip with upper bounds 
            if self.triplet.middle.siteEvent.face.BackwardListNotStarted():
                #this happens when the middle face is situated near the top bounds
                ClipClosingEdgeCrossingBoundsBetween(self.triplet.left, self.triplet.middle, dcel)

            self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(vertex)

            # a new divergent edge(dangling) will be added to the convergent
            convergent = Edge()
            convergent.origin = vertex
            dcel.edgeList.Add(convergent)
            dcel.edgeList.Add(convergent.twin)

            converger.edge = convergent

            # as a double edge, the original gets used for the left side and its twin for the right
            self.triplet.left.siteEvent.face.AppendToForwardList(convergent)
            self.triplet.right.siteEvent.face.PrependToBackwardList(convergent.twin,vertex)

    """
        Geometrically only a top vertex event can happen here
    """
    def ClipWithTopBounds(self, outside, converger, convergerOnRight, dcel):
        	y = dcel.uy
			x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent, self.triplet.middle.siteEvent, y)
			leftPoint = Vertex(x,y,True)
			dcel.vertexList.Add(leftPoint)

			y = dcel.uy
			x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent, self.triplet.right.siteEvent, y)
			rightPoint = Vertex(x,y,True)
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

			if convergerOnRight: #existing edge right of divergent edge's twin
				self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(leftPoint,divergent.twin,existingEdge)

				# add the original divergent to the forward list of the left site's face
				divergent.origin = leftPoint
				self.triplet.left.siteEvent.face.AppendToForwardList(divergent)

				#prepend the twin of the existing edge(which is another divergent) to the right face's backward list
				self.triplet.right.siteEvent.face.PrependToBackwardList(existingEdge.twin, leftPoint)
			else: #existing edge left of divergent edge					

				self.triplet.middle.siteEvent.face.CreateForwardAndBackwardListsAt(leftPoint,existingEdge.twin, divergent)

				# add the original divergent to the forward list of the left site's face
				existingEdge.origin=rightPoint
				self.triplet.left.siteEvent.face.AppendToForwardList(existingEdge)

				# prepend the twin of the divergent to the right face's backward list
				self.triplet.right.siteEvent.face.PrependToBackwardList(divergent.twin, rightPoint)
	
    """
        Geometrically only a bottom vertex event can happen here
    """
    def ClipWithBottomBounds(self, outside, converger, convergerOnRight, dcel):
        
			#if forward list hasn't started, instantiate and clip with upper bounds 
			if self.triplet.middle.siteEvent.face.ForwardListNotStarted():

				#this happens when the middle face is situated near the top bounds
				ClipClosingEdgeCrossingBoundsBetween(self.triplet.middle, self.triplet.right, dcel)
			

			#if backward list hasn't started, instantiate and  clip with upper bounds 
			if self.triplet.middle.siteEvent.face.BackwardListNotStarted():

				#this happens when the middle face is situated near the top bounds
				ClipClosingEdgeCrossingBoundsBetween(self.triplet.left,self.triplet.middle,dcel)
			

			y = dcel.uy
			x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.left.siteEvent,self.triplet.middle.siteEvent,y)
			leftPoint = Vertex(x,y,True)
			dcel.vertexList.Add(leftPoint)

			y = dcel.uy
			x = dcel.GetXOfParabolaIntersectionGivenY(self.triplet.middle.siteEvent,self.triplet.right.siteEvent,y)
			rightPoint = Vertex(x, y, True)
			dcel.vertexList.Add(rightPoint)

			pseudoEdge = Edge(rightPoint, True)
			dcel.edgeList.Add(pseudoEdge)

			#append the clipped section and close at the left point
			self.triplet.middle.siteEvent.face.AppendToForwardList(pseudoEdge)
			self.triplet.middle.siteEvent.face.ConnectBackwardAndForwardListsAt(leftPoint)

    def ClipWithLeftBounds(self, outside, converger, convergerOnRight, dcel)