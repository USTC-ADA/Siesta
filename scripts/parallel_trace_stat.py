import numpy as np
import pickle
import os
from matplotlib.colors import LogNorm
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
from MPI_define import *
import global_val
from mpi4py import MPI
from statistics import geometric_mean
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

TIME_TRACE_NAME = "/0.trace"

PAPI_MON_EVENTS = "PAPI_LST_INS:PAPI_L2_DCA:PAPI_TOT_INS:PAPI_TOT_CYC:PAPI_BR_CN:PAPI_BR_MSP"
compute_events_list = ["cache_references", "cache_misses", "instructions", "cycles", "branches", "branch_misses"]
num_of_compute_events = 6
parser = argparse.ArgumentParser()
parser.add_argument('--dirname', '-d', dest='dirname', default='MG_C_8/', help='directory name')
args = parser.parse_args()

dirname = args.dirname
dirname = dirname[:-1] if dirname[-1] == '/' else dirname
print(dirname + ' is going to be parsed')


class Status:
    def __init__(self, nprocs):
        self.send_bytes = [0] * nprocs
        self.receive_bytes = [0] * nprocs
        # 目前的六种计算事件
        self.compute_events = [0] * num_of_compute_events
        # self.cache_references = 0
        # self.cache_misses = 0
        # self.instructions = 0
        # self.cycles = 0
        # self.branches = 0
        # self.branch_misses = 0


