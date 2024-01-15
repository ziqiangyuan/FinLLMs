import os
import openai
import json
import re
import random
from time import sleep
from tqdm import tqdm
import traceback
from config import params
import sys
proxies = {'http': "http://127.0.0.1:7890",'https': "http://127.0.0.1:7890"}
openai.proxy = proxies
###上面两行是为了在中国用，VPN相关
openai.api_key = params.api_key

variable_list_all = ['income', 'expenses', 'revenue', 'business_cost', 'cost', 'gross_profit', 'expense',
                                  'gross_margins', 'tax', 'asset_impairment_loss', 'credit_impairment_loss',
                                  'fair_value_variation', 'return_on_investment', 'investment_loss', 'other_income',
                                  'operating_profit', 'non_operating_income', 'non_operating_expenses', 'total_profits',
                                  'income_tax_expense', 'current_income_tax', 'deffered_income_tax', 'taxable_income',
                                  'income_tax_rate', 'original_value', 'net_salvage', 'expected_useful_life',
                                  'annual_depreciation_rate', 'net_salvage_rate', 'expected_workload', 'workload',
                                  'expected_uesful_life', 'depreciation_amortization', 'book_balance',
                                  'impairment_provision', 'net_book_value', 'face_amount_of_notes_receivable',
                                  'interest_on_notes_receivable', 'maturity_of_notes_receivable', 'discount_rate',
                                  'discount_period', 'maturity_value_of_notes_receivable', 'discount_interest']
