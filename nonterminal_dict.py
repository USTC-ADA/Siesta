def join(left, right):
    left.next = right
    right.prev = left


class Rule:
    def __init__(self, rule_num):
        self.id = rule_num
        self.guard = Guard(self)
        self.count = 0
        self.index = 0
        self.depth = -1

    def first(self):
        return self.guard.next

    def last(self):
        return self.guard.prev

    def get_rule_body(self):
        ptr = self.guard.next
        body_string = ''
        while ptr != self.guard:
            if ptr.is_non_terminal():
                body_string += ' ' + ptr.rule.id + '^' + ptr.exp
            else:
                body_string += ' ' + ptr.id + '^' + ptr.exp
            ptr = ptr.next
        body_string = body_string.strip()
        return body_string

    def get_rule_body_symbol(self):
        ptr = self.guard.next
        rule_body = []
        while ptr != self.guard:
            rule_body.append(ptr)
            ptr = ptr.next
        return rule_body

    def get_depth(self, rule_dict):
        self.depth = 1
        ptr = self.guard.next
        while ptr != self.guard:
            
            ptr =ptr.next

class Symbol:
    def __init__(self):
        self.id = '0'
        self.exp = '1'
        self.rule = None
        self.prev = None
        self.next = None
        self.ranks = []

    def is_guard(self):
        return False

    def is_non_terminal(self):
        return False

    def insert_after(self, symbol):
        join(symbol, self.next)
        join(self, symbol)


class NonTerminal(Symbol):
    def __init__(self, rule, exp):
        super().__init__()
        self.rule = rule
        self.exp = exp
        self.rule.count += 1
        self.id = self.rule.id
        self.depth = -1

    def is_non_terminal(self):
        return True


class Terminal(Symbol):
    def __init__(self, sym_num, exp):
        super().__init__()
        self.id = sym_num
        self.exp = exp
        self.depth = 0


class Guard(Symbol):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.prev = self
        self.next = self

    def is_guard(self):
        return True


def build_dict(all_cfg):
    rule_dict = {}
    main_rules = []
    for one_cfg in all_cfg:
        index = 0
        for line in one_cfg:
            line = line.strip()
            line = line.split('->')
            one_rule = Rule(line[0])
            # print(line[0])
            rule_dict[line[0]] = one_rule
            if index == 0:
                main_rules.append(line[0])
                index += 1

        for line in one_cfg:
            line = line.strip()
            line = line.split('->')
            rule_body = line[1].split(' ')
            # print(rule_body)
            for e in rule_body:
                if len(e) < 1:
                    continue
                elem = e.split('^')
                # print(elem)
                if elem[0] in rule_dict.keys():
                    nt = NonTerminal(rule_dict[elem[0]], elem[1])
                    rule_dict[line[0]].last().insert_after(nt)
                else:
                    t = Terminal(elem[0], elem[1])
                    rule_dict[line[0]].last().insert_after(t)
    dict_length_old = 0
    dict_length_new = 1
    i = 0
    unique_dict = {}
 

    # 记录每一个非终结符的depth
    depth_dict = {}
    for key, value in rule_dict.items():
        depth = 1
        queues = []
        ptr = value.guard.next
        while ptr != value.guard:
            if ptr.is_non_terminal():
                queues.append(ptr)
            ptr =ptr.next
        while len(queues) > 0:
            # 将当前queues里的所有非终结符全部展开，直到不能展开
            cur_queues = []
            for nonterm in queues:
                ptr = nonterm.rule.guard.next
                while ptr != nonterm.rule.guard:
                    if ptr.is_non_terminal():
                        cur_queues.append(ptr)
                    ptr = ptr.next
            queues = cur_queues    
            depth += 1
        if depth not in depth_dict:
            # 如果当前的这个depth不在已经记录的dict里，把他加进来
            depth_dict[depth] = []
        depth_dict[depth].append(key)
        value.depth = depth

    # 从depth较低的终结符开始合并
    unique_dict = {}    # 最终的非终结符字典，
    nonterm_cnt = 0
    for depth in sorted(depth_dict.keys(), key=lambda x:x):
        cur_depth_list = depth_dict[depth]
        for nonterm_key in cur_depth_list:
            # 遍历当前depth对应的所有非终结符
            rule_body = rule_dict[nonterm_key].get_rule_body()

            if rule_body not in unique_dict:
                # 如果这个展开不在已有的unique_dict当中，那就把他添加进来，注意这里由于分了depth，所以引用的终结符必定是合并过的，并且不会出现同depth的相互引用
                unique_dict[rule_body] = str(nonterm_cnt)
                rule_dict[nonterm_key].id = str(nonterm_cnt)
                nonterm_cnt -= 1
            else:
                # 如果已经有了一样的，那就要合并
                rule_dict[nonterm_key].id = str(unique_dict[rule_body])
        pass
    # if global_val.rank == 0:
    # print('####### show rule dict and unique dict #######')
    # print('unique dict', unique_dict)
    # print('rule dict', rule_dict)
    # print('####### show rule dict and unique dict #######')
    return main_rules, unique_dict, rule_dict


def print_rules(rule_dict, one_cfg, rank):
    with open('result.txt', 'w') as out:
        rules_list = [rule_dict[one_cfg[0].split('->')[0]]]
        length = 1
        j = 0
        while j < length:
            temp = rules_list[j].id + '->'
            ptr = rules_list[j].first()
            while True:
                if ptr.is_guard():
                    break
                if ptr.is_non_terminal():
                    if length > ptr.rule.index and rules_list[ptr.rule.index] == ptr.rule:
                        i = ptr.rule.index
                    else:
                        i = length
                        ptr.rule.index = length
                        rules_list.append(ptr.rule)
                        length += 1
                    temp += ptr.rule.id + '^' + str(ptr.exp) + ' '
                else:
                    temp += str(ptr.id) + '^' + str(ptr.exp) + ' '
                ptr = ptr.next
            j += 1
            # print(temp)
            out.write(temp + '\n')
