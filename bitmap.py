class Bitmap:
    def __init__(self, size):
        self.size = size
        self.bmap = []
        for i in range(size):
            self.bmap.append(0)
    
    def alloc(self):
        for idx in range(self.size):
            if self.bmap[idx] == 0:
                self.bmap[idx] = 1
                return idx
        return -1

    def free(self, idx):
        assert(self.bmap[idx] == 1)
        self.bmap[idx] = 0
        
    def markAlloc(self, idx):
        assert(self.bmap[idx] == 0)
        self.bmap[idx] = 1
        
    def dump(self):
        s = ''
        for idx in range(self.size):
            s += str(self.bmap[idx])
        return s