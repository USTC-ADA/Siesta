import argparse

from mpi4py import MPI
from with_compute import allGather, computeBlockHash, gen_compute_dict, label_small_block, sum_all_perf
from sequitur import _print_rules, process_grammar
from code_generation import code_generation
import global_val
import combine_comm
import pickle
import merge_main_rule
from constant import PERFORMANCE_DIM

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tracepath', '-t', dest='pathPrefix', default='/home/yantao/run/sequitur/flash_traces_new/', help='trace file path prefix')
    parser.add_argument('--output', '-o', dest='outprefix', default='/home/yantao/run/sequitur/', help='output Filename')
    parser.add_argument('--platforms', '-p', dest='platform', default=None, help='output Filename')
    parser.add_argument('--scaling', '-s', dest='scaling_factor', default=1, help='the benchmark execution time will scaling by this factor')
    args = parser.parse_args() 
    return args


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
global_val.size = comm.Get_size()
global_val.rank = rank
args = getArgs()
output_filename = args.outprefix+'code{}.c'.format(rank)
pathPrefix = args.pathPrefix
scaling_factor = int(args.scaling_factor)
trace_name = pathPrefix+str(rank)+'.trace'

# print('getting trace from {}'.format(trace_name))
global_val.truncateDict, global_val.redirect, global_val.bucket, global_val.requestDict, global_val.performanceDict = computeBlockHash(trace_name)

global_val.requestUsed = [False]*len(global_val.requestDict)

data = allGather(comm, rank, global_val.performanceDict, global_val.bucket)

comm.barrier()

global_val.perf_sum = sum_all_perf(comm, rank, global_val.perf_sum)

comm.barrier()

if rank == 0:
    with open(args.outprefix+'data_bucket', "wb") as fout:
        for key in data['bucket'].keys():
            for i in range(PERFORMANCE_DIM):
                data['bucket'][key][i] = data['bucket'][key][i]//scaling_factor
                if data['bucket'][key][i] <= 0:
                    data['bucket'][key][i] = 1
        for i in range(len(global_val.perf_sum)):
            global_val.perf_sum[i] = global_val.perf_sum[i]//scaling_factor
            if global_val.perf_sum[i] == 0:
                global_val.perf_sum[i] = 1
        pickle.dump(data['bucket'], fout)
        pickle.dump(global_val.perf_sum, fout)
        pickle.dump(data['performanceDict'], fout)

mergeDict = data['mergeDicts'][rank]

if rank == 0:
    label_small_block(data['bucket'])

global_val.redirect = {key: mergeDict[global_val.redirect[key]] for key in global_val.redirect}

gen_compute_dict(data)

data = comm.gather(global_val.computeDict, 0)

process_grammar(trace_name)

main_rules, unique_dict, rule_dict = combine_comm.comm_combine(rank=rank, comm=comm, outprefix=args.outprefix+'/cst-cfg-logs/')

global_val.main_rules, global_val.unique_dict, global_val.rule_dict = main_rules, unique_dict, rule_dict

global_val.id_signature_table = dict(zip(global_val.call_signature_table.values(), global_val.call_signature_table.keys()))

global_val.non_terminal_dict = dict(zip(global_val.unique_dict.values(), global_val.unique_dict.keys()))

data = comm.gather(global_val.call_signature_table, 0)

comm.barrier()

data = comm.gather(global_val.computeDict, 0)

comm.barrier()

unique_main_rules = merge_main_rule.combine_main_rule(rank, comm, global_val.main_rules, global_val.rule_dict)

if rank == 0:
    global_val.lcs_main_rules = unique_main_rules

comm.barrier()

if rank == 0:
    print(global_val.gathered_cst)

code_generation(args.outprefix, output_filename, len(global_val.requestDict), rank, comm, scaling_factor)

if rank == 0:
    print('communication cnt = {}'.format(len(global_val.gathered_cst)-len(global_val.computeDict)))
    print('computation cnt = {}'.format(len(global_val.computeDict)))
    print('non_term cnt = {}'.format(len(global_val.non_terminal_dict)))
    print('small code blcok cnt = {}'.format(global_val.small_block_cnt))
    main_rule_ids = [-int(global_val.rule_dict[main_rule].id) for main_rule in global_val.main_rules]
    try:
        with open(args.outprefix+'gathered_cst', "wb") as fout:
            pickle.dump(global_val.gathered_cst, fout)
        with open(args.outprefix+'non_terminal_dict', "wb") as fout:
            pickle.dump(global_val.non_terminal_dict, fout)
        with open(args.outprefix+'computeDict', "wb") as fout:
            pickle.dump(global_val.computeDict, fout)
        with open(args.outprefix+'requestDict', "wb") as fout:
            pickle.dump(len(global_val.requestDict), fout)
        with open(args.outprefix+'rules_list', "wb") as fout:
            pickle.dump(global_val.rules_list, fout)
        with open(args.outprefix+'comm_cnt', "wb") as fout:
            pickle.dump(global_val.comm_cnt, fout)
        with open(args.outprefix+'main_rule_ids', "wb") as fout:
            pickle.dump(main_rule_ids, fout)
        with open(args.outprefix+'rule_dict', "wb") as fout:
            pickle.dump(global_val.rule_dict, fout)
        with open(args.outprefix+'lcs_main_rules', "wb") as fout:
            pickle.dump(global_val.lcs_main_rules, fout)

        with open(args.outprefix+'compressed_trace', "wb") as fout:
            pickle.dump(global_val.gathered_cst, fout)
            pickle.dump(global_val.non_terminal_dict, fout)
            pickle.dump(global_val.computeDict, fout)
            pickle.dump(len(global_val.requestDict), fout)
            pickle.dump(global_val.rules_list, fout)
            pickle.dump(global_val.comm_cnt, fout)
            pickle.dump(main_rule_ids, fout)
    except Exception as e:
        print(e)
        print('dump compressed trace failed! please review. this may be cause by maximum recursion depth exceeded while pickling an object')

if rank == 0:
    print('######## test only compress mpi events ########')
process_grammar(trace_name, process_type='mpi')

main_rules, unique_dict, rule_dict = combine_comm.comm_combine(rank=rank, comm=comm, outprefix=args.outprefix+'/cst-cfg-mpi-logs/')
non_terminal_dict = dict(zip(unique_dict.values(), unique_dict.keys()))

if rank == 0:
    print(global_val.gathered_cst)
    print(non_terminal_dict)
    
process_grammar(trace_name, process_type='compute')
main_rules, unique_dict, rule_dict = combine_comm.comm_combine(rank=rank, comm=comm, outprefix=args.outprefix+'/cst-cfg-compute-logs/')
non_terminal_dict = dict(zip(unique_dict.values(), unique_dict.keys()))

if rank == 0:
    print('######## end test only compress mpi events ########')
