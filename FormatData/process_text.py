import os
import json
import random
from FormatData.FinQA import FinQA, Qa, JsonFunction
from utils.general_utils import *

def format_str(context):
    context = context.replace('-', " ")
    context = context.replace(';', " ;")
    context = context.replace('. ', " . ")
    context = context.replace(', ', " , ")
    context = context.replace('(', "( ")
    context = context.replace(')', " )")
    context = context.replace('$', " $ ")
    context = context.replace('%', " %")
    context = context.replace('\"', "")
    return context


def filter_gold(value_list, time_list, text_list):
    valid_flag = 1
    gold_inds = {}

    num_list = value_list + time_list
    num_list_flag = value_list + time_list
    for (index, text) in enumerate(text_list):
        num_text = re.findall(r"\d+\.?\d*", text)
        if len(num_text) > 15:
            return 0, {}
        for num in num_text:
            if str_to_num(num) in num_list:
                gold_inds['text_' + str(index + 1)] = text
                if str_to_num(num) in num_list_flag:
                    num_list_flag.remove(str_to_num(num))
    if len(num_list_flag) != 0:
        valid_flag = 0
    return valid_flag, gold_inds


def get_table_finqa(table_json, function):
    key = function.variables[0]
    time_list = list(table_json['table_value'][key].keys())
    time_index = random.randint(0, len(time_list) - 1)
    time = time_list[time_index]
    program = function.program
    for v in function.variables:
        program = program.replace(v, str(int(table_json['table_value'][v][time])))
    pre_text = table_json['text']

    text_temp = pre_text.replace('\n', ' ')
    text_temp = format_str(text_temp)
    text_split = text_temp.split(". ")
    text_split_1 = []
    for (index, t) in enumerate(text_split):
        if t != '' and index != len(text_split) - 1:
            text_split_1.append(t + '. ')

    table = table_json['table']
    table = list(map(list, zip(*table)))
    table[0][0] = ''
    all_v_list = list(table_json['table_value'].keys())

    gold_inds = {}
    for (index, v) in enumerate(all_v_list):
        if v in function.variables:
            gold_inds['table_' + str(index + 1)] = table_row_to_text(table[0], table[index + 1])
    #old_inds = {}
    #gold_inds['table_' + str(time_index + 1)] = table_row_to_text(table[0], table[time_index + 1])
    question = 'What is value of ' + function.target + ' in ' + str(time)
    invalid_flag, exe_res = get_res(program, [])
    qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
    finqa = FinQA(0, text_split_1, table, [], qa)
    return finqa

def get_text_finqa_timeFun(table_json, function):
    time_flag = 0
    if '*n-1' in function.target:
        return None
    for v in function.variables:
        if '*n-1' in v:
            time_flag = 1
    key = function.variables[0]
    key = key.split('*')[0]
    time_list = list(table_json['text_value'][key].keys())
    time_list.sort()
    if time_flag == 1:
        if len(time_list) < 2:
            return None
        time_index = random.randint(1, len(time_list) - 1)
        select_time = [int(time_list[time_index]), int(time_list[time_index]) - 1]
    else:
        time_index = random.randint(0, len(time_list) - 1)
        select_time = [int(time_list[time_index])]
    time = time_list[time_index]

    value_list = []
    program = function.program
    for v in function.variables:
        if '*n-1' in v:
            num = table_json['text_value'][v.replace('*n-1', '')][str(int(time) - 1)]
            program = program.replace(v, str(int(num)))
            value_list.append(num)
    for v in function.variables:
        if '*n-1' not in v:
            num = table_json['text_value'][v.replace('*n', '')][time]
            program = program.replace(v, str(int(num)))
            value_list.append(num)
    pre_text = table_json['text']

    text_temp = pre_text.replace('\n', ' ')
    text_temp = format_str(text_temp)
    text_split = text_temp.split(". ")
    text_split_1 = []
    for (index, t) in enumerate(text_split):
        if t != '' and index != len(text_split) - 1:
            text_split_1.append(t + '. ')

    table = table_json['table'].replace('\n','')
    try:
        if table[0] !='[':
            temp = table.split('[')
            table = ''
            for i in range(1, len(temp)):
                table += '[' + temp[i]
        table = json.loads(table)
        table = list(map(list, zip(*table)))
        for (i, t1) in enumerate(table):
            for (j, t) in enumerate(t1):
                table[i][j] = str(t)
        table[0][0] = ''
    except:
        return None

    flag, gold_inds = filter_gold(value_list, select_time, text_split_1)
    if flag != 1:
        return None
    #old_inds = {}
    #gold_inds['table_' + str(time_index + 1)] = table_row_to_text(table[0], table[time_index + 1])
    question = 'What is value of ' + function.target.replace('*n', '').replace('_', ' ') + ' in ' + str(time)
    invalid_flag, exe_res = get_res(program, [])
    qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
    finqa = FinQA(0, text_split_1, table, [], qa)
    return finqa

