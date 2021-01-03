class PriorityQueue(object): 
    def __init__(self):
        self.heap = []

    def Top(self):
        if self.heap.count > 0:
            return self.heap[0]
        else:
            return None

    def Pop(self):
        if self.heap.Count is 0:
            return None

        lastTop = self.heap[0]

        if self.heap.count > 1:
            lastEvent = self.heap[self.heap.count - 1]
            SwapIndices(lastTop, lastEvent)
            self.heap.pop(self.heap.count - 1)
            self.heap[0] = lastEvent
            BubbleDown(0)
        else:
            self.heap.pop(self.heap.count - 1)

        return lastTop

    def Push(self, eventNode):
        eventNode.index = self.heap.count
        self.heap.append(eventNode)
        BubbleUp(self.heap.count - 1)
        print("Inserted event " + eventNode.x + " " + eventNode.y)

    def IsEmpty(self):
        return False

    def Parent(self, index):
        return (index - 1) / 2

    def Left(self, index):
        return index*2 + 1

    def Right(self, index):
        return index*2 + 2

    def Compare(self, o1, o2):
        return o1.y > o2.y

    def BubbleUp(self, index):
        while index > 0 and Compare(self.heap[index], self.heap[Parent(index)]):
            parentIndex = Parent(index)

            # Swap this position and indice with its parent
            SwapIndices(self.heap[index], self.heap[parentIndex])
            t = self.heap[index]
            self.heap[index] = self.heap[parentIndex]
            self.heap[parentIndex] = t
            index = parentIndex

    def SwapIndices(self, e1, e2):
        t = e1.index
        e1.index = e2.index
        e2.index = t

    def BubbleDown(self, index):
        swapIndex = SmallestBetweenRootAndChildren(index)
        while swapIndex is not index:
            # Swap this position and indice with the smallest node
            SwapIndices(self.heap[index], self.heap[swapIndex])
            t = self.heap[index]
            self.heap[index] = self.heap[swapIndex]
            self.heap[swapIndex] = t

            index = swapIndex
            swapIndex = SmallestBetweenRootAndChildren(index)

    def SmallestBetweenRootAndChildren(self, index):
        left = Left(index)
        right = Right(index)

        # No child therefore parent is the smallest
        if left >= self.heap.count:
            return index

        # Considering only parent and left
        if right >= self.heap.count:
            if Compare(self.heap[index], self.heap[left]):
                return index
            else:
                return left

        # Considering all 3
        if Compare(self.heap[left], self.heap[right]):
            if Compare(self.heap[index], self.heap[left]):
                return index
            else:
                return left
        else:
            if Compare(self.heap[index], self.heap[right]):
                return index
            else:
                return right

    def Delete(self, eventObj):
        eventInQ = heap[eventObj.index]
        if(eventInQ is not eventObj):
            return False
        
        print("Deleting" + eventObj)

        if (self.heap.count > 1):
            lastEvent = self.heap[self.heap.count - 1]
            self.heap.pop(self.heap.count - 1)
            self.heap[eventObj.index] = lastEvent
            BubbleDown(eventObj.index)
        else:
            self.heap.pop(self.heap.count - 1)
        
        return True