
from constant import TWO_COMM_LIST, TAG_FUNC_LIST, SEND_RECV_LIST, collectiveList, PERFORMANCE_DIM, SMALL_CODE_BLOCK_STANDARD
from with_compute import *
from mpi4py import MPI
import global_val


class FixedWorkload:
    def __init__(self):
        pass


def is_small_block(value):
    # value是一个大小为performance_dim的数组，当是小代码块的时候返回true，否则返回false
    try:
        for i in range(PERFORMANCE_DIM):
            if value[i] > SMALL_CODE_BLOCK_STANDARD[i]:
                return False
        return True
    except Exception as e:
        print(e)
        # 如果出了什么错，就默认不是小代码块
        return False


def is_terminal_exist(symbol):
    # 判断一个symbol是够已经在 cst 里
    return symbol in global_val.call_signature_table.keys()


def get_symbol_index(symbol):
    # 返回cst中symbol的id，如果不存在该symbol，返回-1
    try:
        return global_val.call_signature_table[symbol]
    except Exception as e:
        return -1


def add_symbol2cst(symbol):
    # 把symbol加入到cst当中，如果cst已经有了，那就不做处理
    # 返回cst中这个symbol的编号
    if not is_terminal_exist(symbol):
        global_val.call_signature_table[symbol] = global_val.cst_num
        ans = get_symbol_index(symbol)
        global_val.cst_num += 1
        return ans
    else:
        return get_symbol_index(symbol)


def construct_key_from_mpi_event(mpi_event):
    key = ''
    events = mpi_event.split(',')
    function = events[1]
    key += function
    key += ';'

    if function in collectiveList:
        key += events[2]
    else:
        rank = int(events[0])
        para = events[2].split(';')
        target = int(para[2])
        target = rank - target
        para[2] = str(target)
        key += ";".join(para)
        
    key += ';'
    if events[1] == 'MPI_Waitall' or events[1] == 'MPI_Wait':
        requests = events[5].split(':')
        requests = requests[:len(requests)-1]
        length = len(requests)
        for i in range(length):
            if requests[i] not in global_val.requestUsedMap:
                pass
            else:
                id = global_val.requestUsedMap.pop(requests[i])
                global_val.requestUsed[int(id)] = False
                key += id
                key += ':'
    else:
        # 最多只需要一个request并且是使用request
        request = events[5].split(':')[0]
        if int(request) == -1:
            key += '-1:'
        else:
            available_request_id = str(find_avaliable_request())
            key += available_request_id
            global_val.requestUsedMap[request] = available_request_id
            key += ':'

    key += ';'
    if len(events) > 6:
        key += str(global_val.comm_map[events[6]]['id'])    # comm  存在部分函数调用没有comm这个结构体

    if events[1] in SEND_RECV_LIST:
        key += ';'
        rank = int(events[0])
        tgt = int(events[7])
        key += str(rank-tgt)
        key += ';'
        key += events[8]
        key += ';'
        key += events[9]
        
    if events[1] in TWO_COMM_LIST:
        key += ';'
        key += str(global_val.comm_map[events[7]]['id'])
    if events[1] == 'MPI_Cart_create':
        key += ';'
        key += events[8]
        key += ';'
        key += events[9]
        key += ';'
        key += events[10]
        key += ';'
        key += events[11]
    if events[1] == 'MPI_Comm_split':
        key += ';'
        key += events[8]    # color
        key += ';'
        key += events[9]    # key
    if events[1] in TAG_FUNC_LIST:
        key += ';'
        key += events[7]
    return key


# 返回一个数组，长度为3，含有的值分别为LST、INS、BR_CN
def constrcut_variance_key_from_compute_event(compute_event):
    line = compute_event.strip()
    s = line.split(',')[2]
    s = s.split(';')[:6]
    # 6个值分别为LST、L2_DCA、INS、CYC、BR_CN、BR_MSP
    # 不变的是 LST、INS、BR_CN
    lst = int(s[0])
    ins = int(s[2])
    br_cn = int(s[4])
    return [lst, ins, br_cn]


def construct_key_from_compute_event(compute_event):
    line = compute_event.strip()
    s = line.split(',')[2]
    s = s.split(';')[:6]
    values = [int(val) for val in s]
    afterHandle = dataHandler(values)
    if is_small_block(afterHandle):
        return None
    index_1 = global_val.truncateDict[afterHandle]
    index_2 = global_val.redirect[index_1]
    key = index_2
    return key


def create_signature_from_event(line: str):
    line = line.strip()
    # 对于MPI通信事件，丢弃最后两位时间数据，把其他的部分作为key值
    if ' MPI_Compute' not in line:
        key = construct_key_from_mpi_event(line)
    else:
        key = construct_key_from_compute_event(line)
    if key != None:
        symbol_id = add_symbol2cst(key)
    else:
        symbol_id = None
    return symbol_id, key


