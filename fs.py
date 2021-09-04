from bitmap import Bitmap
from inode import Inode
from block import Block
import random

class FS:
    def __init__(self, numInodes, numData, printState, printOps, printFinal):
        self.numInodes = numInodes
        self.numData = numData

        self.ibitmap = Bitmap(self.numInodes)
        self.inodes = []
        for i in range(self.numInodes):
            self.inodes.append(Inode())

        self.dbitmap = Bitmap(self.numInodes)
        self.data = []
        for i in range(self.numData):
            self.data.append(Block('free'))
        
        # root inode
        self.ROOT = 0
        
        # create root directory
        self.ibitmap.markAlloc(self.ROOT)
        self.inodes[self.ROOT].setAll('dir', 0, 2)
        self.dbitmap.markAlloc(self.ROOT)
        self.data[0].setType('dir')
        self.data[0].addDirEntry('.', self.ROOT)
        self.data[0].addDirEntry('..', self.ROOT)

        # this is just for the fake workload generator
        self.files = []
        self.dirs = ['/']
        self.nameToInum = {'/': self.ROOT}

        self.printState = printState
        self.printOps = printOps
        self.printFinal = printFinal

    def dump(self):
        print('inode bitmap:', self.ibitmap.dump())
        print('inodes:')
        for i in range(0, self.numInodes):
            ftype = self.inodes[i].getType()
            if ftype == 'free':
                print('[]')
            else:
                print(f'[{ftype} address: {self.inodes[i].getAddr()} refCount: {self.inodes[i].getRefCnt()}]')
        print('')
        
        print('data bitmap:', self.dbitmap.dump())
        print('data:')
        for i in range(self.numData):
            print(self.data[i].dump())
        print('')

    def makeName(self):
        p = 'abcdefghijklmnopqrstuvwxyz'
        return p[int(random.random()*len(p))]
        p = 'bcdfghjklmnpqrstvwxyz'
        f = p[int(random.random()*len(p))]
        p = 'aeiou'
        s = p[int(random.random()*len(p))]
        p = 'bcdfgjklmnpqrstvwxyz'
        l = p[int(random.random()*len(p))]
        return f'{f}{s}{l}'

    def inodeAlloc(self):
        return self.ibitmap.alloc()

    def inodeFree(self, inum):
        self.ibitmap.free(inum)
        self.inodes[inum].free()

    def dataAlloc(self):
        return self.dbitmap.alloc()

    def dataFree(self, bnum):
        self.dbitmap.free(bnum)
        self.data[bnum].free()

    def getParent(self, name):
        tmp = name.split('/')
        if len(tmp) == 2:
            return '/'
        pname = ''
        for i in range(1, len(tmp)-1):
            pname += '/' + tmp[i]
        return pname

    def deleteFile(self, name):
        if self.printOps:
            print('unlink("{name}");')
        inum = self.nameToInum[name]

        if self.inodes[inum].getRefCnt() == 1:
            # free data block first
            dblock = self.inodes[inum].getAddr()
            if dblock != -1:
                self.dataFree(dblock)
            # then free inode
            self.inodeFree(inum)
        else:
            self.inodes[inum].decRefCnt()

        # remove from parent directory
        parent = self.getParent(name)
        # print '--> delete from parent', parent
        pInum = self.nameToInum[parent]
        pblock = self.inodes[pInum].getAddr()
        # decrease parent inode ref count
        self.inodes[pInum].decRefCnt()
        # print '--> delete from parent address', pblock
        self.data[pblock].delDirEntry(name)

        # finally, remove from files list
        self.files.remove(name)
        return 0

    def createLink(self, target, newFile, parent):
        # find info about parent
        parentInum = self.nameToInum[parent]
        
        # if there is some space in the parent directory
        pblock = self.inodes[parentInum].getAddr()
        if self.data[pblock].getFreeEntries() <= 0:
            print('*** createLink failed: not enough space in the parent directory ***')
            return -1
        
        if self.data[pblock].dirEntryExists(newFile):
            print('*** createLink failed: not a unique name')
            return -1
        
        # now find inumber of target
        tinum = self.nameToInum[target]
        self.inodes[tinum].incRefCnt()

        # inc parent ref count
        self.inodes[parentInum].incRefCnt()

        # now add to directory
        tmp = newFile.split('/')
        ename = tmp[len(tmp)-1]
        self.data[pblock].addDirEntry(ename, tinum)
        return tinum

    def createFile(self, parent, newfile, ftype):
        # find info about parent
        parentInum = self.nameToInum[parent]
        # is there room in the parent directory?
        pblock = self.inodes[parentInum].getAddr()

        if self.data[pblock].getFreeEntries() <= 0:
            print('*** createFile failed: not enough space in parent directory ***')
            return -1

        # have to make sure file name is unique
        block = self.inodes[parentInum].getAddr()
        # print 'is %s in directory %d' % (newfile, block)
        if self.data[block].dirEntryExists(newfile):
            print('*** createFile failed: not a unique name ***')
            return -1

        # find free inode
        inum = self.inodeAlloc()
        if inum == -1:
            print('*** createFile failed: no inodes left ***')
            return -1

        # if a directory, have to allocate directory block for basic (., ..) info
        fblock = -1
        if ftype == 'dir':
            refCnt = 2
            fblock = self.dataAlloc()
            if fblock == -1:
                print('*** createFile failed: no data blocks left ***')
                self.inodeFree(inum)
                return -1
            else:
                self.data[fblock].setType('dir')
                self.data[fblock].addDirEntry('.',  inum)
                self.data[fblock].addDirEntry('..', parentInum)
        else:
            refCnt = 1

        # now ok to init inode properly
        self.inodes[inum].setAll(ftype, fblock, refCnt)

        # inc parent ref count
        self.inodes[parentInum].incRefCnt()

        # and add to directory of parent
        self.data[pblock].addDirEntry(newfile, inum)
        return inum

    def writeFile(self, tfile, data):
        inum = self.nameToInum[tfile]
        curSize = self.inodes[inum].getSize()
        print(f'writeFile: inum: {inum} cursize: {curSize} refcnt: {self.inodes[inum].getRefCnt()}')
        
        if curSize == 1:
            print('*** writeFile failed: file is full ***')
            return -1

        fblock = self.dataAlloc()
        if fblock == -1:
            print('*** writeFile failed: no data blocks left ***')
            return -1
        else:
            self.data[fblock].setType('file')
            self.data[fblock].addData(data)
        self.inodes[inum].setAddr(fblock)
        
        if self.printOps:
            print(f'fd=open("{file}", O_WRONLY|O_APPEND); write(fd, buf, BLOCKSIZE); close(fd);')
        return 0

    def doDelete(self):
        print('doDelete')
        if len(self.files) == 0:
            return -1
        dfile = self.files[int(random.random() * len(self.files))]
        print(f'try delete({dfile})')
        return self.deleteFile(dfile)

    def doLink(self):
        print('doLink')
        if len(self.files) == 0:
            return -1
        parent = self.dirs[int(random.random() * len(self.dirs))]
        nfile = self.makeName()

        # pick random target
        target = self.files[int(random.random() * len(self.files))]

        # get full name of newfile
        if parent == '/':
            fullName = parent + nfile
        else:
            fullName = parent + '/' + nfile

        print(f'try createLink({target} {nfile} {parent}')
        inum = self.createLink(target, nfile, parent)
        if inum >= 0:
            self.files.append(fullName)
            self.nameToInum[fullName] = inum
            if self.printOps:
                print(f'link({target}, {fullName});')
            return 0
        return -1

    def doCreate(self, ftype):
        print('doCreate')
        parent = self.dirs[int(random.random() * len(self.dirs))]
        nfile = self.makeName()
        if ftype == 'dir':
            tlist = self.dirs
        else:
            tlist = self.files

        if parent == '/':
            fullName = parent + nfile
        else:
            fullName = parent + '/' + nfile

        print(f'try createFile({parent} {nfile} {ftype})')
        inum = self.createFile(parent, nfile, ftype)
        if inum >= 0:
            tlist.append(fullName)
            self.nameToInum[fullName] = inum
            if parent == '/':
                parent = ''
            if ftype == 'dir':
                if self.printOps:
                    print(f'mkdir({parent} {nfile})')
            else:
                if self.printOps:
                    print(f'create({parent} {nfile})')
            return 0
        return -1

    def doAppend(self):
        print('doAppend')
        if len(self.files) == 0:
            return -1
        afile = self.files[int(random.random() * len(self.files))]
        print(f'try writeFile({afile})')
        data = chr(ord('a') + int(random.random() * 26))
        rc = self.writeFile(afile, data)
        return rc

    def run(self, numRequests):
        self.percentMkdir  = 0.40
        self.percentWrite  = 0.40
        self.percentDelete = 0.20
        self.numRequests   = 20

        print('Initial state')
        self.dump()

        for i in range(numRequests):
            if self.printOps == False:
                print('Which operation took place?')
            rc = -1
            while rc == -1:
                r = random.random()
                if r < 0.3:
                    rc = self.doAppend()
                    print(f'doAppend rc: {rc}')
                elif r < 0.5:
                    rc = self.doDelete()
                    print(f'doDelete rc: {rc}')
                elif r < 0.7:
                    rc = self.doLink()
                    print(f'doLink rc: {rc}')
                else:
                    if random.random() < 0.75:
                        rc = self.doCreate('file')
                        print(f'doCreate(f) rc: {rc}')
                    else:
                        rc = self.doCreate('dir')
                        print(f'doCreate(d) rc: {rc}')
            if self.printState == True:
                self.dump()
            else:
                print('State of file system (inode bitmap, inodes, data bitmap, data)?')

        if self.printFinal:
            print('Summary of files, directories::')
            print(' Files:', self.files)
            print(' Directories:', self.dirs)