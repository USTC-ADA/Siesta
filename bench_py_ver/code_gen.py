import os
from typing import List
from block import Block
from block_to_code import Code
from opt import Convexopt
from minibench import Minibench
from mpi4py import MPI
import argparse
import pickle
from val_correction import Correction


import sys
print("python version: %s" % (sys.version))

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

my_cmd_papi = " -I/gpfs/home/cs/sunjw/common/papi/include -L/gpfs/home/cs/sunjw/common/papi/lib -std=c99 -lpapi "
path = './'

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', dest='outprefix', default='/gpfs/home/cs/sunjw/addition/run/sequitur-main/', help='output Filename')
    args = parser.parse_args() 
    return args
args = getArgs()

param_for_x = []
cache_intercept = [[] for _ in range(3)]
if rank == 0:
    bench = Minibench(my_cmd_papi)
    param_for_x,cache_intercept = bench.fit()
    print(param_for_x)
comm.barrier()
param_for_x = comm.bcast(param_for_x, 0)
cache_intercept = comm.bcast(cache_intercept, 0)
comm.barrier()

def get_now_metric(block:Block,env_var) -> List:
    global my_cmd_papi,path
    os.environ["PAPI_MON_EVENTS"] = env_var
    codename = 'temp_block' + str(rank)
    code = Code(path,[block],'withpapi',codename)
    code.gen_code()
    cmd = "gcc "+code.codec+my_cmd_papi+"-o "+ codename
    os.system(cmd)
    f = os.popen(path+codename)
    metric = f.readline().strip().split(" ")
    return [int(i) for i in metric]

def print_compare_block(block:Block):
    now_metric = get_now_metric(block,'PAPI_LST_INS:PAPI_L2_DCA:PAPI_TOT_INS:PAPI_TOT_CYC')
    now_metric += get_now_metric(block,'PAPI_BR_CN:PAPI_BR_MSP')
    print(block.target)
    print(now_metric)

def find_best_block(block:Block):
    global param_for_x
    
    y = [block.target[block.trans['cyc']],block.target[block.trans['ins']],block.target[block.trans['lst']],
        block.target[block.trans['l1_dcm']],block.target[block.trans['br_cn']],block.target[block.trans['br_msp']]]
    perf_sum = [block.perf_sum[block.trans['cyc']],block.perf_sum[block.trans['ins']],block.perf_sum[block.trans['lst']],
        block.perf_sum[block.trans['l1_dcm']],block.perf_sum[block.trans['br_cn']],block.perf_sum[block.trans['br_msp']]]
        
    Opt = Convexopt(y,param_for_x,perf_sum)

    block.param.add,block.param.add2,block.param.div,block.param.div2,block.param.iter1,block.param.iter2,block.param.msp1,block.param.msp2,block.param.l1cache_ins,block.param.l1cache_cyc,block.param.l1cache_lst = Opt.findmin()

    print(block.param.add,block.param.add2,block.param.div,block.param.div2,block.param.iter1,block.param.iter2,block.param.msp1,block.param.msp2,block.param.l1cache_ins,block.param.l1cache_cyc,block.param.l1cache_lst)
    print_compare_block(block)




if __name__ == "__main__":
    # data = {0:[3553994, 944940, 10829901, 8935896, 1222192, 38088],14: [3553175, 652521, 7827437, 8493163, 1221921, 38080]}#,0:[271106535, 22401931, 871214238, 1695648148, 207987193, 9553246]}
    with open(args.outprefix+'data_bucket', "rb") as fin:
        data = pickle.load(fin)
        perf_sum = pickle.load(fin)
        performanceDict = pickle.load(fin)
        if rank == 0:
            print(data)
            print(perf_sum)
            print(performanceDict)
    blocks = []
    perf_sum = [perf_sum[i]/sum(perf_sum) for i in range(len(perf_sum))]
    corr = Correction(data,perf_sum,performanceDict,param_for_x)
    data = corr.correction()
    
    # count = 0
    # for i in data.values():
    #     target = i
    #     print(count)
    #     block = Block(target,count)
    #     find_best_block(block)
    #     blocks.append(block)
    #     count += 1
    # code = Code(path,blocks,'withoutpapi','block')
    # code.gen_code()
    
    data_length = len(data)
    targets = list(data.values())
    for i in range(rank, data_length, size):
        target = targets[i]
        block = Block(target, i,perf_sum)
        find_best_block(block)
        blocks.append(block)
        print(i)

    comm.barrier()
    gathered_blocks = comm.gather(blocks, 0)
    comm.barrier()
    if rank == 0:
        all_blocks = []
        for line in gathered_blocks:
            for elem in line:
                all_blocks.append(elem)
        code = Code(path,all_blocks,'withoutpapi','block')
        code.gen_code()
    comm.barrier()


    # data in input.txt
    # with open('./input.txt','r') as f:
    #     n = int(f.readline())
    #     blocks = []
    #     for i in range(n):
    #         target = [int(j) for j in f.readline().split(',')]
    #         block = Block(target,i)
    #         find_best_block(block)
    #         blocks.append(block)
    #     code = Code(path,blocks,'withoutpapi','block')
