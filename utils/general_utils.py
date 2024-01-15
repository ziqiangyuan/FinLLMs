import argparse
import collections
import json
import os
import re
import string
import sys
import random


def remove_space(text_in):
    res = []

    for tmp in text_in.split(" "):
        if tmp != "":
            res.append(tmp)

    return " ".join(res)


def table_row_to_text(header, row):
    '''
    use templates to convert table row to text
    '''
    res = ""

    if header[0]:
        res += (header[0] + " ")

    for head, cell in zip(header[1:], row[1:]):
        res += ("the " + remove_mart(str(row[0])) + " of " + remove_mart(str(head)) + " is " + remove_mart(str(cell)) + " ; ")

    res = remove_space(res)
    return res.strip()


def remove_mart(text):
    p = re.compile(r'\d,\d')

    while 1:
        m = p.search(text)
        if m:
            mm = m.group()
            text = text.replace(mm, mm.replace(',', ''))
        else:
            break
    return text

def str_to_num(text):
    text = text.replace(",", "")
    try:
        num = float(text)
    except ValueError:
        if "%" in text:
            text = text.replace("%", "")
            try:
                num = float(text)
                num = num / 100.0
            except ValueError:
                num = "n/a"
        elif "const" in text:
            text = text.replace("const_", "")
            if text == "m1":
                text = "-1"
            num = float(text)
        else:
            num = "n/a"
    return num

def is_num(text):
    text = str(text)
    text = text.replace(",", "")
    try:
        num = int(text)
    except ValueError:
        try:
            num = float(text)
        except ValueError:
            if text and text[-1] == "%":
                num = text
            else:
                return False
    return True

def get_program_from_text(text):
    # 0代表无效
    res = []
    text = text.replace(' ', '')
    text = text.replace('\n', '')
    if '(' in text:
        op = text.split('(')[0] + '('
        res.append(op)
        text = text.split('(')[1]
    else:
        return 1, []
    if ',' in text:
        arg1 = text.split(',')[0]
        arg2 = text.split(',')[1]
        arg2 = arg2[:-1]
        res.append(arg1)
        res.append(arg2)
        res.append(')')
    else:
        return 1, []
    return 0, res

all_ops = ["add", "subtract", "multiply", "divide", "exp", "greater", "table_max",
           "table_min", "table_sum", "table_average"]
def eval_program(program, table):
    '''
    calculate the numerical results of the program
    '''

    invalid_flag = 0
    this_res = "n/a"

    try:
        program = program[:-1]  # remove EOF
        # check structure
        for ind, token in enumerate(program):
            if ind % 4 == 0:
                if token.strip("(") not in all_ops:
                    return 1, "n/a"
            if (ind + 1) % 4 == 0:
                if token != ")":
                    return 1, "n/a"

        program = "|".join(program)
        steps = program.split(")")[:-1]

        res_dict = {}

        for ind, step in enumerate(steps):
            step = step.strip()

            if len(step.split("(")) > 2:
                invalid_flag = 1
                break
            op = step.split("(")[0].strip("|").strip()
            args = step.split("(")[1].strip("|").strip()

            arg1 = args.split("|")[0].strip()
            arg2 = args.split("|")[1].strip()

            if op == "add" or op == "subtract" or op == "multiply" or op == "divide" or op == "exp" or op == "greater":

                if "#" in arg1:
                    arg1 = res_dict[int(arg1.replace("#", ""))]
                else:
                    arg1 = str_to_num(arg1)
                    if arg1 == "n/a":
                        invalid_flag = 1
                        break

                if "#" in arg2:
                    arg2 = res_dict[int(arg2.replace("#", ""))]
                else:
                    arg2 = str_to_num(arg2)
                    if arg2 == "n/a":
                        invalid_flag = 1
                        break

                if op == "add":
                    this_res = arg1 + arg2
                elif op == "subtract":
                    this_res = arg1 - arg2
                elif op == "multiply":
                    this_res = arg1 * arg2
                elif op == "divide":
                    this_res = arg1 / arg2
                elif op == "exp":
                    this_res = arg1 ** arg2
                elif op == "greater":
                    this_res = "yes" if arg1 > arg2 else "no"

                res_dict[ind] = this_res

            elif "table" in op:
                table_dict = {}
                for row in table:
                    table_dict[row[0]] = row[1:]

                if "#" in arg1:
                    arg1 = res_dict[int(arg1.replace("#", ""))]
                else:
                    if arg1 not in table_dict:
                        invalid_flag = 1
                        break

                    cal_row = table_dict[arg1]
                    num_row = process_row(cal_row)

                if num_row == "n/a":
                    invalid_flag = 1
                    break
                if op == "table_max":
                    this_res = max(num_row)
                elif op == "table_min":
                    this_res = min(num_row)
                elif op == "table_sum":
                    this_res = sum(num_row)
                elif op == "table_average":
                    this_res = sum(num_row) / len(num_row)

                res_dict[ind] = this_res
        if this_res != "yes" and this_res != "no" and this_res != "n/a":
            this_res = round(this_res, 5)

    except:
        invalid_flag = 1

    return invalid_flag, this_res


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


def process_row(row_in):
    row_out = []
    invalid_flag = 0

    for num in row_in:
        num = num.replace("$", "").strip()
        num = num.split("(")[0].strip()

        num = str_to_num(num)

        if num == "n/a":
            invalid_flag = 1
            break

        row_out.append(num)

    if invalid_flag:
        return "n/a"

    return row_out


def get_res(program, table):
    pred_text = program.replace(' ', '')
    pred_text = pred_text.replace('),', ')|')
    pred_program = []
    for p_t in pred_text.split('|'):
        invalid_flag, p_t_l = get_program_from_text(p_t)
        if invalid_flag == 0:
            for i in p_t_l:
                pred_program.append(i)
    pred_program.append('EOF')
    invalid_flag, exe_res = eval_program(pred_program, table)
    return invalid_flag, exe_res
'''
a = 'Depreciation and amortization expense included as a charge to income was $66,082 and $67,107 for'
print(re.findall(r"\d+\.?\d*", a))
'''