# 表示一个规则，guard作为哨兵
class Rule:
    def __init__(self, rule_num):
        self.id = rule_num
        self.guard = Guard(self)
        self.count = 0
        self.index = 0

    def first(self):
        return self.guard.next

    def last(self):
        return self.guard.prev


# 用于合并左右两个symbol，删除左边symbol可能拥有的digram
def join(left, right):
    if left.next is not None:
        left.delete_digram()
    left.next = right
    right.prev = left


# 符号基类，定义了基本的方法
class Symbol:
    def __init__(self):
        self.id = 0
        self.exp = 1
        self.rule = None
        self.prev = None
        self.next = None

    def is_guard(self):
        return False

    def is_non_terminal(self):
        return False

    # 查找当前symbol构建的key是否在表中，如果不为当前symbol构建的，那么就发现了重复项，查找不到返回None
    def get_digram(self):
        if self.next is not None:
            index = str(self.id) + '^' + str(self.exp) + '&' + str(self.next.id) + '^' + str(self.next.exp)
            if index in global_val.digrams_hashtable:
                return global_val.digrams_hashtable[index]
            else:
                return None

    # 仅当从digram中查找到的key值对应的表项与当前symbol相等时，才会去删除这一项
    def delete_digram(self):
        if self.next is not None:
            if self.is_guard() or self.next.is_guard():
                return
            index = str(self.id) + '^' + str(self.exp) + '&' + str(self.next.id) + '^' + str(self.next.exp)
            if index in global_val.digrams_hashtable:
                if global_val.digrams_hashtable[index] == self:
                    del global_val.digrams_hashtable[index]

    # 如果表中没有这一项，就构建key值并将symbol插入到哈希表
    def put_digram(self):
        if self.next is not None:
            index = str(self.id) + '^' + str(self.exp) + '&' + str(self.next.id) + '^' + str(self.next.exp)
            if index not in global_val.digrams_hashtable:
                global_val.digrams_hashtable[index] = self

    # 连接 this = symbol 与 symbol = this.next，删除this与this.next构建的digram
    def insert_after(self, symbol):
        join(symbol, self.next)
        join(self, symbol)

    # 将一个digram用非终结符替代
    def substitute(self, rule):
        prev = self.prev
        self.next.clean_up()
        self.clean_up()
        # del prev.next
        # del prev.next
        prev.insert_after(NonTerminal(rule, 1))
        if not prev.check():
            prev.next.check()

    # 如果遇到即将插入digram table的项已存在于哈希表的处理方法
    def process_match(self, match):
        # checked = self.get_digram()

        if (match.prev.is_guard() and match.next.next.is_guard()):
            rule = match.prev.rule
            self.substitute(rule)
        else:
            
            rule = Rule(-global_val.number_of_rules)
            global_val.number_of_rules += 1
            if self.is_non_terminal():
                rule.last().insert_after(NonTerminal(self.rule, self.exp))
            else:
                rule.last().insert_after(Terminal(self.id, self.exp))

            if self.next.is_non_terminal():
                rule.last().insert_after(NonTerminal(self.next.rule, self.next.exp))
            else:
                rule.last().insert_after(Terminal(self.next.id, self.next.exp))

            match.substitute(rule)
            self.substitute(rule)
            rule.first().put_digram()
           
        # 如果新创建的规则的第一个symbol是非终结符，那么该非终结符对应的规则可能被替代
        if rule.first().is_non_terminal() and rule.first().exp == 1 and rule.first().rule.count == 1:
            rule.first().expand()

    def clean_up(self):
        pass

    # 对于新插入的元素，检查其是否符合几项规则
    def check(self):
        if self.is_guard() or self.next.is_guard():
            return False

        # 应用twins-removal规则
        if self.id == self.next.id:
            self.prev.delete_digram()
            self.exp += self.next.exp
            self.next.clean_up()
            return self.prev.check()

        checked = self.get_digram()

        if checked is None:
            self.put_digram()
            return False

        # twins规则中，发现重叠，应当返回0
        if checked.next is self:
            return False
        else:
            self.process_match(checked)
            return True

    def expand(self):
        pass


# 非终结符
class NonTerminal(Symbol):
    def __init__(self, rule, exp):
        super().__init__()
        self.rule = rule
        self.exp = exp
        self.rule.count += 1
        self.id = self.rule.id

    def clean_up(self):
        join(self.prev, self.next)
        self.delete_digram()
        self.rule.count -= 1

    def is_non_terminal(self):
        return True

    # 对于只出现一次的规则，将其替换掉对应非终结符
    def expand(self):
        left = self.prev
        right = self.next
        first = self.rule.first()
        last = self.rule.last()

        join(left, first)
        join(last, right)
        last.put_digram()

        self.rule.guard.rule = None
        self.rule.guard = None


# 终结符
class Terminal(Symbol):
    def __init__(self, sym_num, exp):
        super().__init__()
        self.id = sym_num
        self.exp = exp

    def clean_up(self):
        join(self.prev, self.next)
        self.delete_digram()