def get_table_finqa2(table_json):
    this_id = 0
    finqa_list = []
    for key in table_json['table_value']:
        time = list(table_json['table_value'][key].keys())
        value_dict = table_json['table_value'][key]
        value = []
        for key1 in value_dict.keys():
            value.append(value_dict[key1])
        if len(value) < 3:
            continue
        value_index = random.sample(range(0, len(value) - 1), 2)
        target = key
        pre_text = table_json['text']
        table = table_json['table']

        text_temp = pre_text.replace('\n', ' ')
        text_temp = format_str(text_temp)
        text_split = text_temp.split(". ")
        text_split_1 = []
        for (index, t) in enumerate(text_split):
            if t != '' and index != len(text_split) - 1:
                text_split_1.append(t + '. ')

        table = list(map(list, zip(*table)))
        table[0][0] = ''
        all_v_list = list(table_json['table_value'].keys())
        gold_inds = {}
        for (index, v) in enumerate(all_v_list):
            if v == target:
                gold_inds['table_' + str(index + 1)] = table_row_to_text(table[0], table[index + 1])
        #gold_inds = {}
        #for index in value_index:
        #    gold_inds['table_' + str(index + 1)] = table_row_to_text(table[0], table[index + 1])
        value_list = []
        time_list = []
        if time[value_index[0]] > time[value_index[1]]:
            t = value_index[0]
            value_index[0] = value_index[1]
            value_index[1] = t
        for i in value_index:
            time_list.append(int(time[i]))
            value_list.append(int(value[i]))
        question, program = increase(value_list, time_list, target)
        invalid_flag, exe_res = get_res(program, [])
        qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
        this_id += 1
        finqa = FinQA(this_id, text_split_1, table, [], qa)
        finqa_list.append(finqa)
        # increase rate
        value_list = []
        time_list = []
        for i in value_index:
            time_list.append(int(time[i]))
            value_list.append(int(value[i]))
        question, program = increase_rate(value_list, time_list, target)
        invalid_flag, exe_res = get_res(program, [])
        qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
        this_id += 1
        finqa = FinQA(this_id, text_split_1, table, [], qa)
        finqa_list.append(finqa)
        # sum_value
        value_list = []
        time_list = []
        for i in range(min(value_index), max(value_index) + 1):
            time_list.append(int(time[i]))
            value_list.append(int(value[i]))
        question, program = sum_value(value_list, time_list, target)
        invalid_flag, exe_res = get_res(program, [])
        qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
        this_id += 1
        finqa = FinQA(this_id, text_split_1, table, [], qa)
        finqa_list.append(finqa)
        # avg_value
        value_list = []
        time_list = []
        for i in value_index:
            time_list.append(int(time[i]))
            value_list.append(int(value[i]))
        question, program = avg_value(value_list, time_list, target)
        invalid_flag, exe_res = get_res(program, [])
        qa = Qa(question, program, exe_res, str(exe_res), gold_inds, '')
        this_id += 1
        finqa = FinQA(this_id, text_split_1, table, [], qa)
        finqa_list.append(finqa)
    return finqa_list

