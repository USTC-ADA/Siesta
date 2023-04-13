import glob
import time
from numpy import ndim
from constant import TAG_FUNC_LIST
import global_val 
from get_function_size import get_func_size
from functools import cache

def parse_ranks(ranks):
    return ranks


def gen_rank_if(ranks):
    res = 'if ( rank == {}'.format(ranks[0])
    i = 1
    while i < len(ranks):
        res += ' || rank =={}'.format(ranks[i])
        i += 1
    res += ') {\n'
    return res


def is_same_list(l1, l2):
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False
    return True


def get_blockId(perf):
    # print(global_val.computeDict)
    return global_val.computeDict[int(perf)]

@cache
def scale_communication(mpi_func_name, size, process_size, scaling_factor):
    # try:
    # return get_func_size(mpi_func_name, size, process_size, scaling_factor)
    # except Exception as e:
    #     # print(e)
    if size >= scaling_factor:
        return size // scaling_factor
    else:
        return 1


def parse_comm_datatype(datatype, datacount):
    if datatype == 4:
        return datacount, 'MPI_INT'
    elif datatype == 8:
        return datacount, 'MPI_DOUBLE'
    
    return datacount*datatype, 'MPI_CHAR'


def parse_comm(comm_str):
    try:
        # print(global_val.comm_map)
        # res = int(global_val.comm_map[comm_str]['id'])
        res = int(comm_str)
    except Exception as e:
        print("unexcepted comm!")
        print(e)
        res = 0
    return res


def handle_multi_request(prefix, requests):
    requests = requests.split(':')
    length = len(requests)
    s = ''
    s += prefix
    # print(global_val.requestDict)
    for i in range(length-1):
        s += 'wait_requests[{}] = requests[{}]; '.format(i, requests[i])
    s += '\n'
    return length-1, s


def handle_multi_dims(prefix, dims):
    dims = dims.split(':')
    length = len(dims)
    s = ''
    s += prefix
    s += 'int use_dims[{}];\n'.format(length-1)
    s += prefix
    for i in range(length-1):
        s += 'use_dims[{}] = {}; '.format(i, dims[i])
    s += '\n'
    return s


def handle_multi_periods(prefix, periods):
    periods = periods.split(':')
    length = len(periods)
    s = ''
    s += prefix
    s += 'int use_periods[{}];\n'.format(length-1)
    s += prefix
    for i in range(length-1):
        s += 'use_periods[{}] = {}; '.format(i, periods[i])
    s += '\n'
    return s