class GenerateData:
    def __init__(self, variable_list, time, max_retry):
        self.error_flag = False
        self.variable_list = variable_list
        # 用于随生成无关表格
        self.variable_list_all = ['income', 'expenses', 'revenue', 'business_cost', 'cost', 'gross_profit', 'expense',
                                  'gross_margins', 'tax', 'asset_impairment_loss', 'credit_impairment_loss',
                                  'fair_value_variation', 'return_on_investment', 'investment_loss', 'other_income',
                                  'operating_profit', 'non_operating_income', 'non_operating_expenses', 'total_profits',
                                  'income_tax_expense', 'current_income_tax', 'deffered_income_tax', 'taxable_income',
                                  'income_tax_rate', 'original_value', 'net_salvage', 'expected_useful_life',
                                  'annual_depreciation_rate', 'net_salvage_rate', 'expected_workload', 'workload',
                                  'expected_uesful_life', 'depreciation_amortization', 'book_balance',
                                  'impairment_provision', 'net_book_value', 'face_amount_of_notes_receivable',
                                  'interest_on_notes_receivable', 'maturity_of_notes_receivable', 'discount_rate',
                                  'discount_period', 'maturity_value_of_notes_receivable', 'discount_interest']
        self.time_begin = 0
        self.time_end = 0
        self.time = time
        self.time_list = []
        self.sleeptime = 2
        ###休眠等待时间
        self.text = ''
        self.table = []
        self.table_text = ''
        self.table_value = ''
        self.table_value_all = ''
        self.text_value = ''
        self.one_shot_table=''
        self.one_shot_text=''
        self.run(max_retry)

    def get_shot(self):
        with open('data/train.json','r', encoding='utf-8') as file:
            file_train = json.load(file)
        i=random.randint(1, len(file_train))
        train=file_train[i]
        self.one_shot_table=str(train['table'])
        self.one_shot_text=''.join(train['pre_text'])+''.join(train['post_text'])
        

    def generate_time(self):
        time_1 = random.randint(int(self.time[0]), int(self.time[1]))
        time_2 = random.randint(int(self.time[0]), int(self.time[1]))
        if time_1 == time_2:
            time_1 = time_1 - 1
        if time_1 - time_2 < 2:
            time_1 = time_1 - 1
        self.time_begin = min(time_1, time_2)
        self.time_end = max(time_1, time_2)
        if self.time_end - self.time_begin > 4:
            self.time_end = random.randint(self.time_begin + 1, self.time_begin + 4)

        self.time_list = []
        for i in range(self.time_begin, self.time_end + 1):
            self.time_list.append(i)

    def generate_table(self):

        temp_text = 'Please randomly generate a piece of financial statement table snippet with '
        for i in range(0, len(self.variable_list)):
            temp_text += self.variable_list[i]
            if i != len(self.variable_list) - 1:
                temp_text += ', '

        temp_text += ' from ' + str(self.time_begin) + ' to ' + str(
            self.time_end) + ' in json format such as {\"xxxx\": {\"2017\": 190000\n   \"2018\": 295000\n}\n \"xxxx\": {\"2017\": 10000\n   \"2018\": 70000\n}\n }. Please do not output other content except json.'

        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user",
                 "content": temp_text}
            ]
        )
        self.table_value_all = completion.choices[0].message
        self.table_value = completion.choices[0].message.content
        #print(self.table_value)
        self.table_value = self.table_value.strip('`')
        self.table_value = self.table_value.strip('json')
        #print(self.table_value)

        self.table_value = self.table_value.lower()

        # 去除数字内部逗号
        p = re.compile(r'\d,\d')
        while 1:
            m = p.search(self.table_value)
            if m:
                mm = m.group()
                self.table_value = self.table_value.replace(mm, mm.replace(',', ''))
            else:
                break

        self.table_value_all.content = self.table_value

        self.table_value = json.loads(self.table_value)

        self.table = []
        table1 = ['year']
        table2 = []
        for key in self.table_value:
            table1.append(key)
        self.table.append(table1)
        for i in range(0, len(self.time_list)):
            table2.append(int(self.time_list[i]))
            for j in range(1, len(table1)):
                a=self.table_value[str(table1[j])]
                table2.append(int(a[str(self.time_list[i])]))
            self.table.append(table2)
            table2 = []


    def get_table_text(self):

        temp_text=''
        for i in range(4):
            self.get_shot()
            temp_text = temp_text+self.one_shot_table+'\nPlease randomly generate a piece of irrelevant financial statement text based on the above data.\n'+self.one_shot_text+'\n'
        
        temp_text =temp_text+str(self.table)+'\nPlease randomly generate a piece of irrelevant financial statement text based on the above data.\n'
        #print(temp_text)
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": temp_text}
            ],
        )


        self.table_text = completion.choices[0].message.content

    def generate_text(self):
        
        self.text = self.table_value_all
        self.text_value = self.table_value
        temp_text=''
        for i in range(4):
            self.get_shot()
            temp_text = temp_text+self.one_shot_table+'\nPlease randomly generate a piece of financial statement text based on the above data, which must contain all the data.\n'+self.one_shot_text+'\n'
        
        
        temp_text=temp_text+str(self.table)+'\nPlease randomly generate a piece of financial statement text based on the above data, which must contain all the data.\n'
        #print(temp_text)
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": temp_text}
            ],
        )

        self.text_text = completion.choices[0].message.content
        self.conversion()

    def get_text_table(self):
        var = random.randint(2, 3)
        non_variable = random.sample(self.variable_list_all, var)
        temp_text = 'Please only randomly generate a piece of financial statement table snippet with '
        for i in range(0, len(non_variable)):
            temp_text += non_variable[i]
            if i != len(non_variable) - 1:
                temp_text += ', '
        temp_text += ' in array format such as [["year","xxxx","xxxx"],["2013",150000,12000],["2014",180000,18000],].Do not output anything other than an array.'
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                self.text,
                {"role": "user", "content": temp_text}
            ]
        )

        self.text_table = completion.choices[0].message.content

    def conversion(self):
        # 处理million
        p = re.compile(r'\d,\d')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                self.text_text = self.text_text.replace(mm, mm.replace(',', ''))
            else:
                break
        p = re.compile(r'\d.\d\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.', '')
                m2 = m1.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m2.replace('million', '0000'))
            else:
                break
        p = re.compile(r'\d.\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.', '')
                m2 = m1.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m2.replace('million', '00000'))
            else:
                break

        p = re.compile(r'\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m1.replace('million', '000000'))
            else:
                break
        p = re.compile(r'\d.\d\d billion')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.', '')
                m2 = m1.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m2.replace('billion', '0000000'))
            else:
                break
        p = re.compile(r'\d.\d billion')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.', '')
                m2 = m1.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m2.replace('billion', '00000000'))
            else:
                break

        p = re.compile(r'\d billion')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace(' ', '')
                self.text_text = self.text_text.replace(mm, m1.replace('billion', '000000000'))
            else:
                break

    def run(self, max_retry=5):
        i = 0
        j = 0
        while(i<2 and j<6):
            if i==0:
                try:
                    self.generate_time()
                    self.generate_table()
                    sleep(self.sleeptime)
                    self.get_table_text()
                    sleep(self.sleeptime)
                except Exception as e:
                    print(e)
                    print(sys.exc_info()) 
                    print('An error occurred,automatically retry after '+str(self.sleeptime)+' seconds')
                    sleep(self.sleeptime)
                    j = j+1
                    continue
                else:
                    i = i+1
                    
            else :
                try:
                    self.generate_text()
                    sleep(self.sleeptime)
                    self.get_text_table()
                    sleep(self.sleeptime)
                    self.error_flag = False
                    #print('yes')
                except Exception as e:
                    print(e)
                    print(sys.exc_info()) 
                    print('An error occurred,automatically retry after '+str(self.sleeptime)+' seconds')
                    sleep(self.sleeptime)
                    j = j+1
                    continue
                else:
                    i = i+1
        if j>= 6:
            self.error_flag=True
        # while i<max_retry:
        #     try:
        #         self.generate_time()
        #         self.generate_table()
        #         sleep(self.sleeptime)
        #         self.get_table_text()
        #         sleep(self.sleeptime)
        #         self.generate_text()
        #         sleep(self.sleeptime)
        #         self.get_text_table()
        #         sleep(self.sleeptime)
        #         print('yes')
        #         i+=1
        #         self.error_flag = False
        #     except Exception as e:
        #         print(e)
        #         print(sys.exc_info()) 
        #         print('An error occurred,automatically retry after ' + str(self.sleeptime) + ' seconds')
        #         sleep(self.sleeptime)
        #         self.error_flag = True


