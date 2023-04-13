import global_val
from editDistance import levenshtein_distance
from nonterminal_dict import Symbol, NonTerminal, Terminal, Guard, Rule

max_difference = 0.3


# main_rule_strings = [['1^1', '2^1', '3^1', '4^1', '5^1', '6^1', '7^1', '6^1', '8^1', '-1^1', '12^1', '-2^1',
# '29^1', '30^1', '31^1', '-3^74', '-4^1', '33^1', '34^1', '35^1'], ['1^1', '6^1', '3^1', '4^1', '5^1', '6^1', '7^1',
# '6^1', '8^1', '-12^1', '-13^1', '29^1', '30^1', '31^1', '-14^74', '-15^1', '42^1', '34^1', '9^1'], ['1^1', '6^1',
# '3^1', '4^1', '43^1', '6^1', '44^1', '6^1', '8^1', '-1^1', '-20^1', '29^1', '30^1', '31^1', '-21^74', '-22^1',
# '42^1', '34^1', '9^1'], ['1^1', '6^1', '3^1', '4^1', '43^1', '6^1', '44^1', '6^1', '8^1', '-12^1', '-27^1', '29^1',
# '30^1', '31^1', '-28^74', '-29^1', '42^1', '34^1', '9^1'], ['1^1', '49^1', '3^1', '4^1', '5^1', '6^1', '7^1',
# '6^1', '8^1', '-1^1', '-34^1', '29^1', '30^1', '31^1', '-35^70', '-36^1', '50^1', '-37^1', '-38^4', '-39^1',
# '42^1', '34^1', '9^1'], ['1^1', '49^1', '3^1', '4^1', '-47^1', '29^1', '30^1', '31^1', '-48^6', '-49^3', '-50^1',
# '51^1', '-51^1', '-52^1', '-51^1', '-53^1', '-52^1', '-54^1', '-53^7', '-55^1', '-56^66', '-57^1', '42^1', '34^1',
# '9^1'], ['1^1', '6^1', '3^1', '52^1', '43^1', '6^1', '44^1', '6^1', '8^1', '-1^1', '-69^1', '29^1', '30^1', '31^1',
# '-70^74', '-71^1', '42^1', '34^1', '9^1'], ['1^1', '6^1', '3^1', '4^1', '43^1', '6^1', '44^1', '6^1', '8^1',
# '-12^1', '-75^1', '29^1', '30^1', '31^1', '-76^74', '-77^1', '42^1', '34^1', '9^1']]


def calculate_lcs(rule1, rule2):
    # print("start combing two rules")
    combined_rule = Rule(rule1.id)
    rule_body1 = rule1.get_rule_body_symbol()
    rule_body2 = rule2.get_rule_body_symbol()
    # print(rule1.get_rule_body())
    # print(rule2.get_rule_body())
    len1 = len(rule_body1)
    len2 = len(rule_body2)
    dp = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if rule_body1[i - 1].id == rule_body2[j - 1].id and rule_body1[i - 1].exp == rule_body2[j - 1].exp:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    symbols_list = []
    i2 = len1
    j2 = len2
    while i2 > 0 and j2 > 0:
        if dp[i2][j2] == dp[i2 - 1][j2 - 1] + 1 \
                and dp[i2 - 1][j2] == dp[i2][j2 - 1] \
                and dp[i2 - 1][j2 - 1] == dp[i2 - 1][j2]:
            # combine_similar_path(i2 - 1, j2 - 1)
            e = rule_body1[i2 - 1]
            t = Terminal(e.id, e.exp)
            t.ranks.extend(e.ranks)
            t.ranks.extend(rule_body2[j2 - 1].ranks)
            i2 -= 1
            j2 -= 1
            symbols_list.append(t)
            # combined_rule.last().insert_after(t)
        elif dp[i2][j2] == dp[i2 - 1][j2]:
            # combine_similar_path(i2 - 1, j2)
            e = rule_body1[i2 - 1]
            t = Terminal(e.id, e.exp)
            t.ranks.extend(e.ranks)
            i2 -= 1
            symbols_list.append(t)
            # combined_rule.last().insert_after(t)
        else:
            # combine_similar_path(i2, j2 - 1)
            e = rule_body2[j2 - 1]
            t = Terminal(e.id, e.exp)
            t.ranks.extend(e.ranks)
            j2 -= 1
            symbols_list.append(t)
            # combined_rule.last().insert_after(t)

    # combine_similar_path(len1, len2)
    for i in range(len(symbols_list) - 1, -1, -1):
        combined_rule.last().insert_after(symbols_list[i])

    # print(combined_rule.get_rule_body())
    # for elem in combined_rule.get_rule_body_symbol():
    #     print(elem.ranks, end=' ')
    # print('\n')
    return combined_rule