def call_mpi_by_str(s: str, prefix: str, scaling_factor=1):
    s = s.split('\n')[0].split(';')
    mpi_name = s[0]
    datacount = int(s[1])
    datatype = int(s[2])
    target = int(s[3])
    # if target == 9999:
    #     target = 'MPI_ANY_SOURCE'
    requests = s[4]
    request = s[4].split(':')[0]

    cnt, tp = parse_comm_datatype(datatype, datacount)
    cnt = scale_communication(mpi_name, cnt, global_val.size, scaling_factor)

    tag = 0
    if mpi_name in TAG_FUNC_LIST:
        # print()
        tag = int(s[6])

    if mpi_name == 'MPI_Bcast':
        comm = parse_comm(s[5])
        return prefix+'MPI_Bcast(buffer, {}, {}, {}, comms[{}]);\n'.format(cnt, tp, target, comm)
    elif mpi_name == 'MPI_Send':
        comm = parse_comm(s[5])
        return prefix+'MPI_Send(sendbuf, {}, {}, rank-({}), {}, comms[{}]);\n'.format(cnt, tp, target, tag, comm)
    elif mpi_name == 'MPI_Ssend':
        comm = parse_comm(s[5])
        return prefix+'MPI_Ssend(sendbuf, {}, {}, rank-({}), {}, comms[{}]);\n'.format(cnt, tp, target, tag, comm)
    elif mpi_name == 'MPI_Irecv':
        comm = parse_comm(s[5])
        return prefix+'MPI_Irecv(recvbuf, {}, {}, rank-({}), {}, comms[{}], &requests[{}]);\n'.format(cnt, tp, target, tag, comm, request)
    elif mpi_name == 'MPI_Wait':
        return prefix+'MPI_Wait(&requests[{}], &status);\n'.format(request)
    elif mpi_name == 'MPI_Reduce':
        comm = parse_comm(s[5])
        return prefix+'MPI_Reduce(sendbuf, recvbuf, {}, {}, MPI_SUM, {}, comms[{}]);\n'.format(cnt, tp, target, comm)
    elif mpi_name == 'MPI_Barrier':
        comm = parse_comm(s[5])
        return prefix+'MPI_Barrier(comms[{}]);\n'.format(comm)
    elif mpi_name == 'MPI_Allreduce':
        comm = parse_comm(s[5])
        return prefix+'MPI_Allreduce(sendbuf, recvbuf, {}, {}, MPI_MAX, comms[{}]);\n'.format(cnt, tp, comm)
    elif mpi_name == 'MPI_Recv':
        comm = parse_comm(s[5])
        return prefix+'MPI_Recv(recvbuf, {}, {}, rank-({}), {}, comms[{}], &status);\n'.format(cnt, tp, target, tag, comm)
    elif mpi_name == 'MPI_Isend':
        comm = parse_comm(s[5])
        return prefix+'MPI_Isend(sendbuf, {}, {}, rank-({}), {}, comms[{}], &requests[{}]);\n'.format(cnt, tp, target, tag, comm, request)
    elif mpi_name == 'MPI_Waitall':
        num, temp = handle_multi_request(prefix, requests)
        return temp+prefix+'MPI_Waitall({}, wait_requests, MPI_STATUS_IGNORE);\n'.format(num)
    elif mpi_name == 'MPI_Comm_split':
        pre_comm = parse_comm(s[5])
        comm = parse_comm(s[6])
        color = int(s[7])
        key = int(s[8])
        return prefix+'MPI_Comm_split(comms[{}], {}, {}, &comms[{}]);\n'.format(pre_comm, color, key, comm)
    elif mpi_name == 'MPI_Comm_dup':
        pre_comm = parse_comm(s[5])
        comm = parse_comm(s[6])
        return prefix+'MPI_Comm_dup(comms[{}], &comms[{}]);\n'.format(pre_comm, comm)
    elif mpi_name == 'MPI_Comm_free':
        comm = parse_comm(s[5])
        return prefix+'MPI_Comm_free(&comms[{}]);\n'.format(comm)
    elif mpi_name == 'MPI_Allgather':
        comm = parse_comm(s[5])
        return prefix+'MPI_Allgather(sendbuf, {}, {}, recvbuf, {}, {}, comms[{}]);\n'.format(cnt, tp, cnt, tp, comm)
    elif mpi_name == 'MPI_Cart_create':
        pre_comm = parse_comm(s[5])
        comm = parse_comm(s[6])
        ndims = int(s[7])
        reoeder = int(s[8])
        dims = s[9]
        temp1 = handle_multi_dims(prefix, dims)
        periods = s[10]
        temp2 = handle_multi_periods(prefix, periods)
        return temp1+temp2+prefix+'MPI_Cart_create(comms[{}], {}, use_dims, use_periods, {}, &comms[{}]);\n'.format(pre_comm, ndims, reoeder, comm)
    elif mpi_name == 'MPI_Alltoall':
        comm = parse_comm(s[5])
        return prefix+'MPI_Alltoall(sendbuf, {}, {}, recvbuf, {}, {}, comms[{}]);\n'.format(cnt, tp, cnt, tp, comm)
    elif mpi_name == 'MPI_Sendrecv_replace':
        comm = parse_comm(s[5])
        dest = int(s[6])
        tag1 = int(s[7])
        tag2 = int(s[8])
        return prefix+'MPI_Sendrecv_replace(sendbuf, {}, {}, {}, {}, {}, {}, comms[{}], &status);\n'.format(cnt, tp, dest, tag1, target, tag2, comm)
    else:
        return ''


def is_terminal_comm(s: str):
    if s.find('MPI') >= 0:
        isComm = True
    else:
        isComm = False
    return isComm


def convert_id2str(id: int, times: int, depth: int, prefix: str, scaling_factor=1):
    res = ''
    inline_prefix = prefix
    if times > 1:
        res += prefix+'for (int i{} = 0; i{} < {}; i{}++) {{\n'.format(depth, depth, times, depth)
        inline_prefix += '\t'

    if id > 0:
        # 是终结符
        s = global_val.gathered_cst[id]
        if is_terminal_comm(str(s)):
            res += call_mpi_by_str(s, inline_prefix, scaling_factor)
        else:
            # 如果是计算代码块
            #  if int(get_blockId(s)) not in global_val.small_block_list:
            res += inline_prefix + 'block{}();\n'.format(get_blockId(s))
    else:
        # 是非终结符
        ptr = global_val.rules_list[-id].first()
        while True:
            if ptr.is_guard():
                break
            if ptr.is_non_terminal():
                res += convert_id2str(-ptr.rule.index, ptr.exp, depth+1, inline_prefix, scaling_factor)
            else:
                res += convert_id2str(ptr.id, ptr.exp, depth+1, inline_prefix, scaling_factor)
            ptr = ptr.next

    if times > 1:
        res += prefix+'}\n'
    return res


def code_generation_single_process():
    res = convert_id2str(0, 1, 0, '\t\t')
    return res


