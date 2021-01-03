import abc


class Node(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, p):
        parent = p

    @abc.abstractmethod
    def IsLeaf(self):
        """
            Traverses to the leaf node for the given x,y
        """
        return

    @abc.abstractmethod
    def Traverse(self, x, y):
        return
