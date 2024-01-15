from FormatData.FinQA import FinQA
import json
import random
import os
import re
from utils.general_utils import *
from config import params


def data_split(full_list, ratio, shuffle=True):
    """
    数据集拆分: 将列表full_list按比例ratio（随机）划分为2个子列表sublist_1与sublist_2
    :param full_list: 数据列表
    :param ratio:     子列表1
    :param shuffle:   子列表2
    :return:
    """
    n_total = len(full_list)
    offset = int(n_total * ratio)
    if n_total == 0 or offset < 1:
        return [], full_list
    if shuffle:
        random.shuffle(full_list)
    sublist_1 = full_list[:offset]
    sublist_2 = full_list[offset:]
    return sublist_1, sublist_2


def print_steps(list):
    gold_num = {}
    for f in list:
        p = f['qa']['program']
        len_p = len(p.split('('))
        if len_p in gold_num:
            gold_num[len_p] = gold_num[len_p] + 1
        else:
            gold_num[len_p] = 1
    for k in gold_num.keys():
        gold_num[k] = float(gold_num[k]) / float(len(list))
    print("steps分布", gold_num)


def print_gold(list):
    gold_num = {}
    for f in list:
        if len(f['qa']['gold_inds']) in gold_num:
            gold_num[len(f['qa']['gold_inds'])] = gold_num[len(f['qa']['gold_inds'])] + 1
        else:
            gold_num[len(f['qa']['gold_inds'])] = 1
    for k in gold_num.keys():
        gold_num[k] = float(gold_num[k]) / float(len(list))
    print("gold_num分布", gold_num)


def check_gold(gold, program, question):
    gold_nums = []
    for key in gold.keys():
        nums = re.findall(r"\d+\.?\d*", gold[key])
        gold_nums += nums
    request_num = []
    # nums = re.findall(r"\d+\.?\d*", program)
    nums = []
    strlist = program.split(',')
    for s in strlist:
        if '(' in s:
            nums_str = s.split('(')[1]
        else:
            nums_str = s.split(')')[0]
        if '_' not in nums_str and '#' not in nums_str:
            nums.append(nums_str.replace(' ',''))
    request_num += nums
    nums = re.findall(r"\d+\.?\d*", question)
    request_num += nums
    for num in request_num:
        if num not in gold_nums:
            return False
    return True


def check_finqa_data(finqa):
    if len(finqa.qa.gold_inds) > params.max_gold:
        return False
    if "This growth can be attributed to an expansion in sales volumes and an increase in the average selling price of products. " in finqa.pre_text:
        return False
    if "Despite the increased cost, we managed to generate an income of  $ 600000, indicating a significant growth in our revenue. " in finqa.pre_text:
        return False
    if len(finqa.qa.gold_inds) >= len(finqa.pre_text) + len(finqa.table):
        return False
    if len(finqa.pre_text) == 0 or len(finqa.table) <= 1:
        return False
    if finqa.qa.exe_ans == 'n/a':
        return False
    return True


def write_json(finqa_list: list, path: str, blend: bool = True, old_path: str = 'json') -> None:
    content = []
    id = 1
    for f in finqa_list:
        if len(f.qa.gold_inds) > 0:
            '''
            if not check_gold(f.qa.gold_inds, f.qa.program, f.qa.question):
                print(f)
                continue
            '''
            if len(f.pre_text) == 0:
                f.pre_text.append("Report")
            if not check_finqa_data(f):
                continue
            if not check_gold(f.qa.gold_inds, f.qa.program, f.qa.question):
                continue
            table = []
            for r in f.table:
                row = []
                for c in r:
                    row.append(str(c))
                table.append(row)
            # table 转置
            # table = list(map(list, zip(*table)))
            f.table = table
            f.id = str(id)
            id += 1
            content.append(f.get_dict())
    #print_gold(content)
    #print_steps(content)
    random.shuffle(content)
    train, last = data_split(content, params.train_rate, True)
    test, dev = data_split(last, params.test_rate / (1 - params.train_rate), True)

    # train = train[0:3000]
    # test = test[0:500]
    # dev = dev[0:500]

    if blend:
        old_train_path = os.path.join(old_path, 'train.json')
        old_dev_path = os.path.join(old_path, 'dev.json')
        old_test_path = os.path.join(old_path, 'test.json')
        with open(old_train_path, encoding='utf-8') as input_file:
            train_data = json.load(input_file)
        with open(old_dev_path, encoding='utf-8') as input_file:
            dev_data = json.load(input_file)
        with open(old_test_path, encoding='utf-8') as input_file:
            test_data = json.load(input_file)
        train = train + train_data
        random.shuffle(train)
        dev = dev + dev_data
        random.shuffle(dev)
        test = test + test_data
        random.shuffle(test)
        print("finqa")
        print_gold(train_data + dev_data + test_data)
    print("train：", len(train))
    print("test：", len(test))
    print("dev：", len(dev))
    train_path = os.path.join(path, 'train.json')
    dev_path = os.path.join(path, 'dev.json')
    test_path = os.path.join(path, 'test.json')
    mkdir(path)
    with open(train_path, "w", encoding='utf-8') as f:
        json.dump(train, f, indent=4)
    with open(dev_path, "w", encoding='utf-8') as f:
        json.dump(dev, f, indent=4)
    with open(test_path, "w", encoding='utf-8') as f:
        json.dump(test, f, indent=4)
