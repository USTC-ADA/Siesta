from math import log2
import os
import argparse
from pickle import FALSE
import sys
from mpi4py import MPI
import copy
from constant import ABSOLUTE_DELTA, CYC_SIMILARITY, PERFORMANCE_DIM, SIMILARITY, TWO_EVENTS_TRACE_SUFFIX, FOUR_EVENTS_TRACE_SUFFIX, TRACE_SUFFIX, THRESHOLD


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--allevents', '-a', action='store_true', dest='allEvents', default=False, help='do all events in a file. True or False')
    parser.add_argument('--tracepath', '-t', dest='pathPrefix', default='/home/xuqingguo/packages/kripke-v1.2.4-d85c6bc/build/bin/', help='trace file path prefix')
    parser.add_argument('--outputpath', '-o', dest='outPathPrefix', default='/home/xuqingguo/src/performance/sequitur/kripke/trace/', help='output trace file path prefix')
    parser.add_argument('--verify', '-v', action='store_true', default=False, help='verify merged trace')
    args = parser.parse_args() 
    return args


def splice_trace(first2EventFile, last4EventFile, outputFileName):
    f1 = open(first2EventFile)
    f2 = open(last4EventFile)
    res = []

    line1 = f1.readline()
    line2 = f2.readline()

    f3 = open(outputFileName, "w")

    while line1:
        s = line2.split(',')
        # print(s)
        try:
            if s[1] == ' MPI_Compute':
                values = s[2].split(';')[:4]
                line = line1.split('\n')[0]+';'.join(values)+';\n'
                f3.write(line)
            else:
                f3.write(line1)
        except Exception as e:
            print(e)
            exit(-1)
            
        line1 = f1.readline()
        line2 = f2.readline()

    f1.close()
    f2.close()
    f3.close()


def splice_by_index(filenames, outputFileName):
    fout = open(outputFileName, "w")
    fins = []
    for filename in filenames:
        fins.append(open(filename))
    
    lines = []
    for fin in fins:
        lines.append(fin.readline())
    
    while len(lines) > 0:
        s = lines[0].split(',')
        try:
            if s[1] == ' MPI_Compute':
                res = lines[0].split('\n')[0]
                metrics = []
                for line in lines:
                    metric = line.split(',')[2].split(';')[:1][0]
                    metrics.append(metric)
                res += ';'.join(metrics)
                res += ';\n'
                fout.write(res)
            else:
                fout.write(lines[0])
        except Exception as e:
            print(e)
            exit(-1)
        lines = []
        for fin in fins:
            lines.append(fin.readline())
    
    for fin in fins:
        fin.close()

    fout.close()



if __name__ == '__main__':
    args = getArgs()

    allEvents = args.allEvents
    PATH_PREFIX = args.pathPrefix
    outprefix = args.outPathPrefix
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if allEvents:
        input_filename = [PATH_PREFIX+str(rank)+'.trace_{}'.format(i) for i in range(6)]

        outputFileName  = str(rank)+TRACE_SUFFIX
        print('reading from {}, output to {}'.format(input_filename, outprefix+outputFileName))
        splice_by_index(input_filename, outprefix+outputFileName)
    else:
        first2EventFile = PATH_PREFIX+str(rank)+TWO_EVENTS_TRACE_SUFFIX
        last4EventFile  = PATH_PREFIX+str(rank)+FOUR_EVENTS_TRACE_SUFFIX
        outputFileName  = str(rank)+TRACE_SUFFIX
        print('reading from {} and {}, output to {}'.format(first2EventFile, last4EventFile, outprefix+outputFileName))
        splice_trace(first2EventFile, last4EventFile, outprefix+outputFileName)
