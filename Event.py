import PriorityQueue
import BeachLine
#import DoublyConnectedEdgeList
import abc

class Event(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abc.abstractmethod
    def Handle(self, queue, beachline, dcel):
        return

    def ToString(self):
        return '("+x+", "+y+")'
    