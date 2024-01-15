import re
from utils.general_utils import *
#from postfix import *
class Qa:
    def __init__(self, question, program, exe_ans, answer, gold_inds, scale):
        self.question = question
        self.program = program
        self.exe_ans = exe_ans
        self.answer = answer
        self.gold_inds = gold_inds
        self.scale = scale

    def get_dict(self):
        res = {'question': self.question, 'program': self.program, 'exe_ans': self.exe_ans, 'answer': self.answer,
               'gold_inds': self.gold_inds}
        return res

class FinQA:
    def __init__(self, this_id, pre_text, table, post_text, Qa):
        self.gold_index = {}
        self.flag = False
        self.id = this_id
        self.pre_text = pre_text
        self.table = table
        self.post_text = post_text
        self.qa = Qa

    def get_dict(self):
        res = {'id': self.id, 'pre_text': self.pre_text, 'table': self.table, 'post_text': self.post_text, 'qa': self.qa.get_dict()}
        return res

class JsonFunction:
    def __init__(self, json_obj=None, target=None, variables=None, formula=None):
        self.variable_without_time = []
        if json_obj is not None:
            self.variables = json_obj['variable']
            self.formula = json_obj['formula']
        else:
            self.variables = variables
            self.formula = formula
        self.program = ''
        for v in self.variables:
            self.variable_without_time.append(v.replace('*n-1', '').replace('*n', ''))
        #print(self.variable_without_time)
        for (index, x) in enumerate(self.formula):
            self.program += x
            if index % 3 == 0:
                self.program += '('
            elif index % 3 == 1:
                self.program += ', '
            elif index % 3 == 2:
                self.program += ')'
                if index != len(self.formula) - 1:
                    self.program += ', '
        self.target = target

