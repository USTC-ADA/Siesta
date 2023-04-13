import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

# The OSU Micro Benchmarks (OMB) are a widely used suite of benchmarks for measuring and evaluating
# the performance of MPI operations for point-to-point, multi-pair, and collective communications.
# These benchmarks are often used for comparing different MPI implementations and the underlying
# network interconnect.

pt2pt_list = [
    'osu_latency',  # - Latency Test
    'osu_multi_lat'  # - Multi-pair Latency Test
]

bandwith_list = [
    'osu_bw',  # - Bandwidth Test
    'osu_bibw'  # - Bidirectional Bandwidth Test
]

collective_list = [
    'osu_allgather',  # - MPI_Allgather Latency Test(*)
    'osu_allgatherv',  # - MPI_Allgatherv Latency Test
    'osu_allreduce',  # - MPI_Allreduce Latency Test
    'osu_alltoall',  # - MPI_Alltoall Latency Test
    'osu_alltoallv',  # - MPI_Alltoallv Latency Test
    'osu_barrier',  # - MPI_Barrier Latency Test
    'osu_bcast',  # - MPI_Bcast Latency Test
    'osu_gather',  # - MPI_Gather Latency Test(*)
    'osu_gatherv',  # - MPI_Gatherv Latency Test
    'osu_reduce',  # - MPI_Reduce Latency Test
    'osu_reduce_scatter',  # - MPI_Reduce_scatter Latency Test
    'osu_scatter',  # - MPI_Scatter Latency Test(*)
    'osu_scatterv',  # - MPI_Scatterv Latency Test
]


# def get_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--nprocs', '-n', dest='nprocs', default=16, help='process number')
#     parser.add_argument('--osubenchmark', '-b', dest='osu_dir', default='/gpfs/home/cs/sunjw/addition/run/osutest', help='benchmark dir')
#     args = parser.parse_args()
#     return args


def run_osu_bench(name, n_procs, osu_dir):
    sub_dir = ''
    if name == 'osu_latency' or name == 'osu_bibw' or name == 'osu_bw':
        n_procs = 2
    if name in pt2pt_list:
        sub_dir = '/pt2pt/'
    elif name in collective_list:
        sub_dir = '/collective/'
    else:
        print('error! wrong name {}'.format(name))
    output = ') 1> ' + name + '.log 2> ' + name + '.err'
    # parameters = '--mca btl self,vader'
    parameters = ''
    cmd = '(mpirun' + parameters + ' -np ' + str(n_procs) + ' ' + osu_dir + sub_dir + name + output
    os.system(cmd)


def make_sub(ax, data, title):
    # ax.set_yscale('log')
    plt.plot(data[0], data[1], c='black')
    ax.set_ylabel('Latency (us)')
    ax.set_xlabel('Size')
    ax.set_title(title)
    # ax.set_xticks(x)
    # ax.set_xticklabels(labels)
    # ax.legend(loc='upper left')


def make_multi_sub(ax, data, index, title):
    legends = ['64', '128', '256', '512']
    plt.plot(data[0][index][0], data[0][index][1], label=legends[0])
    plt.plot(data[1][index][0], data[1][index][1], label=legends[1])
    plt.plot(data[2][index][0], data[2][index][1], label=legends[2])
    plt.plot(data[3][index][0], data[3][index][1], label=legends[3])
    ax.set_ylabel('Latency (us)')
    ax.set_xlabel('Size')
    ax.legend(loc='upper left')
    ax.set_title(title)


def visualize(dir_path):
    data = []
    titles = []
    for name in os.listdir(dir_path):
        if name == 'osu_barrier.log' or '.pdf' in name or '.png' in name or '.err' in name:
            continue
        if os.path.isfile(os.path.join(dir_path, name)):
            titles.append(name.split('.')[0])
            x, y = [], []
            with open(os.path.join(dir_path, name), 'r') as f:
                print(name)
                for line in f:
                    line = line.strip()
                    if line == "" or '#' in line:
                        continue
                    else:
                        line = line.split()
                        x.append(int(line[0]))
                        y.append(float(line[1]))
            temp = [x, y]
            data.append(temp)
    n = len(data)
    fig = plt.figure(figsize=(20, 16), constrained_layout=True)
    for i in range(1, n + 1):
        ax = fig.add_subplot(4, 4, i)
        make_sub(ax, data[i - 1], titles[i - 1])
    plt.savefig('line_chart' + '.pdf', format='pdf')
    plt.savefig('line_chart' + '.png', format='png')


def multi_visualization():
    multi_data = []
    titles = []
    cwd = os.getcwd()
    scales = ['64', '128', '256', '512']
    for scale in scales:
        name_list = []
        data = []
        dir_path = cwd + '/' + 'osu_bench' + '_' + scale
        if not os.path.exists(dir_path):
            print('some error in data, %s not found' % dir_path)
        else:
            os.chdir(dir_path)
        for name in os.listdir(dir_path):
            if '.pdf' in name or 'png' in name or '.err' in name:
                continue
            func = name.split('.')[0]
            if func not in collective_list and func not in pt2pt_list:
                continue
            name_list.append(name)
        name_list.sort()
        for name in name_list:
            print(name)
            if os.path.isfile(os.path.join(dir_path, name)):
                titles.append(name.split('.')[0])
                x, y = [], []
                with open(os.path.join(dir_path, name), 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line == "" or '#' in line:
                            continue
                        else:
                            line = line.split()
                            if int(line[0]) > 1000000:
                                continue
                            x.append(int(line[0]))
                            y.append(float(line[1]))
                temp = [x, y]
                data.append(temp)
        multi_data.append(data)
    fig = plt.figure(figsize=(20, 16), constrained_layout=True)
    n = len(multi_data[0])
    print(n, len(multi_data))
    # print(multi_data)
    for i in range(1, n + 1):
        ax = fig.add_subplot(4, 4, i)
        make_multi_sub(ax, multi_data, i - 1, titles[i - 1])
    plt.savefig('multi_line_chart' + '.pdf', format='pdf')
    plt.savefig('multi_line_chart' + '.png', format='png')


def collect_run_time(n_procs, osu_dir, cur_dir):
    dir_path = cur_dir + '/' + 'osu_bench' + '_' + str(n_procs)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    os.chdir(dir_path)
    for name in pt2pt_list:
        run_osu_bench(name, n_procs, osu_dir)
    for name in collective_list:
        run_osu_bench(name, n_procs, osu_dir)
    visualize(dir_path)


if __name__ == '__main__':
    # args = get_args()
    # n_procs = args.nprocs
    # osu_dir = args.osu_dir
    n_procs = 512
    osu_dir = '/gpfs/home/cs/sunjw/addition/run/osutest'
    cur_dir = '/home/cs/sunjw/addition/run/sequitur-main/src'
    collect_run_time(n_procs, osu_dir, cur_dir)
