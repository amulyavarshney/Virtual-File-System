# main program
from fs import FS
import random
import argparse


parser = argparse.ArgumentParser(prog='fs', usage='%(prog)s [options] path', description='Virtual File System')
# parser.parse_args()
# parser.add_argument('-g', '--hello', help='hello print')


parser.add_argument('-s', '--seed',        default=0,     help='the random seed',                      action='store', type=int, dest='seed')
parser.add_argument('-i', '--numInodes',   default=8,     help='number of inodes in file system',      action='store', type=int, dest='numInodes')
parser.add_argument('-d', '--numData',     default=8,     help='number of data blocks in file system', action='store', type=int, dest='numData')
parser.add_argument('-n', '--numRequests', default=10,    help='number of requests to simulate',       action='store', type=int, dest='numRequests')
parser.add_argument('-r', '--reverse',     default=False, help='instead of printing state, print ops', action='store_true',      dest='reverse')
parser.add_argument('-p', '--printFinal',  default=False, help='print the final set of files/dirs',    action='store_true',      dest='printFinal')
parser.add_argument('-c', '--compute',     default=False, help='compute answers for me',               action='store_true',      dest='solve')

# parser.add_argument('-s', '--seed',        default=0,     help='the random seed',                      action='store', type=int, dest='seed')
# parser.add_argument('-i', '--numInodes',   default=8,     help='number of inodes in file system',      action='store', type=int, dest='numInodes')
# parser.add_argument('-d', '--numData',     default=8,     help='number of data blocks in file system', action='store', type=int, dest='numData')
# parser.add_argument('-n', '--numRequests', default=10,    help='number of requests to simulate',       action='store', type=int, dest='numRequests')
# parser.add_argument('-r', '--reverse',     default=False, help='instead of printing state, print ops', action='store_true',      dest='reverse')
# parser.add_argument('-p', '--printFinal',  default=False, help='print the final set of files/dirs',    action='store_true',      dest='printFinal')
# parser.add_argument('-c', '--compute',     default=False, help='compute answers for me',               action='store_true',      dest='solve')

args = parser.parse_args()
# print(args.hello)

print('ARG seed',        args.seed)
print('ARG numInodes',   args.numInodes)
print('ARG numData',     args.numData)
print('ARG numRequests', args.numRequests)
print('ARG reverse',     args.reverse)
print('ARG printFinal',  args.printFinal)

random.seed(args.seed)

if args.reverse:
    printState = False
    printOps   = True
else:
    printState = True
    printOps   = False

if args.solve:
    printState = True
    printOps   = True

printFinal = args.printFinal

#
# have to generate RANDOM requests to the file system
# that are VALID!
#

f = FS(args.numInodes, args.numData, printState, printOps, printFinal)

#
# ops: mkdir rmdir : create delete : append write
#

f.run(args.numRequests)