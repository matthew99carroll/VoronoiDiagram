class PriorityQueue(object):
    def __init__(self):
        self.heap = []

    def Top(self):
        if len(self.heap) > 0:
            return self.heap[0]
        else:
            return None

    def Pop(self):
        if len(self.heap) is 0:
            return None

        lastTop = self.heap[0]

        if len(self.heap) > 1:
            lastEvent = self.heap[len(self.heap) - 1]
            self.SwapIndices(lastTop, lastEvent)
            self.heap.pop(len(self.heap) - 1)
            self.heap[0] = lastEvent
            self.BubbleDown(0)
        else:
            self.heap.pop(len(self.heap) - 1)

        return lastTop

    def Push(self, eventNode):
        eventNode.index = len(self.heap)
        self.heap.append(eventNode)

        self.BubbleUp(len(self.heap) - 1)
        print("Inserted event " + str(eventNode.x) + " " + str(eventNode.y))

    def IsEmpty(self):
        return False

    def Parent(self, index):
        return (index - 1) / 2

    def Left(self, index):
        return index * 2 + 1

    def Right(self, index):
        return index * 2 + 2

    def Compare(self, o1, o2):
        return o1.y > o2.y

    def BubbleUp(self, index):
        while index > 0 and self.Compare(self.heap[index], self.heap[int(self.Parent(index))]):
            parentIndex = self.Parent(index)

            # Swap this position and indice with its parent
            self.SwapIndices(self.heap[index], self.heap[parentIndex])
            t = self.heap[index]
            self.heap[index] = self.heap[parentIndex]
            self.heap[parentIndex] = t
            index = parentIndex

    def SwapIndices(self, e1, e2):
        t = e1.index
        e1.index = e2.index
        e2.index = t

    def BubbleDown(self, index):
        swapIndex = self.SmallestBetweenRootAndChildren(index)
        while swapIndex is not index:
            # Swap this position and indice with the smallest node
            self.SwapIndices(self.heap[index], self.heap[swapIndex])
            t = self.heap[index]
            self.heap[index] = self.heap[swapIndex]
            self.heap[swapIndex] = t

            index = swapIndex
            swapIndex = self.SmallestBetweenRootAndChildren(index)

    def SmallestBetweenRootAndChildren(self, index):
        left = self.Left(index)
        right = self.Right(index)

        # No child therefore parent is the smallest
        if left >= len(self.heap):
            return index

        # Considering only parent and left
        if right >= len(self.heap):
            if self.Compare(self.heap[index], self.heap[left]):
                return index
            else:
                return left

        # Considering all 3
        if self.Compare(self.heap[left], self.heap[right]):
            if self.Compare(self.heap[index], self.heap[left]):
                return index
            else:
                return left
        else:
            if self.Compare(self.heap[index], self.heap[right]):
                return index
            else:
                return right

    def Delete(self, eventObj):
        eventInQ = self.heap[eventObj.index]
        if (eventInQ is not eventObj):
            return False

        print("Deleting" + eventObj)

        if (len(self.heap) > 1):
            lastEvent = self.heap[len(self.heap) - 1]
            self.heap.pop(len(self.heap) - 1)
            self.heap[eventObj.index] = lastEvent
            self.BubbleDown(eventObj.index)
        else:
            self.heap.pop(len(self.heap) - 1)

        return True