class TraceStat:
    def __init__(self, nprocs):
        self.nprocs = nprocs
        self.stats = [Status(nprocs) for _ in range(nprocs)]
        # 注意，sendbyte在进行allgather后会发生变化，大小变大
        self.start_time_list = []
        self.recv_buf = []
        self.recv_bytes = []
        # 因为第一个MPI_Init记录的时间戳尚未初始化，所以从第一个MPI事件开始记录
        # 并记录该时间为base值，求之后的时间戳与该时间戳的差值
        # 观察trace发现，第一个事件记录的时间戳依然不准，从第二个时间戳开始记录
        self.count_flag = 0
        self.first_time_record = 0
        global rank

    def parse_trace(self, s):
        if " MPI_Compute" not in s:

            if s[1] == 'MPI_Comm_split':
                trace_comm = s[7]
                pre_comm = s[6]
                if trace_comm not in global_val.comm_map:
                    global_val.comm_map[trace_comm] = {'id': global_val.comm_cnt, 'color': int(s[8]), 'key': int(s[9]),
                                                 'parent': pre_comm}
                    global_val.comm_cnt += 1
            elif s[1] == 'MPI_Comm_dup':
                pre_comm = s[6]
                trace_comm = s[7]
                if trace_comm not in global_val.comm_map:
                    global_val.comm_map[trace_comm] = {'id': global_val.comm_cnt, 'parent': pre_comm}
                    global_val.comm_cnt += 1
            elif s[1] == 'MPI_Cart_create':
                pre_comm = s[6]
                trace_comm = s[7]
                if trace_comm not in global_val.comm_map:
                    global_val.comm_map[trace_comm] = {'id': global_val.comm_cnt, 'parent': pre_comm}
                    global_val.comm_cnt += 1
            elif s[1] == 'MPI_Comm_create':
                pass
            if len(s) > 6 and s[1] != 'MPI_Comm_free':
                trace_comm = s[6]
                if trace_comm not in global_val.comm_map:
                    global_val.comm_map[trace_comm] = {'id': 0, 'parent': None}
            elif s[1] == 'MPI_Comm_free':
                # MPI_Comm_free理论上来参数里的MPI_Comm一定会在前面出现，在这里只需要记录前面已经出现过的MPI_Comm就可以了
                trace_comm = s[6]
                if trace_comm not in global_val.comm_map:
                    global_val.comm_map[trace_comm] = {'id': global_val.comm_cnt, 'parent': 0}
                    global_val.comm_cnt += 1

            event_line = s.split(',')
            my_rank = int(event_line[0])
            function = event_line[1]
            data_group = event_line[2]
            data_group = data_group.split(';')
            count = data_group[0]
            data_type = data_group[1]
            target = int(data_group[2])

            # 对于MPI_Init记录的第一个尚未初始化时间戳时候的负数数据舍去
            if self.count_flag == 2:
                self.first_time_record = int(event_line[3])
                self.start_time_list.append(0)
            elif self.count_flag > 2:
                start_time = int(event_line[3]) - self.first_time_record
                self.start_time_list.append(start_time)
            self.count_flag += 1

            if function in send_list:
                n_bytes = int(count) * int(data_type)
                self.stats[my_rank].send_bytes[target] += n_bytes
            elif function in recv_list:
                n_bytes = int(count) * int(data_type)
                self.stats[target].receive_bytes[my_rank] += n_bytes
            else:
                # TODO 对于其他MPI通信事件的信息统计（如果占比很小可能不需要做）
                pass
        else:
            event_line = s.split(',')
            my_rank = int(event_line[0])
            event = event_line[1]
            compute_data = event_line[2]
            compute_data = compute_data.split(';')
            # 目前考虑的计算事件为6种方式，可以考虑从环境变量中读取不同事件
            for i in range(num_of_compute_events):
                self.stats[my_rank].compute_events[i] += int(compute_data[i])

    def one_record_time(self, s):
        # 在并行化的实现中，每个rank只会遍历自己进程号的trace
        # 合并到parse trace过程中，没有必要遍历两遍trace文件
        # 如果想要输出trace的时间图像，可以直接修改对应的rank
        if " MPI_Compute" not in s:
            event_line = s.split(',')
            start_time = int(event_line[3]) if int(event_line[3]) > 0 else 0
            self.start_time_list.append(start_time)
            end_time = int(event_line[4]) if int(event_line[4]) > 0 else 0

    def print_status(self, filename):
        self.recv_buf = comm.gather(self.stats[rank].compute_events, 0)
        # 注意，每个进程只发送stat中自己读的trace，接收list中为顺序的计算事件数据，将结果依次输出
        if rank == 0:
            with open(filename, 'w') as fo:
                for i in range(len(self.recv_buf)):
                    fo.write("process:" + str(i) + ":\n")
                    print("process " + str(i) + " : ")
                    for j in range(num_of_compute_events):
                        fo.write(compute_events_list[j] + ":" + str(self.recv_buf[i][j]) + "\n")
                        print(compute_events_list[j] + " : " + str(self.recv_buf[i][j]))

    def visualize_comm_patterns(self, filename):
        self.recv_bytes = comm.gather(self.stats[rank].send_bytes, 0)
        # 收集所有进程，自身send的字节数，构成matrix
        if rank == 0:
            matrix = np.array(self.recv_bytes)  # np.maximum(matrix_send, matrix_recv) * self.scale_factor
            plt.figure(figsize=(8, 6))
            max_num = matrix.max()
            if max_num < 10000:
                sns.heatmap(matrix, cmap="binary", linecolor='Black')
            else:
                sns.heatmap(matrix, cmap="binary", linecolor='Black', norm=LogNorm(vmin=1000))
            plt.xlabel("Sender Rank")
            plt.ylabel("Receiver Rank")
            plt.ylim(0, self.nprocs)
            plt.xlim(0, self.nprocs)
            # plt.show()
            plt.savefig(filename + '.png', format='png')

    @staticmethod
    def transpose(matrix):
        new_matrix = []
        for i in range(len(matrix[0])):
            matrix1 = []
            for j in range(len(matrix)):
                matrix1.append(matrix[j][i])
            new_matrix.append(matrix1)
        return new_matrix

    def compute_matrix(self):
        matrix = comm.allgather(self.stats[rank].compute_events)
        # 通过MPI通信实现下面的过程，allgather让每个进程都有一份matrix副本
        # for i in range(self.nprocs):
        #     matrix.append(self.stats[i].compute_events)
        matrix = self.transpose(matrix)
        # for line in matrix:
        #     print(line)
        return matrix


