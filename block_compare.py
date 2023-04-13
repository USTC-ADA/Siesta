#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
from statistics import mean
import copy
import os
import argparse
from with_compute import allGather
from mpi4py import MPI
from math import log10
from constant import THRESHOLD, CYC_THRESHOLD, SIMILARITY, CYC_SIMILARITY, ABSOLUTE_DELTA, PERFORMANCE_DIM
from with_compute import isSimilar, redirectList, dataHandler, findAKey,weightMergeBucket
from utils import add_seprate_symbol_after_path

def computeBlockHash(filename):
    f = open(filename, "r")
    line = f.readline()
    performanceDict = {}
    bucket = {}  # dict { (performance tuple): [这个bucket的计数, 这个bucket的代号] }
    lineCount = 0  # 用来对总的行数进行记录，并无实际作用，只是用来对比一下数据
    bucketCount = 0  # 用来记录已经用了多少个bucket了
    blockList = []  # 用来存储聚类之后的block的序列信息，只保存对应的代号
    bucketDict = {}  # dict { bucket代号: [performance tuple] }
    requestDict = {} # dict { request_addr: request_id }
    perf_sum = [0]*PERFORMANCE_DIM
    while line:
        if "MPI_Compute" in line:
            line = line.strip()
            s = line.split(',')[2]
            s = s.split(';')[:6]
            values = [int(val) for val in s]
            afterHandle = dataHandler(values)
            if afterHandle in bucket:
                # bucketDict中对应的元素加权求平均
                temp = (bucketDict[bucket[afterHandle][1]])
                for i in range(len(temp)):
                    temp[i] *= bucket[afterHandle][0]
                    temp[i] += values[i]
                bucketDict[bucket[afterHandle][1]] = [int(val / (bucket[afterHandle][0] + 1)) for val in temp]
                bucket[afterHandle][0] += 1
                
            else:
                bucketDict[bucketCount] = values
                bucket[afterHandle] = [1, bucketCount]
                bucketCount += 1
            for i in range(PERFORMANCE_DIM):
                perf_sum[i] += values[i]
            blockList.append(bucket[afterHandle][1])
            lineCount += 1
        else:
            s = line.split('\n')[0].split(',')
            request = s[len(s)-1]
            if request not in requestDict:
                requestDict[request] = len(requestDict)
        line = f.readline()

    # 准备返回的数据
    truncateDict = {val: bucket[val][1] for val in bucket.keys()}
    # 遍历bucket，如果LST, L1_DCM, INS, BR_CN 和 BR_MSP 都相同，只有 CYC 不同，则将他们合并
    fiveSimilar = {}
    redirect = {}  # 因为需要删除一些代号，所以需要重定向一下旧的代号 TODO 处理有问题，不影响合并代码块
    for key in bucket.keys():
        five = (key[0], key[1], key[2], key[4], key[5])
        # if str(key[0]).find('530') >= 0:
        #     print(key[3]) 
        if five in fiveSimilar:
            # 合并两个记录
            # 以第一个出现的记录为准，重定向bucketDict中的记录
            bucketDict[bucket[key][1]] = bucketDict[fiveSimilar[five]]
            # 删除后者在bucket中的记录，加权求CYC的均值
            
            bucketDict[fiveSimilar[five]][3] = int(
                (bucketDict[fiveSimilar[five]][3] * performanceDict[fiveSimilar[five]] + key[3] * bucket[key][0]) / (
                        performanceDict[fiveSimilar[five]] + bucket[key][0]))
            performanceDict[fiveSimilar[five]] += bucket[key][0]
            redirect[bucket[key][1]] = fiveSimilar[five]
            bucketDict.pop(bucket[key][1])
        else:
            fiveSimilar[five] = bucket[key][1]
            performanceDict[bucket[key][1]] = bucket[key][0]
            redirect[bucket[key][1]] = bucket[key][1]

    bucket = bucketDict
    preLen = 0
    while preLen != len(bucket):
        preLen = len(bucket)
        bucketDict = bucket
        bucket = {}  # 清空这个bucket回收利用一下
        # 第二次合并，一定程度上相似就合并
        for key in bucketDict.keys():
            findASimilar = False
            for other in bucket.keys():
                if isSimilar(bucket[other], bucketDict[key]):
                    # 如果找到一个不是自己，且比较相似的，则合并他们
                    for i in range(PERFORMANCE_DIM):
                        bucket[other][i] = int(
                            (bucket[other][i] * performanceDict[other] + bucketDict[key][i] * performanceDict[key]) / (
                                    performanceDict[other] + performanceDict[key]))
                    performanceDict[other] += performanceDict[key]
                    performanceDict.pop(key)
                    findASimilar = True
                    # 需要磨抹平redirect：
                    redirect = redirectList(redirect, key, other)
                    break
            if not findASimilar:
                # 没有找到就加进来
                bucket[key] = bucketDict[key]
    blockList = [redirect[val] for val in blockList]
    return bucket, performanceDict, blockList, perf_sum