# 哨兵
class Guard(Symbol):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.prev = self
        self.next = self

    def clean_up(self):
        join(self.prev, self.next)

    def is_guard(self):
        return True

    def check(self):
        return False


def append_terminal(sym):
    # print(str(sym) + ' has already got')
    (global_val.main_rule.last()).insert_after(Terminal(sym, 1))
    global_val.main_rule.last().prev.check()


def print_rules(main_rule: global_val.main_rule, rules_list: global_val.rules_list):
    with open('result.txt', 'w') as out:
        global_val.rules_list = [global_val.main_rule]
        length = 1
        j = 0
        while j < length:
            temp = str(-j) + '->'
            ptr = global_val.rules_list[j].first()
            while True:
                if ptr.is_guard():
                    break
                if ptr.is_non_terminal():
                    if length > ptr.rule.index and global_val.rules_list[ptr.rule.index] == ptr.rule:
                        i = ptr.rule.index
                    else:
                        i = length
                        ptr.rule.index = length
                        global_val.rules_list.append(ptr.rule)
                        length += 1
                    temp += str(-ptr.rule.index) + '^' + str(ptr.exp) + ' '
                else:
                    temp += str(ptr.id) + '^' + str(ptr.exp) + ' '
                ptr = ptr.next
            j += 1
            print(temp)
            out.write(temp + '\n')


def _print_rules(rank):
    with open('result.txt', 'w') as out:
        global_val.rules_list = [global_val.main_rule]
        length = 1
        j = 0
        while j < length:
            temp = str(-j) + '->'
            ptr = global_val.rules_list[j].first()
            while True:
                if ptr.is_guard():
                    break
                if ptr.is_non_terminal():
                    if length > ptr.rule.index and global_val.rules_list[ptr.rule.index] == ptr.rule:
                        i = ptr.rule.index
                    else:
                        i = length
                        ptr.rule.index = length
                        global_val.rules_list.append(ptr.rule)
                        length += 1
                    temp += str(-ptr.rule.index) + '^' + str(ptr.exp) + ' '
                else:
                    temp += str(ptr.id) + '^' + str(ptr.exp) + ' '
                ptr = ptr.next
            j += 1
            out.write(temp + '\n')


def sequitur(filename):
    with open(filename, 'r') as file_in:
        count = 0
        for line in file_in:
            number, temp = create_signature_from_event(line)
            if number != None and temp != None:
                append_terminal(number) # 太小的代码块不放进来
            else:
                global_val.small_block_cnt += 1
        # print_rules()


def sequitur_mpi(filename):
    with open(filename, 'r') as file_in:
        variance_dict = {} # trace: mpi1 compute1 mpi2 compute2... key=${mpi1_id}_${mpi2_id} value: [possible fixed workload]
        count = 0
        pre_compute_key, pre_mpi_key = None, None
        for line in file_in:
            number, temp = create_signature_from_event(line)
            if ' MPI_Compute' not in line:
                # 把这个通信终结符和前面的通信终结符和计算终结符合并作为一个key来识别
                if pre_compute_key != None and pre_mpi_key != None:
                    mpi_key = str(pre_mpi_key)+'_'+str(number)
                    if mpi_key not in variance_dict:
                        variance_dict[mpi_key] = [pre_compute_key] 
                    else:    
                        possible_variance_key = variance_dict[mpi_key]
                if number != None and temp != None:
                    append_terminal(number) # 太小的代码块不放进来
                else:
                    global_val.small_block_cnt += 1
                pre_mpi_key = number
            else:
                # 是通信，考虑在这里加上性能波动的识别
                # 1. 性能指标压缩后放到cst当中
                pre_compute_key = number
                # 2. 把这个计算代码块的不变的部分转化为识别性能波动的key
                variance_key = constrcut_variance_key_from_compute_event(line) # [lst, ins, br_cn]


        # print_rules()


def sequitur_compute(filename):
     with open(filename, 'r') as file_in:
        count = 0
        for line in file_in:
            if ' MPI_Compute' in line:
                number, temp = create_signature_from_event(line)
                if number != None and temp != None:
                    append_terminal(number) # 太小的代码块不放进来
                else:
                    global_val.small_block_cnt += 1
        # print_rules()


def find_avaliable_request():
    for i in range(len(global_val.requestUsed)):
        if global_val.requestUsed[i] == False:
            global_val.requestUsed[i] = True
            return i
    return -1


def free_request(i):
    global_val.requestUsed[i] = False


def process_grammar(trace_name, process_type=None):
    global_val.main_rule = Rule(-global_val.number_of_rules)
    global_val.number_of_rules += 1
    if process_type == None:
        sequitur(trace_name)
    elif process_type == 'MPI' or process_type == 'mpi':
        sequitur_mpi(trace_name)
    elif process_type == 'Compute' or process_type == 'COMPUTE' or process_type == 'compute':
        sequitur_compute(trace_name)
    else:
        sequitur(trace_name)