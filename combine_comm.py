import argparse
import os
import editDistance
from utils import inverseDict

import nonterminal_dict
from with_compute import *
from mpi4py import MPI
from constant import *
import numpy as np
import pickle


def combine_cst(rank, comm, outprefix):
    with open(outprefix + '/' + str(rank) + "cst&cfg.log", 'w') as fo:
        all_cst = comm.gather(global_val.call_signature_table, root=0)
        # all_cst_sum = [0]
        all_cst_sum = comm.reduce(len(global_val.call_signature_table), root=0, op=MPI.SUM)
        # comm.reduce(len(global_val.call_signature_table), all_cst_sum)
        if rank == 0:
            print('all process cst sum = {}'.format(all_cst_sum))
        gathered_cst = {}
        cst_num_global = 0
        for key, value in global_val.call_signature_table.items():
            fo.write(str(key) + " : " + str(value) + "\n")
        if rank == 0:
            for one_dict in all_cst:
                if gathered_cst is None:
                    gathered_cst = one_dict
                    cst_num_global = len(gathered_cst)
                else:
                    for elem in one_dict.keys():
                        if elem not in gathered_cst:
                            cst_num_global += 1
                            gathered_cst[elem] = cst_num_global
        gathered_cst = comm.bcast(gathered_cst, root=0)
        # print("process" + str(rank) + "receive : \n" + str(combined_cst))
    if rank == 0:
        print('gatheres cst num = {}'.format(len(gathered_cst)))
    return gathered_cst


def inverse_dict(cst):
    return dict(zip(cst.values(), cst.keys()))


def serialize_cfg(combined_cst, rank):
    inversed_dict = inverse_dict(global_val.call_signature_table)
    cfg_list = []
    # concrete_grammar(global_val.main_rule)
    rules_list = [global_val.main_rule]
    length = 1
    j = 0
    while j < length:
        temp = str(rank) + '&' + str(-j) + '->'
        ptr = rules_list[j].first()
        while True:
            if ptr.is_guard():
                break
            # temp += "a\"" + str(id(ptr)) + "\" "
            if ptr.is_non_terminal():
                if length > ptr.rule.index and rules_list[ptr.rule.index] == ptr.rule:
                    i = ptr.rule.index
                else:
                    i = length
                    ptr.rule.index = length
                    rules_list.append(ptr.rule)
                    length += 1
                temp += str(rank) + '&' + str(-i) + '^' + str(ptr.exp) + ' '
            else:
                temp += str(combined_cst[inversed_dict[ptr.id]]) + '^' + str(ptr.exp) + ' '
            ptr = ptr.next
        j += 1
        cfg_list.append(temp)
    return concrete_grammar(cfg_list)


def serialize_cfg_for_edit_distance(combined_cst, comm):
    inversed_dict = inverse_dict(global_val.call_signature_table)
    cfg_list = []
    rules_list = [global_val.main_rule]
    length = 1
    j = 0
    while j < length:
        temp = [-j]
        ptr = rules_list[j].first()
        while True:
            if ptr.is_guard():
                break
            # temp += "a\"" + str(id(ptr)) + "\" "
            if ptr.is_non_terminal():
                if length > ptr.rule.index and rules_list[ptr.rule.index] == ptr.rule:
                    i = ptr.rule.index
                else:
                    i = length
                    ptr.rule.index = length
                    rules_list.append(ptr.rule)
                    length += 1
                temp.append(-i)
                temp.append(ptr.exp)
            else:
                temp.append(combined_cst[inversed_dict[ptr.id]])
                temp.append(ptr.exp)
            ptr = ptr.next
        j += 1
        cfg_list.append(temp)
    gathered_grammar = comm.gather(cfg_list, 0)
    gathered_grammar = comm.bcast(gathered_grammar, 0)
    return gathered_grammar


