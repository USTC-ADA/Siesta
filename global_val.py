
digrams_hashtable = {}
number_of_rules = 0
call_signature_table = {}
id_signature_table = {}
cst_num = 1
rules_list = []
main_rule = None

comm_map = {}   # {comm_id: {color: {rank: val}, key: {rank: val}, parent: comm_id}} 只有在comm_split才会记录
comm_cnt = 1    # 一定有一个MPI_COMM_WORLD

truncateDict = {}
redirect = {}
bucket = {}
requestDict = {}
requestUsed = []
requestUsedMap = {}
performanceDict = {}
computeDict = {}
compute_cnt = 0

small_block_cnt = 0

rank = 0
size = 0

main_rules = None           # main_rules = [rank0's rule 0, rank1's rule 0…]
unique_dict = None          # unique_dict = {non_terminal_real_content: non_terminal_id}
non_terminal_dict = None    # non_terminal_dict = {non_terminal_id: non_terminal_real_content}
rule_dict = None            # 具体的rule结构体
gathered_cst = None         # 所有终结符的表

lcs_main_rules = []         # lcs压缩后的main_rule的list
ranks_dict = {}             # rank set的hash表
small_block_list = []       # 小代码块的列表

perf_sum = [0, 0, 0, 0, 0, 0]               # 原trace的六个纬度的和，长度为6的数组
