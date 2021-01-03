from InternalNode import InternalNode
from Parabola import Parabola
from Triplet import Triplet


class BeachLine(object):
    def __init__(self):
        self.root = None

    def GetParabolaFor(self, x, y):
        if self.root is None:
            return None

        node = self.root

        while not node.IsLeaf():
            node = node.Traverse(x, y)

        return node

    def InsertRootParabola(self, siteEvent):
        self.root = Parabola(siteEvent, None)

    def InsertAndSplit(self, siteEvent, above):
        # Divide this parabola node into 3 parabola nodes by using two internal nodes
        replacer = InternalNode(above.siteEvent, siteEvent, above.parent)
        replacer.left = Parabola(above.siteEvent, replacer)

        subNode = InternalNode(siteEvent, above.siteEvent, replacer)
        replacer.right = subNode

        newParabola = Parabola(siteEvent, subNode)
        subNode.left = newParabola
        subNode.right = Parabola(above.siteEvent, subNode)

        # Replace the above with replacer
        if above.parent is not None:
            if above is above.parent.left:
                above.parent.left = replacer
            else:
                above.parent.right = replacer
        else:
            self.root = replacer

        return newParabola

    def FindTripletOnLeftSide(self, parabola):
        # Find the right most leaf node in the left subtree
        left1 = self.FindLeftSibling(parabola)

        if left1 is not None:
            left2 = self.FindLeftSibling(left1)
            if left2 is not None:
                return Triplet(left2, left1, parabola)
            else:
                return None
        else:
            return None

    def FindTripletOnRightSide(self, parabola):
        # Find the right most leaf node in the left subtree
        right1 = self.FindRightSibling(parabola)

        if right1 is not None:
            right2 = self.FindRightSibling(right1)
            if right2 is not None:
                return Triplet(parabola, right1, right2)
            else:
                return None
        else:
            return None

    def FindLeftSibling(self, parabola):
        node = parabola

        # Look for the parent that has a left child
        comingFrom = None
        while node.parent is not None and node.parent.left is node:
            comingFrom = node
            node = node.parent

        # It reached the root coming from the left side
        if (node.parent is None and not node.IsLeaf()) and (node.left is comingFrom):
            return None

        if node.parent.left.IsLeaf():
            return node.parent.left
        else:
            generalNode = node.parent.left
            while (not generalNode.IsLeaf()):
                generalNode = generalNode.right

            return generalNode

    def FindRightSibling(self, parabola):
        node = parabola

        # Look for the parent that has a left child
        comingFrom = None
        while node.parent is not None and node.parent.right is node:
            comingFrom = node
            node = node.parent

        # It reached the root coming from the left side
        if (node.parent is None and not node.IsLeaf()) and (node.right is comingFrom):
            return None

        if node.parent.right.IsLeaf():
            return node.parent.right
        else:
            generalNode = node.parent.right
            while (not generalNode.IsLeaf()):
                generalNode = generalNode.left

            return generalNode

    def ToString(self):
        return "Root: " + self.root
