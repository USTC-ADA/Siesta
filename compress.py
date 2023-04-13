import pickle
import argparse
import sys
import inspect


def getArgs():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--tracepath', '-t', dest='pathPrefix', default='/home/yantao/run/sequitur/flash_traces_new/', help='trace file path prefix')
    # parser.add_argument('--nprocs', '-n', dest='nprocs', default=36, help='process number')
    parser.add_argument('--output', '-o', dest='outprefix', default='/home/yantao/run/sequitur/', help='output Filename')
    # parser.add_argument('--compress', '-c', dest='compress', action='store_true', help='enable inter process compression in main_rule')
    args = parser.parse_args() 
    return args

args = getArgs()

with open(args.outprefix+'compressed_trace', "rb") as fin:
    gathered_cst = pickle.load(fin)
    non_terminal_dict = pickle.load(fin)
    computeDict = pickle.load(fin)
    requestNum = pickle.load(fin)
    # rules_list = pickle.load(fin)
    # lcs_main_rules = pickle.load(fin)
    # comm_cnt = pickle.load(fin)
    # main_rule_ids = pickle.load(fin)

# print(non_terminal_dict)
print(sys.getsizeof(pickle.dumps(gathered_cst)))
print(sys.getsizeof(pickle.dumps(non_terminal_dict)))

def delete_unnecessary_symbol_times(symbols):
    for i in range(len(symbols)):
        symbol = symbols[i]
        try:
            if symbol.split('^')[1] == '1':
                symbols[i] = symbol.split('^')[0]
        except Exception as e:
            print(e)
    return ' '.join(symbols)

for key in non_terminal_dict.keys():
    value = non_terminal_dict[key]
    symbols = value.split(' ')
    non_terminal_dict[key] = delete_unnecessary_symbol_times(symbols)
print(gathered_cst)
print(computeDict)
# print(non_terminal_dict)
print(sys.getsizeof(pickle.dumps(non_terminal_dict)))

# # based on the obervation
def compress_non_term(nonterm):
    symbols = nonterm.split(' ')
    step = [2,3,4,5]
    pass