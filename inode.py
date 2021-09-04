class Inode:
    def __init__(self, ftype='free', addr=-1, refCnt=1):
        self.setAll(ftype, addr, refCnt)

    def setAll(self, ftype, addr, refCnt):
        assert(ftype == 'free' or ftype == 'dir' or ftype == 'file')
        self.ftype = ftype
        self.addr = addr
        self.refCnt = refCnt

    def incRefCnt(self):
        self.refCnt += 1
    
    def decRefCnt(self):
        self.refCnt -= 1
    
    def getRefCnt(self):
        return self.refCnt

    def setType(self, ftype):
        assert(ftype == 'free' or ftype == 'dir' or ftype == 'file')
        self.ftype = ftype

    def setAddr(self, block):
        self.addr = block

    def getSize(self):
        if self.addr == -1:
            return 0
        return 1

    def getAddr(self):
        return self.addr

    def getType(self):
        return self.ftype

    def free(self):
        self.ftype = 'free'
        self.addr = -1