def process2(path):
    table_finqa_list = []
    # 获取公式
    with open("D:\\code\DataGenerate\\function.json", encoding='utf-8') as input_file:
        input_data = json.load(input_file)
    function_list = []
    for target in input_data.keys():
        json_list = input_data[target]
        for j in json_list:
            fun = JsonFunction(json_obj=j, target=target)
            function_list.append(fun)
    # 获取table json1
    with open(path, encoding='utf-8') as input_file:
        input_data = json.load(input_file)
    for j in input_data:
        table_value = j['table_value']
        variable = table_value.keys()
        for fun in function_list:
            flag = 0
            for v in fun.variables:
                if v in variable:
                    continue
                flag = 1
                break
            if flag == 0:
                finQA = get_table_finqa(j, fun)
                table_finqa_list.append(finQA)
    # table 变化
    for j in input_data:
        table_finqa_list += get_table_finqa2(j)
    return table_finqa_list
    # 遍历table json并处理
def increase(value, time, target):
    target = target.replace('_', ' ')
    question = 'between t1 and t2 , what was the change in target'
    question = question.replace('t1', str(time[0]))
    question = question.replace('t2', str(time[1]))
    question = question.replace('target', target)
    program = 'subtract(v2, v1)'
    program = program.replace('v1', str(value[0]))
    program = program.replace('v2', str(value[1]))
    return question, program

def increase_rate(value, time, target):
    target = target.replace('_', ' ')
    question = 'between t1 and t2 , what was the change rate in target'
    question = question.replace('t1', str(time[0]))
    question = question.replace('t2', str(time[1]))
    question = question.replace('target', target)
    program = 'subtract(v2, v1), divide(#0, v1)'
    program = program.replace('v1', str(value[0]))
    program = program.replace('v2', str(value[1]))
    return question, program

def sum_value(value, time, target):
    target = target.replace('_', ' ')
    question = 'in time_list , what was the total cash flows on target'
    time_list = ''
    for (index, t) in enumerate(time):
        time_list += str(t)
        if index == len(time) - 1:
            continue
        elif index == len(time) - 2:
            time_list += ' and '
        else:
            time_list += ' , '
    question = question.replace('time_list', time_list)
    question = question.replace('target', target)
    program = ''
    for i in range(1, len(value)):
        if i == 1:
            program += 'add(v1, v2)'
            program = program.replace('v1', str(value[i - 1]))
            program = program.replace('v2', str(value[i]))
        else:
            program += 'add(#v1, v2)'
            program = program.replace('v1', str(i-2))
            program = program.replace('v2', str(value[i]))
        if i != len(value) - 1:
            program += ', '
    return question, program

def avg_value(value, time, target):
    target = target.replace('_', ' ')
    question = 'what were average target for aeronautics in millions from t1 to t2?'
    t_max = max(time)
    t_min = min(time)
    question = question.replace('t1', str(t_min))
    question = question.replace('t2', str(t_max))
    question = question.replace('target', target)
    program = ''
    for i in range(1, len(value)):
        if i == 1:
            program += 'add(v1, v2)'
            program = program.replace('v1', str(value[i - 1]))
            program = program.replace('v2', str(value[i]))
        else:
            program += 'add(#v1, v2)'
            program = program.replace('v1', str(i-2))
            program = program.replace('v2', str(value[i]))
        program += ', '
    program += 'divide(#v1, const_v2)'
    program = program.replace('v1', str(len(value) - 2))
    program = program.replace('v2', str(t_max - t_min + 1))
    return question, program

def process(path, Funs):
    text_finqa_list = []
    function_list = []
    # 获取公式
    for f in Funs:
        fun = JsonFunction(variables=f['variables'], formula=f['formula'], target=f['target'])
        function_list.append(fun)
    # 获取text json1
    with open(path, encoding='utf-8') as input_file:
        input_data = json.load(input_file)
    for j in input_data:
        text_value = j['text_value']
        variable = text_value.keys()
        for fun in function_list:
            flag = 0
            for v in fun.variable_without_time:
                if v in variable:
                    continue
                flag = 1
                break
            if flag == 0:
                finQA = get_text_finqa_timeFun(j, fun)
                if finQA is not None:
                    text_finqa_list.append(finQA)
    return text_finqa_list
#process("D:\\code\\DataGenerate\\FormatData\\table_text.json")