def create_non_term(prefix, scaling_factor=1):
    nonterm_h_out = open(prefix+'nonterm.h', 'w')
    nonterm_h_out.write('#include "block.h"\n')
    nonterm_h_out.write('#include "mpi.h"\n')
    nonterm_h_out.write('#include <stdio.h>\n')
    non_term_max = len(global_val.non_terminal_dict)
    for i in range(non_term_max):
        nonterm_h_out.write('void non_term_{}();\n'.format(i))
    nonterm_h_out.close()
    
    nonterm_c_out = open(prefix+'nonterm.c', 'w')
    nonterm_c_out.write('#include "nonterm.h"\n\n')
    nonterm_c_out.write('extern MPI_Status status;\n')
    nonterm_c_out.write('extern MPI_Status wait_status[];\n')
    nonterm_c_out.write('extern MPI_Request wait_requests[];\n')
    nonterm_c_out.write('extern MPI_Request requests[];\n')
    nonterm_c_out.write('extern MPI_Comm comms[];\n')
    nonterm_c_out.write('extern int rank, size;\n')
    nonterm_c_out.write('extern void* buffer;\n')
    nonterm_c_out.write('extern void* sendbuf;\n')
    nonterm_c_out.write('extern void* recvbuf;\n')
    for i in range(non_term_max):
        nonterm_c_out.write('void non_term_{}() {{\n'.format(i))
        # nonterm_c_out.write('\tprintf("%d\\n", rank);\n')
        contents = global_val.non_terminal_dict[str(-i)].split(' ')
        for content in contents:
            sym = int(content.split('^')[0])
            exp = int(content.split('^')[1])
            if sym <= 0:     # 是非终结符
                if exp != 1:
                    nonterm_c_out.write('\tfor (int i = 0; i < {}; i++)\n'.format(exp))
                    nonterm_c_out.write('\t')
                nonterm_c_out.write('\tnon_term_{}();\n'.format(-sym))
            else:           # 终结符
                res = convert_id2str(sym, exp, 1, '\t', scaling_factor)
                nonterm_c_out.write(res)
        nonterm_c_out.write('}\n')


