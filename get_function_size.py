import osubench
import os

# args = osubench.get_args()
# o_dir = args.osu_dir
o_dir = '/gpfs/home/cs/sunjw/addition/run/osutest'
cur_dir = '/home/cs/sunjw/addition/run/sequitur-main/src'

data = {}

# incomplete
sendList = [
    "MPI_Bsend",
    "MPI_Rsend",
    "MPI_Send",
    "MPI_Sendrecv",
    "MPI_Sendrecv_replace",
    "MPI_Ssend",
    "MPI_Recv",
]

osu_dict = {
    "osu_allgather": "MPI_Allgather",
    "osu_allgatherv": "MPI_Allgatherv",
    "osu_allreduce": "MPI_Allreduce",
    "osu_alltoall": "MPI_Alltoall",
    "osu_alltoallv": "MPI_Alltoallv",
    "osu_barrier": "MPI_Barrier",
    "osu_bcast": "MPI_Bcast",
    "osu_gather": "MPI_Gather",
    "osu_gatherv": "MPI_Gatherv",
    "osu_reduce": "MPI_Reduce",
    "osu_multi_lat": "MPI_Send",
    "osu_scatter": "MPI_Scatter",
    "osu_scatterv": "MPI_Scatterv",
    "osu_latency": "osu_latency",
    "osu_reduce_scatter": "osu_reduce_scatter"
}


# binary search find left boundary
def find_index(arr, target):
    left = 0
    right = len(arr) - 1
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left


def get_data(n_procs):
    if n_procs in data:
        return
    else:
        print("get data from minibench")
        data[n_procs] = {}
    dir_path = cur_dir + '/' + 'osu_bench' + '_' + str(n_procs)
    if not os.path.exists(dir_path):
        osubench.collect_run_time(n_procs, o_dir, cur_dir)
    for name in os.listdir(dir_path):
        if name == 'osu_barrier.log' or '.pdf' in name or '.png' in name or '.err' in name:
            continue
        if os.path.isfile(os.path.join(dir_path, name)):
            title = osu_dict[name.split('.')[0]]
            x, y = [], []
            with open(os.path.join(dir_path, name), 'r') as f:
                print('get data from ' + name)
                for line in f:
                    line = line.strip()
                    if line == "" or '#' in line:
                        continue
                    else:
                        line = line.split()
                        x.append(int(line[0]))
                        y.append(float(line[1]))
            temp = [x, y]
            data[n_procs][title] = temp

def get_func_size(func_name, size, proc_number, scale=10):
    # 规模较小时看不出时间差异
    if size < 100:
        return size//scale + 1

    if proc_number <= 16:
        n_procs = 16
    elif proc_number <= 64:
        n_procs = 64
    elif proc_number <= 128:
        n_procs = 128
    elif proc_number <= 256:
        n_procs = 256
    elif proc_number <= 529:
        n_procs = 512
    else:
        n_procs = 1024
    
    get_data(n_procs)
    
    if func_name in sendList:
        func_name = 'MPI_Send'
    if func_name not in data[n_procs]:
        print('function name not found')
        return size//scale + 1
    else:
        x, y = data[n_procs][func_name]
        if len(x) == 0:
            print('check minibench')
            return size//scale + 1
        x_index = find_index(x, size)
        if x_index < len(x) - 1:
            if size > (x[x_index] + x[x_index + 1]) / 2:
                x_index = x_index + 1
        time_in_dict = y[x_index]
        time_to_find = time_in_dict / scale
        size_index = len(y)
        for i in range(len(y)):
            if y[i] < time_to_find:
                size_index = i
            else:
                break
        if size_index == len(y):
            print('time is too small')
            return size//scale + 1
        else:
            return int(x[size_index])


if __name__ == '__main__':
    print(get_func_size('MPI_Send', 100000, 16))