def combine_cfg(combined_cst, loacl_cfg, rank, comm, outprefix):
    # print("start combining context free grammar")
    gathered_grammar = comm.gather(loacl_cfg, 0)
    all_cfg_sum = comm.reduce(len(loacl_cfg), root=0, op=MPI.SUM)
    # comm.reduce(len(global_val.call_signature_table), all_cst_sum)
    if rank == 0:
        print('all process cfg sum = {}'.format(all_cfg_sum))

    if outprefix != None:    
        with open(outprefix + '/' + str(rank) + "cst&cfg.log", 'a') as fo:
            fo.write("\n")
            for line in loacl_cfg:
                fo.write(str(line) + "\n")

    if rank == 0:
        main_rules, unique_dict, rule_dict = nonterminal_dict.build_dict(gathered_grammar)
    else:
        main_rules = []
        unique_dict = {}
        rule_dict = {}
    comm.barrier()
    if rank == 0:
        print('compressed cfg sum = {}'.format(len(unique_dict)))
    # main_rules = comm.bcast(main_rules, 0)
    # unique_dict = comm.bcast(unique_dict, 0)
    # rule_dict = comm.bcast(rule_dict, 0)
    
    return main_rules, unique_dict, rule_dict


def serialize(unique_grammar, grammar_number, combined_cst, outprefix):
    data_info = {
        'unique_grammar': unique_grammar,
        'grammar_number': grammar_number,
        'combined_cst': combined_cst
    }
    if outprefix != None:
        with open(outprefix + 'combined_cst_cfg', "wb") as fout:
            pickle.dump(data_info, fout)


def deserialize(outprefix):
    with open(outprefix + 'combined_cst_cfg', "rb") as fin:
        data_info = pickle.load(fin)


def comm_combine(rank, comm, outprefix):
    global_val.rank = rank
    if rank == 0:
        if outprefix != None:
            if not os.path.exists(outprefix):
                os.mkdir(outprefix)
    comm.barrier()

    gathered_cst = combine_cst(rank, comm, outprefix)

    global_val.gathered_cst = inverseDict(gathered_cst)

    # 用于计算全局的非终结符字典和新的main rule
    gathered_cfg = serialize_cfg(gathered_cst, rank)

    main_rules, unique_dict, rule_dict = combine_cfg(gathered_cst, gathered_cfg, rank, comm, outprefix)
    comm.barrier()


    return main_rules, unique_dict, rule_dict
    # global_val.main_rules = main_rules
    # global_val.unique_dict = unique_dict
    # global_val.rule_dict = rule_dict


def calculate_edit_distance(rank, comm, outprefix):
    gathered_cst = combine_cst(rank, comm, outprefix)
    # 用于计算最小编辑距离
    all_cfg = serialize_cfg_for_edit_distance(gathered_cst, comm)
    editDistance.parse_cfg_lists(all_cfg, outprefix + "res_of_tatio.log", rank, comm.Get_size(), comm)


def have_one_value(d):
    for value in d.values():
        if value == 1:
            return True
    return False


def compute_nonterm_ref(cfg_dict):
    nonterm_ref_dict = {}
    for nonterm in cfg_dict.keys():
        expand_res = cfg_dict[nonterm]
        expand_symbols = expand_res.split(' ')
        for symbol in expand_symbols:
            if len(symbol) <= 1:
                continue
            symbol_id = symbol.split('^')[0]
            if '&' not in symbol_id:
                continue
            exp = symbol.split('^')[1]
            if symbol_id not in nonterm_ref_dict:
                nonterm_ref_dict[symbol_id] = 0
            nonterm_ref_dict[symbol_id] += 1
            if int(exp) != 1:
                # 如果exp不为1的话，说明不能展开，直接给ref加1，保证不会被展开
                nonterm_ref_dict[symbol_id] += 1
    return nonterm_ref_dict

    
def expand_rule(cfg_dict, nonterm_id):
    tag = '{}^{}'.format(nonterm_id, 1)
    for nonterm in cfg_dict.keys():
        if tag in cfg_dict[nonterm]:
            cfg_dict[nonterm] = cfg_dict[nonterm].replace(tag, cfg_dict[nonterm_id])
            break
    del(cfg_dict[nonterm_id])


def concrete_grammar(cfg_list):
    # 1. construct cfg dict
    cfg_dict = {cfg.split('->')[0]: cfg.split('->')[1] for cfg in cfg_list}

    nonterm_ref_dict = compute_nonterm_ref(cfg_dict)

    while have_one_value(nonterm_ref_dict):
        for key in nonterm_ref_dict.keys():
            if nonterm_ref_dict[key] == 1:
                expand_rule(cfg_dict, key)

        nonterm_ref_dict = compute_nonterm_ref(cfg_dict)
    cfg_list = ['{}->{}'.format(key, cfg_dict[key]) for key in cfg_dict.keys()]
    return cfg_list
