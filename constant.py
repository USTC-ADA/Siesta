'''
    假定所有trace file的名称是${rank}.trace_*
'''
TWO_EVENTS_TRACE_SUFFIX = ".trace_2"
FOUR_EVENTS_TRACE_SUFFIX = ".trace_4"
TRACE_SUFFIX = ".trace"

THRESHOLD = 0.05
CYC_THRESHOLD = 0.07
SIMILARITY = 0.05
CYC_SIMILARITY = 0.1
ABSOLUTE_DELTA = 10000
PERFORMANCE_DIM = 6

SMALL_CODE_BLOCK_STANDARD = [1000, 1000, 5000, 10000, 5000, 5000]

SIMILARITY_INTER_PROCESS = 0.1
CYC_SIMILARITY_INTER_PROCESS = 0.3

TWO_COMM_LIST = ['MPI_Comm_split', 'MPI_Comm_dup', 'MPI_Cart_create']

USE_REQUEST_LIST = [
    'MPI_Isend',
    'MPI_Irecv',
    'MPI_Ibcast',
    'MPI_Ireduce'
]

FREE_REQUEST_LIST = [
    'MPI_Wait',
    'MPI_Waitall',
    'MPI_Waitsome',
    'MPI_Waitany'
]

TAG_FUNC_LIST = [
    'MPI_Send',
    'MPI_Recv',
    'MPI_Isend',
    'MPI_Irecv',
    'MPI_Ssend',
    'MPI_Issend',
    'MPI_Irsend'
]

SEND_RECV_LIST = [
    'MPI_Sendrecv',
    'MPI_Sendrecv_replace'
]

SMALL_BLOCK_CYC = 10000


collectiveList = [
    "MPI_Allgather",
    "MPI_Allgatherv",
    "MPI_Allreduce",
    "MPI_Alltoall",
    "MPI_Alltoallv",
    "MPI_Barrier",
    "MPI_Bcast",
    "MPI_Gather",
    "MPI_Gatherv",
    "MPI_Iallgather",
    "MPI_Iallgatherv",
    "MPI_Iallreduce",
    "MPI_Ialltoall",
    "MPI_Ialltoallv",
    "MPI_Ialltoallw",
    "MPI_Ibcast",
    "MPI_Ibarrier",
    "MPI_Iexscan",
    "MPI_Igather",
    "MPI_Igatherv",
    "MPI_Ireduce",
    "MPI_Ireduce_scatter_block",
    "MPI_Ireduce_scatter",
    "MPI_Iscan",
    "MPI_Iscatter",
    "MPI_Iscatterv",
    "MPI_Reduce",
    "MPI_Reduce_scatter",
    "MPI_Scatter",
    "MPI_Scatterv",
    "MPI_Wait",
    "MPI_Waitall",
    "MPI_Init"
]

COLLECTIVE_LIST = [
    "MPI_Allgather",
    "MPI_Allgatherv",
    "MPI_Allreduce",
    "MPI_Alltoall",
    "MPI_Alltoallv",
    "MPI_Barrier",
    "MPI_Bcast",
    "MPI_Gather",
    "MPI_Gatherv",
    "MPI_Iallgather",
    "MPI_Iallgatherv",
    "MPI_Iallreduce",
    "MPI_Ialltoall",
    "MPI_Ialltoallv",
    "MPI_Ialltoallw",
    "MPI_Ibcast",
    "MPI_Ibarrier",
    "MPI_Iexscan",
    "MPI_Igather",
    "MPI_Igatherv",
    "MPI_Ireduce",
    "MPI_Ireduce_scatter_block",
    "MPI_Ireduce_scatter",
    "MPI_Iscan",
    "MPI_Iscatter",
    "MPI_Iscatterv",
    "MPI_Reduce",
    "MPI_Reduce_scatter",
    "MPI_Scatter",
    "MPI_Scatterv",
    "MPI_Wait",
    "MPI_Waitall",
    "MPI_Init"
]



# incomplete
pt2ptList = [
    "MPI_Bsend",
    "MPI_Ibsend",
    "MPI_Irsend",
    "MPI_Isend",
    "MPI_Issend",
    "MPI_Rsend",
    "MPI_Send",
    "MPI_Sendrecv",
    "MPI_Sendrecv_replace",
    "MPI_Ssend",
    "MPI_Recv",
    "MPI_Irecv"
]

send_list = [
    "MPI_Send",
    "MPI_Isend"
]

recv_list = [
    "MPI_Recv",
    "MPI_Irecv"
]

function_para_dict = {
    'MPI_Reduce' : ['file', 'function', 'count', 'datatype',  'root', 'Blank'],
    'MPI_Allreduce' : ['file', 'function', 'count', 'datatype', 'Blank'],
    # 'MPI_Sendrecv': ['file', 'function', 'source', 'dest', 'count', 'datatype', 'Blank'],
    'MPI_Send':['file', 'function', 'dest', 'count', 'datatype', 'Blank'],
    'MPI_Barrier' : ['file', 'function', 'Blank'],
    'MPI_Bcast' : ['file', 'function','count','datatype','root', 'Blank'],
}

event_para_dict = {
    'file': 0,
    'function': 1,
    'count': 2,
    'datatype': 3,
    'target': 4,
    'tag':5,
    'D':6,
    'Blank': 7
}

# event_para_dict = {
#     'file': 0,
#     'function': 1,
#     'incount': 2,
#     'count': 3,
#     'datatype': 4,
#     'source': 5,
#     'dest': 6,
#     'request': 7,
#     'sendcount': 8,
#     'sendcnt': 9,
#     'sendcnts': 10,
#     'sendtype': 11,
#     'recvcount': 12,
#     'recvcnt': 13,
#     'recvcnts': 14,
#     'recvtype': 15,
#     'op': 16,
#     'root': 17,
#     'S': 18,
#     'E': 19,
#     'D': 20,
#     'Blank': 21}