def code_generation(prefix, output_filename, request_num, rank, comm, scaling_factor=1):

    # all_non_term = comm.gather(global_val.call_signature_table, 0)
    size = comm.Get_size()
    
    if rank == 0:
        # print('in code_generation')
        create_non_term(prefix, scaling_factor)

        out = open(output_filename, 'w')
        out.write('#include <stdlib.h>\n')
        out.write('#include <stdio.h>\n')
        out.write('#include <string.h>\n')
        out.write('#include "mpi.h"\n')
        out.write('#include "block.h"\n')
        out.write('#include "time.h"\n')
        out.write('#include "nonterm.h"\n')

        out.write('#define REQUEST_NUM {}\n'.format(request_num))
        out.write('#define COMM_NUM {}\n'.format(global_val.comm_cnt))

        out.write('MPI_Status status;\n')
        out.write('MPI_Status wait_status[REQUEST_NUM];\n')
        out.write('MPI_Request wait_requests[REQUEST_NUM];\n')
        out.write('MPI_Request requests[REQUEST_NUM];\n')
        out.write('MPI_Comm comms[COMM_NUM];\n')
        out.write('int rank, size;\n')
        out.write('void* buffer;\n')
        out.write('void* sendbuf;\n')
        out.write('void* recvbuf;\n')

        out.write('int main(int argc, char** argv) {\n')
        out.write('\tint i = 0;\n')
        out.write('\tdouble startTime, endTime;\n')
        out.write('\tstartTime = MPI_Wtime();\n')
        out.write('\tMPI_Init(&argc, &argv);\n')
        out.write('\tMPI_Comm_size(MPI_COMM_WORLD, &size);\n')
        out.write('\tMPI_Comm_rank(MPI_COMM_WORLD, &rank);\n')
        out.write('\tcomms[0] = MPI_COMM_WORLD;\n')
        
        out.write('\tbuffer=malloc(10000000);\n')
        out.write('\tsendbuf=malloc(10000000);\n')
        out.write('\trecvbuf=malloc(10000000);\n')
        out.write('\tinitial();\n')

    # res = code_generation_single_process()
    # data = comm.gather(res, 0)
        
    if rank == 0:
        main_rule_cnt = 0
        visit_dict = {}
        # print(len(global_val.lcs_main_rules))
        for main_rule in global_val.lcs_main_rules:
            try:
                ranks = parse_ranks(main_rule.first().ranks)
            except Exception as e:
                print(e)
                exit(-1)
            f = False
            for r in ranks:
                if r in visit_dict:
                    f = True
                visit_dict[r] = True
            if f:
                continue
            main_rule_cnt += 1
            out.write('\t')
            out.write(gen_rank_if(ranks))
            ptr = main_rule.first()
            pre = []
            in_seg = False
            while True:
                if ptr.is_guard():
                    break
                if not is_same_list(ptr.ranks, pre):
                    if in_seg:
                        out.write('\t\t}\n')
                    out.write('\t\t')
                    out.write(gen_rank_if(parse_ranks(ptr.ranks)))
                    in_seg = True
                if int(ptr.id) <= 0:
                    if int(ptr.exp) != 1:
                        out.write('\t\t\tfor (int i = 0; i < {}; i++)\n'.format(ptr.exp))
                        out.write('\t')
                    
                    out.write('\t\t\tnon_term_{}();\n'.format(-int(ptr.id)))
                else:
                    out.write(convert_id2str(int(ptr.id), int(ptr.exp), 1, '\t\t\t', scaling_factor))
                pre = ptr.ranks
                ptr = ptr.next
                # if not is_same_list(ptr.ranks, pre):
                #     out.write('\t\t}\n')
                #     pre = ptr.ranks
            out.write('\t\t}\n')        # 因为每个main_rule中的连续重复的最后一定缺一个大括号，最后补上
            out.write('\t}\n')          # 这个大括号的意思是对每个main_rule的总结

        # for i in range(comm.size):
        #     out.write('\tif (rank == {}) {{\n'.format(i))
        #     out.write('\t\tdouble start, end;\n')
        #     out.write('\t\tstart = MPI_Wtime();\n')
        #     out.write('\t\tMPI_Request requests[REQUEST_NUM];\n')
        #     out.write('\t\tMPI_Request wait_requests[REQUEST_NUM];\n')
        #     out.write('\t\tnon_term_{}(rank, comms, requests, wait_requests, status, sendbuf, recvbuf, buffer);\n'.format(-int(global_val.rule_dict[global_val.main_rules[i]].id)))
        #     out.write('\t\tend = MPI_Wtime();\n')
        #     out.write('\t\tdouble duration = (double)(end - start);\n')
        #     out.write('\t\tprintf("rank %d end, using time %f seconds\\n", rank, duration);\n')
        #     out.write('\t}')

        out.write('\tMPI_Finalize();\n')
        # out.write('\tif (rank == 0) {\n\t\tendTime = MPI_Wtime();\n\t\tprintf("Benchmark Runtime = %f\\n", endTime-startTime);\n\t}\n')
        out.write('\tendTime = MPI_Wtime();\n\tprintf("Benchmark Runtime = %f\\n", endTime-startTime);\n')

        out.write('}')

        out.close()

        make = open(prefix+'makefile', 'w')
        make.write('all: block.c block.h code0.c nonterm.c nonterm.h \n')
        make.write('\tmpicc -c nonterm.c -std=c99\n')
        
        make.write('\tmpicc -c block.c -std=c99\n')
        make.write('\tmpicc -o code code0.c block.o nonterm.o -std=c99\n')
        make.write('\n')
        make.write('mpich: block.c block.h code0.c nonterm.c nonterm.h \n')
        make.write('\texport LD_LIBRARY_PATH=/home/cs/sunjw/common/libunwind-1.5.0/lib/:$LD_LIBRARY_PATH\n')
        make.write('\t/home/cs/sunjw/common/mpich3.3/bin/mpicc -c nonterm.c -std=c99\n')
        
        make.write('\t/home/cs/sunjw/common/mpich3.3/bin/mpicc -c block.c -std=c99\n')
        make.write('\t/home/cs/sunjw/common/mpich3.3/bin/mpicc -o code code0.c block.o nonterm.o -std=c99\n')
        make.close()
        print('before lcs, main rule num = {}'.format(size))
        print('after lcs, main rule num = {}'.format(main_rule_cnt))


def print_all_rules():
    non_term_max = len(global_val.non_terminal_dict)
    # print(global_val.unique_dict)
    # print(global_val.non_terminal_dict)


if __name__ == 'main':
    pass
    # def getArgs():
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument('--tracepath', '-t', dest='pathPrefix', default='/home/yantao/run/sequitur/flash_traces_new/', help='trace file path prefix')
    #     parser.add_argument('--nprocs', '-n', dest='nprocs', default=36, help='process number')
    #     parser.add_argument('--output', '-o', dest='outprefix', default='/home/yantao/run/sequitur/', help='output Filename')
    #     args = parser.parse_args() 
    #     return args
    # output_filename = args.outprefix+'code.c'
    # procs = args.nprocs
    # with open(args.pathPrefix+'compressed_trace', "rb") as fin:
    #     gathered_cst = pickle.load(fin)
    #     non_terminal_dict = pickle.load(fin)
    #     computeDict = pickle.load(fin)
    #     requestNum = pickle.load(fin)
    #     # rules_list = pickle.load(fin)
    #     lcs_main_rules = pickle.load(fin)
    #     comm_cnt = pickle.load(fin)
    # code_generation(args.outprefix, output_filename, requestNum, procs)