def generate(fun_path='data/all_function.json',
             num_formula=5,
             begin_time=2010,
             end_time=2022,
             output_table_path='data/table.json',
             output_text_path='data/text.json',
             max_retry=5, ):
    with open(fun_path, 'r', encoding='utf-8') as file:
        file_test = json.load(file)
    formula = []
    for f in file_test:
        if '*n-1' not in f['target']:
            formula.append(f)
    random.shuffle(formula)
    print(formula)
    file_text_new = []
    file_table_new = []
    k = 0
    
    for temp in tqdm(formula):
        '''
        if k > 30:
            break
        k += 1
        '''
        
        table_variables = temp['variables']
        print(table_variables)
        for i in range(0, len(table_variables)):
            table_variables[i] = table_variables[i].replace('*n-1', '')
            table_variables[i] = table_variables[i].replace('*n', '')
        table_variables = list(set(table_variables))
        print(table_variables)
        #print(num_formula)
        for i in range(0,num_formula):
            g = GenerateData(table_variables, [begin_time, end_time], max_retry)
            #print(i)
            if g.error_flag:
                continue
            g.table = add_noise_in_table(g.table)
            table_info = {"variables": table_variables, "table": g.table, "text": g.table_text, "table_value": g.table_value}
            text_info = {"variables": table_variables, "table": g.text_table, "text": g.text_text, "text_value": g.text_value}

            file_table_new.append(table_info)
            file_text_new.append(text_info)

    with open(output_table_path, 'w', encoding='utf-8') as f:
        json.dump(file_table_new, f, indent=4)

    with open(output_text_path, 'w', encoding='utf-8') as f:
        json.dump(file_text_new, f, indent=4)

def add_noise_in_table(table, num=2):
    variables = table[0][1:]
    for i in range(num):
        v = random.sample(variable_list_all, 1)
        while(v[0] in variables):
            v = random.sample(variable_list_all, 1)
        for (index, t) in enumerate(table):
            if index == 0:
                table[index].append(v[0])
            else:
                value = random.randint(0, 100000)
                table[index].append(value)
    return table


'''
with open('./all_function.json','r', encoding='utf-8') as file:
    file_test = json.load(file)
#输入路径
num_formula = 2
#每个公式生成几个
file_text_new = []
file_table_new = []
for temp in file_test:
    table_variables=temp['variables']
    print(table_variables)
    #可删，这用来看跑到哪个公式了
    for i in range(0, len(table_variables)):
        table_variables[i] = table_variables[i].replace('*n-1','')
        table_variables[i]=table_variables[i].replace('*n','')
    table_variables = list(set(table_variables))     
    
    for i in range(0,num_formula):
        g = GenerateData(table_variables, ['2010', '2022'])

        table_info={"table":g.table,"text":g.table_text,"table_value":g.table_value}
        text_info={"table":g.text_table,"text":g.text_text,"text_value":g.text_value}

        file_table_new.append(table_info)
        file_text_new.append(text_info)
         
with open('./table.json','w', encoding='utf-8') as f:
    json.dump(file_table_new, f,indent=4)  

with open('./text.json','w', encoding='utf-8') as f:
    json.dump(file_text_new, f,indent=4)  
#两个输出路径
'''