def file2list(filename, nprocs):
    compute_data = [[] for _ in range(nprocs)]
    rank = 0
    with open(filename) as fin:
        for line in fin:
            if "process" in line:
                line = line.strip()
                line = line.split(':')
                # print(line)
                if line[1] != "":
                    rank = int(line[1])
                    # print(rank)
            else:
                line = line.strip()
                line = line.split(':')
                # print(line)
                if line[1] != "":
                    compute_data[rank].append(int(line[1]))
    # print(compute_data)
    return compute_data


def draw_ori_pred_bar(ori_file, pred_file, nprocs):
    ori_data = file2list(ori_file, nprocs)
    pred_data = file2list(pred_file, nprocs)
    dir_name = pred_file + '-figures'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    for rank in range(nprocs):
        pred_l = pred_data[rank]
        actual_l = ori_data[rank]
        title = "process " + str(rank)
        # 求预测值与实际值的百分比，因为不同事件的数目差别很大
        for i in range(num_of_compute_events):
            pred_l[i] = pred_l[i] / actual_l[i]
            actual_l[i] = actual_l[i] / actual_l[i]
        final_list = []
        for i in range(num_of_compute_events):
            final_list.append(pred_l[i])
            final_list.append(actual_l[i])
        bar_width = 0.3
        x_list = []
        for i in range(1, num_of_compute_events + 1):
            x_list.append(i)
            x_list.append(i + bar_width + 0.05)
        x = np.array(x_list)
        tick_label = []
        for i in range(num_of_compute_events):
            tick_label.append('Predicted')
            tick_label.append('Actual')
        label = 'Count'

        plt.rcParams.update({'figure.autolayout': True})

        plt.figure()
        ax = plt.subplot()
        plt.bar(x=x, height=final_list, width=bar_width, label=label, color='0.3', tick_label=tick_label)
        ax.set_ylabel('Compute events count Percentage(100%)')
        ax.set_title(title)
        plt.legend()
        # plt.xticks(x, tick_label)
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=45, horizontalalignment='right')
        ax.set_xlabel("compute events")
        # plt.show()
        plt.savefig(dir_name + '/' + title + '.png', format='png')


def make_sub(ax, painting_matrix, title):
    # m应该为6，代表6个指标，n应该为进程数，即num procs
    m = len(painting_matrix)
    n = len(painting_matrix[0])
    x = np.array(range(len(compute_events_list)))
    x = x + 0.5
    y_labels = ['LST', 'L1_DCM', 'INS', 'CYC', 'CN', 'MSP']
    # sns.heatmap(matrix, cmap="binary", linecolor='Black', norm=LogNorm(vmin=1000))
    sns.heatmap(painting_matrix, cmap="binary", linecolor='Black', vmin=0, vmax=1)
    # sns.heatmap(painting_matrix, cmap="RdBu_r", linecolor='Black')
    sns.despine(top=False, right=False, left=False, bottom=False)
    ax.set_xlabel("process id")
    ax.set_ylabel("performance event")
    ax.set_title(title)
    ax.set_yticks(x)
    ax.set_yticklabels(labels=y_labels, rotation=360)
    ax.set_ylim(0, m)
    ax.set_xlim(0, n)


def draw_heatmap(ori_matrix, pre_matrix, filename, title):
    ori_matrix = np.array(ori_matrix)
    pre_matrix = np.array(pre_matrix)
    painting_matrix = np.absolute(ori_matrix - pre_matrix)
    # print(painting_matrix)
    painting_matrix = painting_matrix / ori_matrix
    # print(painting_matrix)
    line_mean = [np.mean(line) for line in painting_matrix]
    # print(line_mean)
    similarity = np.mean(line_mean)
    # print(similarity)
    plt.figure(figsize=(10, 7))
    ax = plt.subplot()
    make_sub(ax, painting_matrix, title)
    # plt.show()
    plt.savefig(filename + '.png', format='png')
    return similarity