def parse_trace(filename):
    f = open(filename)
    start_time_list = []
    end_time_list = []
    line = f.readline()
    while line:
        if "MPI_Compute" in line:
            line = line.strip()
            s = line.split(',')[2]
            s = s.split(';')[:6]
        else:
            s = line.split('\n')[0].split(',')
            start_time = int(s[3])
            end_time = int(s[4])
            
            start_time_list.append(start_time)
            end_time_list.append(end_time)
        line = f.readline()
    f.close()
    return start_time_list, end_time_list


def parse_compute_time(block_list, start_time_list, end_time_list, performance_dict):
    length = len(block_list)
    i = 0
    bucket = {}
    while i < length-1:
        if block_list[i] not in bucket:
            bucket[block_list[i]] = 0
        bucket[block_list[i]] += start_time_list[i+1]-end_time_list[i]
        i += 1
    return bucket


def parse_avg_compute_time(block_list, start_time_list, end_time_list, performance_dict):
    length = len(block_list)
    i = 0
    bucket = {}
    while i < length-1:
        if block_list[i] not in bucket:
            bucket[block_list[i]] = 0
        bucket[block_list[i]] += start_time_list[i+1]-end_time_list[i]
        i += 1
    for key in bucket.keys():
        bucket[key] = bucket[key]/performance_dict[key]
    return bucket


def parse_cyc(real_block_list, bench_block_list, bench_bucket, performance_dict):
    """
    把 bench_bucket 按照 real_block_list 重新压缩一遍
    """
    length = len(real_block_list)
    i = 0
    actual_bucket = {}
    for i in range(length):
        if real_block_list[i] not in actual_bucket:
            actual_bucket[real_block_list[i]] = copy.copy(bench_bucket[bench_block_list[i]])
        else:
            for j in range(6):
                actual_bucket[real_block_list[i]][j] += copy.copy(bench_bucket[bench_block_list[i]][j])
    for key in actual_bucket:
        for j in range(6):
            actual_bucket[key][j] = actual_bucket[key][j] //performance_dict[key]
    return actual_bucket 


def sum_all_perf(comm, rank, perf_sum):
    res = np.zeros(6, dtype='l')
    sendbuf = np.array(perf_sum, dtype='l')

    comm.Reduce(sendbuf, res, root=0, op=MPI.SUM)
    # if rank == 0:
    #     print('second platform perf_sum = {}'.format(res))
    return res