def combine_main_rule(rank, comm, main_rules, rule_dict):
    main_rule_strings = []
    unique_main_rules = []
    unique_main_rule_num = []
    if rank == 0:
        for i in range(len(main_rules)):
            main_rule_strings.append(rule_dict[main_rules[i]].get_rule_body().split(' '))
        for i in range(len(main_rules)):
            # print(main_rule_strings[i])
            rule = Rule(i)
            unique_main_rules.append(rule)
            unique_main_rule_num.append(i)
            for j in range(len(main_rule_strings[i])):
                e = main_rule_strings[i][j].split('^')
                terminal = Terminal(e[0], e[1])
                terminal.ranks.append(i)
                rule.last().insert_after(terminal)
    main_rule_strings = comm.bcast(main_rule_strings, 0)
    # print('rank = ' + str(rank))
    # print(main_rule_strings)
    dict_similar = ''
    local_string = ''
    size = comm.Get_size()
    for j in range(rank + 1, size):
        edit_distance = float(levenshtein_distance(main_rule_strings[rank], main_rule_strings[j]))
        max_len1 = max(len(main_rule_strings[rank]), len(main_rule_strings[j]))
        number_format = format(edit_distance / max_len1, '.5f')
        if float(number_format) < max_difference:
            dict_similar += str(j) + ' '
        local_string += number_format + ' '

    all_string = comm.gather(local_string, 0)
    all_dict_similar = comm.gather(dict_similar, 0)
    if rank == 0:
        # print(all_string)
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
                # 注意，这里不能正序遍历，因为在正序遍历的过程中删除列表的元素，会导致下标出现问题。其实更好看的解决方案是用filter，但是因为元素比较多所以直接倒序了
                for i in range(len(line) - 1, -1, -1):
                    if int(line[i]) in joined.keys():
                        line.remove(line[i])
                    else:
                        joined[int(line[i])] = 1
                line = ' '.join(line)
                clusters.append(line)
            index += 1
        # print(clusters)
        for cluster in clusters:
            cluster = cluster.split(' ')
            main_rank = int(cluster[0])
            for rank in range(1, len(cluster)):
                # print(unique_main_rule_num)
                if unique_main_rules[int(cluster[rank])].id in unique_main_rule_num:
                    unique_main_rules[main_rank] = calculate_lcs(unique_main_rules[main_rank],
                                                                 unique_main_rules[int(cluster[rank])])
                    unique_main_rule_num.remove(unique_main_rules[int(cluster[rank])].id)
                    unique_main_rules[int(cluster[rank])] = unique_main_rules[main_rank]
    return unique_main_rules
        # main_rank = unique_main_rule_num[0]
        # for i in range(1, len(unique_main_rule_num)):
        #     unique_main_rules[main_rank] = calculate_lcs(unique_main_rules[main_rank],
        #                                                  unique_main_rules[unique_main_rule_num[i]])
        #
        # return unique_main_rules[main_rank]

def parse_main_rules(main_rules):
    visit_dict = {}
    cnt = 0
    unique_main_rules = []
    for main_rule in main_rules:
        ranks = main_rule.first().ranks
        flag = False
        for rank in ranks:
            if rank in visit_dict:
                flag = True
                break
        if flag:
            continue
        cnt += 1
        unique_main_rules.append(main_rule)
    return unique_main_rules

