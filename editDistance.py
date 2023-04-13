import numpy as np
import pickle
import argparse

max_difference = 0.1


def deserialize(output_filename):
    with open(output_filename, "rb") as fin:
        data_info = pickle.load(fin)
        all_cfg = data_info['unique_grammar']
    return all_cfg


def levenshtein_distance(str1, str2):
    len1, len2 = len(str1), len(str2)
    dp = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (str1[i - 1] != str2[j - 1]))
    # for line in dp:
    #     print(line)
    # print(dp[-1][-1])
    return dp[-1][-1]


# levenshtein_distance("abcdbcdbcd", "abcebcebce")

def parse_cfg_lists(all_cfg, output_filename, rank, size, comm):
    all_str_list = []
    for one_cfg in all_cfg:
        str_list = []
        for one_rule in one_cfg:
            length = len(one_rule)
            rule_head = one_rule[0]
            one_rule = [str(e) for e in one_rule]
            str1 = "".join(one_rule)
            str_list.append(str1)
            rule_body = []
            for i in range(1, length, 2):
                rule_body.append(str(one_rule[i]) + "^" + str(one_rule[i + 1]))
        string_one_cfg = "".join(str_list)
        all_str_list.append(string_one_cfg)
    # for line in all_str_list:
    #     print(line)
    # res_of_ratio = [[0 for _ in range(len(all_str_list))] for _ in range(len(all_str_list))]
    dict_similar = ''
    # with open(output_filename, "w") as fo:
    #     for i in range(len(all_str_list) - 1):
    #         for j in range(i):
    #             fo.write("0.00000 ")
    #         for j in range(i + 1, len(all_str_list)):
    #             print("compare " + str(i) + " and " + str(j) + " :")
    #             edit_distance = float(levenshtein_distance(all_str_list[i], all_str_list[j]))
    #             max_len1 = max(len(all_str_list[i]), len(all_str_list[j]))
    #             # print(edit_distance)
    #             number_format = format(edit_distance / max_len1, '.5f')
    #             if float(number_format) < max_difference:
    #                 if i not in dict_similar.keys():
    #                     dict_similar[i] = [j]
    #                 else:
    #                     dict_similar[i].append(j)
    #             fo.write(str(number_format) + " ")
    #             # res_of_ratio[i][j] = edit_distance / max(len(all_str_list[i]), len(all_str_list[j]))
    #         fo.write("\n")
    if size != len(all_str_list):
        print("process number not matched!")
        return dict_similar
    fo = open(output_filename, 'w')
    local_string = ""
    # print("process " + str(rank) + " is calculating")
    for j in range(rank + 1, size):
        edit_distance = float(levenshtein_distance(all_str_list[rank], all_str_list[j]))
        max_len1 = max(len(all_str_list[rank]), len(all_str_list[j]))
        number_format = format(edit_distance / max_len1, '.5f')
        if float(number_format) < max_difference:
            dict_similar += str(j) + ' '
        local_string += number_format + ' '

    all_string = comm.gather(local_string, 0)
    all_dict_similar = comm.gather(dict_similar, 0)

    if rank == 0:
        # print(all_dict_similar)
        clusters = []
        joined = {}
        index = 0
        for line in all_dict_similar:
            line = line.strip()
            if line == '':
                index += 1
                continue
            line = line.split(' ')
            if index in joined.keys():
                index += 1
                continue
            else:
                line.insert(0, str(index))
                for elem in line:
                    joined[int(elem)] = 1
                line = ' '.join(line)
                clusters.append(line)
            index += 1
        # print(clusters)
        for line in clusters:
            fo.write(str(line) + '\n')
        fo.write("******************************  end of cluster  ******************************\n")
        for line in all_string:
            fo.write(line + '\n')
    fo.close()
    return dict_similar


# cfg_list = deserialize(filename)
# parse_cfg_lists(cfg_list, out_file)