def block_compare_multiplat(basic_trace_path, other_plat_trace_paths, comm, rank):
    """
    由于不同平台、不同单次运行生成的trace 具有随机性
    单独对两次运行的 trace 进行计算代码块的合并会出现合并后的代码块结果不一样的情况
    根据 basic_trace_path 下的 trace 合并 other_plat_trace_paths 中的计算代码块
    basic_trace_path: str, 作为基准的 trace 所在的路径, 默认所有生成的 trace 名称都是 ${rank}.trace
    other_plat_trace_paths: [str], 其他平台运行所得到的trace的路径
    comm: MPI 结构体
    rank: 当前运行的程序 rank id
    """
    # 1. 对基准平台的 trace 进行压缩，获得单个进程的 trace 计算代码块压缩结果
    f1 = add_seprate_symbol_after_path(basic_trace_path)+'{}.trace'.format(rank)
    cur_plat_bucket, cur_plat_performanceDict, cur_plat_blockList, cur_plat_perf_sum = computeBlockHash(f1)
    
    # 2. 基准平台 trace 的进程间合并
    data = allGather(comm, rank, cur_plat_performanceDict, cur_plat_bucket)

    # 3. 对其余平台 trace 进行单进程压缩
    other_plat_buckets, other_plat_performanceDicts, other_plat_blockLists, other_plat_perf_sums = [], [], [], []
    for other_plat_trace_path in other_plat_trace_paths:
        f2 = add_seprate_symbol_after_path(other_plat_trace_path)+'{}.trace'.format(rank)
        other_plat_bucket, other_plat_performanceDict, other_plat_blockList, other_plat_perf_sum = computeBlockHash(f2)
        # 加到列表里面来
        other_plat_buckets.append(other_plat_bucket)
        other_plat_performanceDicts.append(other_plat_performanceDict)
        other_plat_blockLists.append(other_plat_blockList)
        other_plat_perf_sums.append(other_plat_perf_sum)
    
    # 4. 根据基准平台当前进程的进程内计算代码块压缩结果去压缩其他平台的计算代码块
    buckets = []
    for i in range(len(other_plat_trace_paths)):
        bucket = parse_cyc(cur_plat_blockList, other_plat_blockLists[i], other_plat_buckets[i], cur_plat_performanceDict)
        buckets.append(bucket)
    
    # 5. 将所有其余平台的进程内压缩结果根据基准平台进程间压缩的结果做一次映射
    cur_plat_merged_bucket = data['bucket']
    merge_dict = data['mergeDicts'][rank]
    buckets_with_bench, buckets_cnt_with_bench = [], []
    for bucket in buckets:
        bucket_with_bench = {key : [0,0,0,0,0,0] for key in cur_plat_merged_bucket.keys()}
        bucket_cnt_with_bench = {key : 0 for key in cur_plat_merged_bucket.keys()}
        for key in bucket.keys():
            for i in range(6):
                # important! 注意这里乘以 cur_plat_performanceDict 是因为已经将其他平台的计算代码块根据基准平台的压缩结果压缩了
                bucket_with_bench[merge_dict[key]][i]+=bucket[key][i]*cur_plat_performanceDict[key]
            bucket_cnt_with_bench[merge_dict[key]] += cur_plat_performanceDict[key]
        buckets_with_bench.append(bucket_with_bench)
        buckets_cnt_with_bench.append(bucket_cnt_with_bench)

    # 6. 将所有结果收集起来，统一交给0号进程去做最后的合并
    comm.barrier()
    other_plat_buckets = comm.gather(buckets_with_bench, 0) # [size*[other_plat_res]]
    other_plat_buckets_cnt = comm.gather(buckets_cnt_with_bench, 0)
    comm.barrier()

    # 7. 由0号进程做最后的合并
    if rank == 0:
        final_buckets = []
        final_performanceDicts = []
        cur_plat_final_bucket = data['bucket']
        for i in range(len(other_plat_trace_paths)):
            final_bucket = {key:[0,0,0,0,0,0] for key in cur_plat_final_bucket.keys()}
            final_performanceDict = {key:0 for key in cur_plat_final_bucket.keys()}
            for key in cur_plat_final_bucket:
                sum = 0
                for j in range(len(other_plat_buckets)):
                    for k in range(6):
                        final_bucket[key][k] += other_plat_buckets[j][i][key][k]
                    sum += other_plat_buckets_cnt[j][i][key]
                final_performanceDict[key] = sum
                for j in range(6):
                    final_bucket[key][j] /= sum
            
            for key in final_performanceDicts:
                if final_performanceDicts[key] < 1 and key in cur_plat_bucket:
                    del(final_bucket[key])
                    del(cur_plat_merged_bucket[key])

            final_buckets.append(final_bucket)
            final_performanceDicts.append(final_performanceDict)
    comm.barrier()

    # 8. 计算 perf_sum
    cur_plat_perf_sum = sum_all_perf(comm, rank, cur_plat_perf_sum)
    other_plat_perf_sums = [sum_all_perf(comm, rank, other_plat_perf_sum) for other_plat_perf_sum in other_plat_perf_sums]
    comm.barrier()
    perf_sum_all = list(cur_plat_perf_sum)
    for other_plat_perf_sum in other_plat_perf_sums:
        perf_sum_all += list(other_plat_perf_sum)

    return final_buckets, cur_plat_merged_bucket, perf_sum_all, final_performanceDicts