def draw_linechart(x, name, bench_start_time_list, real_start_time_list):
    plt.figure(dpi=400)

    l1 = plt.plot(x, bench_start_time_list, 'r--', label='benchmark')
    l2 = plt.plot(x, real_start_time_list, 'g--', label='real')
    plt.plot(x, bench_start_time_list, 'r-', x, real_start_time_list, 'g-')

    plt.xlabel('MPI calls')
    plt.ylabel('time')

    plt.legend()
    plt.savefig(name + '_time.png', format='png')


def read_from_packages(dir_name):
    global rank
    nprocs = int(dir_name.split('_')[-1])
    ts = TraceStat(nprocs)
    title = " ".join(dir_name.split('_'))
    filename = dir_name + "/" + str(rank) + ".trace"
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.strip()
            ts.parse_trace(line)

    comm.barrier()

    ts.print_status(dir_name + "/" + dir_name + "-compute_res")
    ts.visualize_comm_patterns(dir_name + "/origin")
    ori_compute_matrix = ts.compute_matrix()

    ts2 = TraceStat(nprocs)
    dir_name2 = dir_name + "/benchmark"
    filename2 = dir_name2 + "/" + str(rank) + ".trace"
    with open(filename2, 'r') as fin:
        for line in fin:
            line = line.strip()
            ts2.parse_trace(line)

    comm.barrier()

    ts2.print_status(dir_name + "/" + dir_name + "benchmark-compute_res")
    ts2.visualize_comm_patterns(dir_name + "/benchmark")
    pred_compute_matrix = ts2.compute_matrix()

    if rank == 0:
        similarity = draw_heatmap(ori_compute_matrix, pred_compute_matrix, dir_name + "/similarity", title)
        print(similarity)

    if rank == 0:
        # 这里可以根据rank来指定输出哪一个trace的时间图
        length = len(ts.start_time_list)
        x = range(length)
        draw_linechart(x, dir_name + "/" + dir_name + "benchmark", ts2.start_time_list, ts.start_time_list)
    # 因为进程数目的限制，不再print每个进程的linechart，如有需要直接在compute res文件中查看结果
    # draw_ori_pred_bar(dir_name + "/" + dir_name + "-compute_res", dir_name + "/" + dir_name + "benchmark-compute_res",
    #                   nprocs)


def read_from_packages_ada(dir_name):
    global rank
    nprocs = int(dir_name.split('_')[-1])
    ts = TraceStat(nprocs)
    title = " ".join(dir_name.split('_'))
    filename = dir_name + "/" + str(rank) + ".trace"
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.strip()
            ts.parse_trace(line)

    comm.barrier()

    ts.print_status(dir_name + "/" + dir_name + "-compute_res")
    ts.visualize_comm_patterns(dir_name + "/origin")
    ori_compute_matrix = ts.compute_matrix()

    ts2 = TraceStat(nprocs)
    dir_name2 = dir_name + "/ada"
    filename2 = dir_name2 + "/" + str(rank) + ".trace"
    with open(filename2, 'r') as fin:
        for line in fin:
            line = line.strip()
            ts2.parse_trace(line)

    comm.barrier()

    ts2.print_status(dir_name + "/" + dir_name + "ada-compute_res")
    ts2.visualize_comm_patterns(dir_name + "/ada")
    pred_compute_matrix = ts2.compute_matrix()

    if rank == 0:
        similarity = draw_heatmap(ori_compute_matrix, pred_compute_matrix, dir_name + "/ada_similarity", title)
        print(similarity)

    if rank == 0:
        # 这里可以根据rank来指定输出哪一个trace的时间图
        length = len(ts.start_time_list)
        x = range(length)
        draw_linechart(x, dir_name + "/" + dir_name + "ada", ts2.start_time_list, ts.start_time_list)
    # 因为进程数目的限制，不再print每个进程的linechart，如有需要直接在compute res文件中查看结果
    # draw_ori_pred_bar(dir_name + "/" + dir_name + "-compute_res", dir_name + "/" + dir_name + "benchmark-compute_res",
    #                   nprocs)


if __name__ == "__main__":
    if os.path.exists(dirname + "/benchmark"):
        read_from_packages(dirname)
    if os.path.exists(dirname + "/ada"):
        read_from_packages_ada(dirname)
