class Block:
    def __init__(self, ftype):
        assert(ftype == 'dir' or ftype == 'file' or ftype == 'free')
        self.ftype = ftype
        self.dirUsed = 0
        self.maxUsed = 32
        self.dirList = []
        self.data = ''

    def dump(self):
        if self.ftype == 'free':
            return '[]'
        elif self.ftype == 'dir':
            rc = ''
            for d in self.dirList:
                # d is of the form ('name', inum)
                short = f'({d[0]}, {d[1]})'
                if rc == '':
                    rc = short
                else:
                    rc += ' '+short
            return '[' + rc + ']'
            # return f'*{self.dirList}'
        else:
            return f'{self.data}'
    
    def setType(self, ftype):
        assert(self.ftype == 'free')
        self.ftype = ftype

    def addData(self, data):
        assert(self.ftype == 'file')
        self.data = data

    def getNumEntries(self):
        assert(self.ftype == 'dir')
        return self.dirUsed

    def getFreeEntries(self):
        assert(self.ftype == 'dir')
        return self.maxUsed - self.dirUsed

    def getEntry(self, num):
        assert(self.ftype == 'dir' and num < self.dirUsed)
        return self.dirList[num]

    def addDirEntry(self, name, inum):
        assert(self.ftype == 'dir')
        self.dirList.append((name, inum))
        self.dirUsed += 1
        assert(self.dirUsed <= self.maxUsed)

    def delDirEntry(self, name):
        assert(self.ftype == 'dir')
        tname = name.split('/')
        dname = tname[len(tname)-1]
        for idx in range(self.dirUsed):
            if self.dirList[idx][0] == dname:
                self.dirList.pop(idx)
                self.dirUsed -= 1
                return
        assert(1 == 0)

    def dirEntryExists(self, name):
        assert(self.ftype == 'dir')
        for d in self.dirList:
            if name == d[0]:
                return True
        return False

    def free(self):
        assert(self.ftype != 'free')
        if self.ftype == 'dir':
            # check for only dot, dotdot here
            assert(self.dirUsed == 2)
            self.dirUsed = 0
        self.data = ''
        self.ftype = 'free'