def block_compress(f1, f2, comm, rank):
    bench_bucket, bench_performanceDict, bench_blockList, bench_perf_sum = computeBlockHash(f1)
    real_bucket, real_performanceDict, real_blockList, real_perf_sum = computeBlockHash(f2)

    data = allGather(comm, rank, real_performanceDict, real_bucket)

    mergeDict = data['mergeDicts'][rank]
    bucket = parse_cyc(real_blockList, bench_blockList, bench_bucket, real_performanceDict)

    merged_real_bucket = data['bucket']
    bucket_cnt = len(merged_real_bucket.keys())

    actual_bench_bucket = {key : [0,0,0,0,0,0] for key in merged_real_bucket.keys()}
    actual_bucket_cnt = {key : 0 for key in merged_real_bucket.keys()}

    for key in bucket.keys():
        for i in range(6):
            actual_bench_bucket[mergeDict[key]][i]+=bucket[key][i]*real_performanceDict[key]
        actual_bucket_cnt[mergeDict[key]] += real_performanceDict[key]

    comm.barrier()

    bench_data_bucket = comm.gather(actual_bench_bucket, 0)
    bench_data_bucket_cnt = comm.gather(actual_bucket_cnt, 0)

    comm.barrier()
    if rank == 0:
        # print(rank, actual_bench_bucket)
        # print(rank, bench_data_bucket)
        real_bucket = merged_real_bucket
        bucket = {key:[0,0,0,0,0,0] for key in real_bucket.keys()}
        real_performanceDict = {key:0 for key in real_bucket.keys()}
        sum = 0
        for key in real_bucket.keys():
            sum = 0
            for i in range(len(bench_data_bucket)):
                for j in range(6):
                    bucket[key][j] += bench_data_bucket[i][key][j]
                sum += bench_data_bucket_cnt[i][key]
            real_performanceDict[key] = sum
            for j in range(6):
                bucket[key][j] /= sum
        # print(bucket)
        # print(real_bucket)

        for key in real_performanceDict:
            if real_performanceDict[key] < 1 and key in real_bucket:
                del(bucket[key])
                del(real_bucket[key])
        
    comm.barrier()

    bench_perf_sum = sum_all_perf(comm, rank, bench_perf_sum)
    real_perf_sum = sum_all_perf(comm, rank, real_perf_sum)

    comm.barrier()
    


    perf_sum_12 = list(real_perf_sum) + list(bench_perf_sum)
    # if rank == 0:
    #     print(real_perf_sum, bench_perf_sum, perf_sum_12)
    return bucket, real_bucket, perf_sum_12, real_performanceDict


if __name__ == 'main':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', '-n', dest='name', default='sweep3d', help='program name')
    # parser.add_argument('--procs', '-p', dest='procs', default='16', help='proc number')
    args = parser.parse_args() 
    name = args.name
    procs = comm.size
    trace_name = '0.trace'
    SEQUITUR_PATH='/home/cs/sunjw/addition/run/sequitur-main'
    BENCHMARK_PATH='benchmark'
    benchmark_path = '{}/{}/{}/'.format(SEQUITUR_PATH, name, BENCHMARK_PATH)
    trace_path = '{}/{}/'.format(SEQUITUR_PATH, name)

    output_dir_name = '{}/{}/block_compare'.format(SEQUITUR_PATH, name)

    if rank == 0:
        if not os.path.exists(trace_path):
            print('trace dir does not exist!')
            exit(-1)

        if not os.path.exists(benchmark_path):
            print('benchmark dir does not exist!')
            exit(-1)

    if not os.path.exists(output_dir_name):
        os.mkdir(output_dir_name)
    f1 = benchmark_path+'{}.trace'.format(rank)
    f2 = trace_path+'{}.trace'.format(rank)

    bench_bucket, bench_performanceDict, bench_blockList, bench_perf_sum = computeBlockHash(f1)
    real_bucket, real_performanceDict, real_blockList, real_perf_sum = computeBlockHash(f2)

    data = allGather(comm, rank, real_performanceDict, real_bucket)

    # if rank == 1:
    #     print(data)

    mergeDict = data['mergeDicts'][rank]

    bucket = parse_cyc(real_blockList, bench_blockList, bench_bucket, real_performanceDict)

    # bench_blockLists = comm.gather(bench_blockList, 0)
    # real_blockLists = comm.gather(real_blockList, 0)

    merged_real_bucket = data['bucket']
    bucket_cnt = len(merged_real_bucket.keys())

    actual_bench_bucket = {key : [0,0,0,0,0,0] for key in merged_real_bucket.keys()}
    actual_bucket_cnt = {key : 0 for key in merged_real_bucket.keys()}


    for key in bucket.keys():
        for i in range(6):
            actual_bench_bucket[mergeDict[key]][i]+=bucket[key][i]*real_performanceDict[key]
        actual_bucket_cnt[mergeDict[key]] += real_performanceDict[key]


    # 合并
    comm.barrier()

    bench_data_bucket = comm.gather(actual_bench_bucket, 0)
    bench_data_bucket_cnt = comm.gather(actual_bucket_cnt, 0)

    comm.barrier()

    if rank == 0:
        real_bucket = merged_real_bucket
        bucket = {key:[0,0,0,0,0,0] for key in real_bucket.keys()}
        real_performanceDict = {key:0 for key in real_bucket.keys()}
        sum = 0
        for key in real_bucket.keys():
            sum = 0
            for i in range(len(bench_data_bucket)):
                for j in range(6):
                    bucket[key][j] += bench_data_bucket[i][key][j]
                sum += bench_data_bucket_cnt[i][key]
            real_performanceDict[key] = sum
            for j in range(6):
                bucket[key][j] /= sum
        # print(bucket)
        # print(real_bucket)

        for key in real_performanceDict:
            if real_performanceDict[key] < 1 and key in real_bucket:
                del(bucket[key])
                del(real_bucket[key])
        # real_time = real_bucket.values()
        # bench_time = bench_bucket.values()

    if rank == 0:
        perf_name = ['LST', 'L1_DCM', 'INS', 'CYC', 'BR_CN', 'MSP']
        for i in range(6):
            bench_cyc = np.array([bucket[key][i]*real_performanceDict[key] for key in bucket])
            real_cyc = np.array([real_bucket[key][i]*real_performanceDict[key] for key in real_bucket])

            code_blocks = bucket.keys()

            bar_width = 0.3
            index_real = np.arange(len(bench_cyc))
            index_bench = index_real+bar_width
            # real_cyc = [log(val) for val in real_cyc]
            # bench_cyc = [log(val) for val in bench_cyc]
            plt.figure(dpi=400)
            plt.bar(index_real, height=real_cyc, width=bar_width, color='0.3', label='real '+name)
            plt.bar(index_bench, height=bench_cyc, width=bar_width, color='0.7', label='benchmark')

            plt.legend()
            plt.xticks(index_real + bar_width/2, code_blocks, rotation=270)
            plt.xticks(index_real + bar_width/2, code_blocks)
            plt.ylabel(perf_name[i])
            plt.title('code blocks {}'.format(perf_name[i]))


            plt.savefig(output_dir_name+'/'+name+'_code_block_{}.png'.format(perf_name[i]), format='png')

        # In[56]:

        limit = [50000, 1000, 50000, 100000, 1000, 1000]
        perf_name = ['log_LST', 'log_L1_DCM', 'log_INS', 'log_CYC', 'log_BR_CN', 'log_MSP']
        for i in range(6):
            bench_cyc = np.array([bucket[key][i]*real_performanceDict[key] for key in bucket])
            real_cyc = np.array([real_bucket[key][i]*real_performanceDict[key] for key in real_bucket])

            code_blocks = bucket.keys()

            bench_cyc = []
            real_cyc = []
            code_blocks = []
            for key in bucket:
        #        if i == 2:
        #            print(key, real_bucket[key][i], limit[i])
                if real_bucket[key][i]>limit[i]:
                    bench_cyc.append(bucket[key][i])
                    real_cyc.append(real_bucket[key][i])
                    code_blocks.append(key)

            bar_width = 0.3
            index_real = np.arange(len(bench_cyc))
            index_bench = index_real+bar_width
            # real_cyc = [log10(val+1) for val in real_cyc]
            # bench_cyc = [log10(val+1) for val in bench_cyc]  
            plt.figure(dpi=400)
            plt.axes(yscale = "log")
            plt.bar(index_real, height=real_cyc, width=bar_width, color='0.3', label='real '+name)
            plt.bar(index_bench, height=bench_cyc, width=bar_width, color='0.7', label='benchmark')

            plt.legend()  
            

            plt.xticks(index_real + bar_width/2, code_blocks, rotation=270)  
            plt.xticks(index_real + bar_width/2, code_blocks)  
            plt.ylabel(perf_name[i])  
            plt.title('code blocks {}'.format(perf_name[i]))  


            plt.savefig(output_dir_name+'/'+name+'_log_code_block_{}.png'.format(perf_name[i]), format='png')

        perf_name = ['LST', 'L1_DCM', 'INS', 'CYC', 'BR_CN', 'MSP']

        limit = [50000, 1000, 50000, 100000, 1000, 1000]
        # limit = [0,0,0,0,0,0]
            # plt.show()
        for i in range(6):
            bench_cyc = []
            real_cyc = []
            code_blocks = []
            for key in bucket:
        #        if i == 2:
        #            print(key, real_bucket[key][i], limit[i])
                if real_bucket[key][i]>limit[i]:
                    bench_cyc.append(bucket[key][i])
                    real_cyc.append(real_bucket[key][i])
                    code_blocks.append(key)
            # bench_cyc = np.array([bucket[key][i] for key in bucket])
            # real_cyc = np.array([real_bucket[key][i] for key in real_bucket])
        #    if i == 2:
        #        print(code_blocks)    
        #        print(bench_cyc)
        #        print(real_cyc)
        #        print(perf_name[i])

            # code_blocks = bucket.keys()

            real = []
            bench = []
            for j in range(len(bench_cyc)):
                real.append(1)
                bench.append(bench_cyc[j]/(real_cyc[j]))

            bar_width = 0.3
            index_real = np.arange(len(bench_cyc))
            index_bench = index_real+bar_width

            plt.figure(dpi=400)
            plt.bar(index_real, height=real, width=bar_width, color='0.3', label='real '+name)
            plt.bar(index_bench, height=bench, width=bar_width, color='0.7', label='benchmark')

            plt.legend()  
            plt.xticks(index_real + bar_width/2, code_blocks, rotation=270)  
            plt.xticks(index_real + bar_width/2, code_blocks)  
            plt.ylabel(perf_name[i])  
            plt.title('code blocks {}'.format(perf_name[i]))  


            plt.savefig(output_dir_name+'/'+name+'_code_block_subject_{}.png'.format(perf_name[i]), format='png')

    comm.barrier()
