import os
import openai
import json
import re
import random
from time import sleep
import traceback
import sys
#proxies = 
openai.proxy = {'http': "http://127.0.0.1:7890",'https': "http://127.0.0.1:7890"}
###上面两行是为了在中国用，VPN相关
openai.api_key = "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"
one_shot_table = '''
- | number of shares ( in thousands ) | weighted average grant date fair value ( per share )
restricted stock and restricted stock units at beginning of year | 407 | $ 9.84
granted | 607 | 18.13
vested | -134 ( 134 ) | 10.88
forfeited | -9 ( 9 ) | 13.72
restricted stock and restricted stock units at end of year | 871 | $ 15.76
Please randomly generate a piece of irrelevant financial statement text based on the above data.
during the year ended march 31 , 2012 , the company has recorded $ 3.3 million in stock-based compensation expense for equity awards in which the prescribed performance milestones have been achieved or are probable of being achieved .
'''
one_shot_text = '''
in millions | 2012 | 2011 | 2010
totaled | $ 3050 | $ 4000 | $ 4020
Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.
annual sales of printing papers and graphic arts supplies and equipment totaled $ 3050 million in 2012 compared with $ 4000 million in 2011 and $ 4020 million in 2010 , reflecting declining demand and the exiting of unprofitable businesses .
'''
few_shot_table = '''
- | number of shares ( in thousands ) | weighted average grant date fair value ( per share )
restricted stock and restricted stock units at beginning of year | 407 | $ 9.84
granted | 607 | 18.13
vested | -134 ( 134 ) | 10.88
forfeited | -9 ( 9 ) | 13.72
restricted stock and restricted stock units at end of year | 871 | $ 15.76
Please randomly generate a piece of irrelevant financial statement text based on the above data.
during the year ended march 31 , 2012 , the company has recorded $ 3.3 million in stock-based compensation expense for equity awards in which the prescribed performance milestones have been achieved or are probable of being achieved .

- | 2013 | 2014 | 2015 | 2016 | 2017
masco | $ 138.48 | $ 155.26 | $ 200.79 | $ 227.08 | $ 318.46
s&p 500 index | $ 132.04 | $ 149.89 | $ 151.94 | $ 169.82 | $ 206.49
s&p industrials index | $ 140.18 | $ 153.73 | $ 149.83 | $ 177.65 | $ 214.55
s&p consumer durables & apparel index | $ 135.84 | $ 148.31 | $ 147.23 | $ 138.82 | $ 164.39
Please randomly generate a piece of irrelevant financial statement text based on the above data.
performance graph the table below compares the cumulative total shareholder return on our common stock with the cumulative total return of ( i ) the standard & poor's 500 composite stock index ( \"s&p 500 index\" ) , ( ii ) the standard & poor's industrials index ( \"s&p industrials index\" ) and ( iii ) the standard & poor's consumer durables & apparel index ( \"s&p consumer durables & apparel index\" ) , from december 31 , 2012 through december 31 , 2017 , when the closing price of our common stock was $ 43.94 . the graph assumes investments of $ 100 on december 31 , 2012 in our common stock and in each of the three indices and the reinvestment of dividends . the table below sets forth the value , as of december 31 for each of the years indicated , of a $ 100 investment made on december 31 , 2012 in each of our common stock , the s&p 500 index , the s&p industrials index and the s&p consumer durables & apparel index and includes the reinvestment of dividends. . $ 50.00 $ 100.00 $ 150.00 $ 200.00 $ 250.00 $ 300.00 $ 350.00 masco s&p 500 index s&p industrials index s&p consumer durables & apparel index .

( in thousands ) | at december 31 , 2016 | at december 31 , 2015 | at december 31 , 2014 | at december 31 , 2013 | at december 31 , 2012
cash and cash equivalents | $ 250470 | $ 129852 | $ 593175 | $ 347489 | $ 341841
working capital ( 1 ) | 1279337 | 1019953 | 1127772 | 702181 | 651370
inventories | 917491 | 783031 | 536714 | 469006 | 319286
total assets | 3644331 | 2865970 | 2092428 | 1576369 | 1155052
total debt including current maturities | 817388 | 666070 | 281546 | 151551 | 59858
total stockholders 2019 equity | $ 2030900 | $ 1668222 | $ 1350300 | $ 1053354 | $ 816922
Please randomly generate a piece of irrelevant financial statement text based on the above data.
other items on our consolidated financial statements have been appropriately adjusted from the amounts provided in the earnings release , including a reduction of our full year 2016 gross profit and income from operations by $ 2.9 million , and a reduction of net income by $ 1.7 million. . ( 1 ) working capital is defined as current assets minus current liabilities.

company/index | baseperiod 12/31/05 | baseperiod 12/31/06 | baseperiod 12/31/07 | baseperiod 12/31/08 | baseperiod 12/31/09 | 12/31/10
a o smith corp | 100.0 | 108.7 | 103.3 | 88.8 | 133.6 | 178.8
s&p small cap 600 index | 100.0 | 115.1 | 114.8 | 78.1 | 98.0 | 123.8
russell 1000 index | 100.0 | 115.5 | 122.1 | 76.2 | 97.9 | 113.6
Please randomly generate a piece of irrelevant financial statement text based on the above data.
the graph below shows a five-year comparison of the cumulative shareholder return on the company's common stock with the cumulative total return of the s&p small cap 600 index and the russell 1000 index , both of which are published indices . comparison of five-year cumulative total return from december 31 , 2005 to december 31 , 2010 assumes $ 100 invested with reinvestment of dividends period indexed returns . 2005 2006 2007 2008 2009 2010 smith ( a o ) corp s&p smallcap 600 index russell 1000 index . 
'''

few_shot_text = '''
in millions | 2012 | 2011 | 2010
totaled | $ 3050 | $ 4000 | $ 4020
Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.
annual sales of printing papers and graphic arts supplies and equipment totaled $ 3050 million in 2012 compared with $ 4000 million in 2011 and $ 4020 million in 2010 , reflecting declining demand and the exiting of unprofitable businesses .

in millions | 2003 | 2002 | 2001
the domestic utility companies | $ 1.5 | $ 2.1 | $ 4
the non-utility nuclear business | $ 3 | $ 3 | $ 2
Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.
part i item 1 entergy corporation , domestic utility companies , and system energy research spending entergy is a member of the electric power research institute ( epri ) . epri conducts a broad range of research in major technical fields related to the electric utility industry . entergy participates in various epri projects based on entergy's needs and available resources . the domestic utility companies contributed $ 1.5 million in 2003 , $ 2.1 million in 2002 , and $ 4 million in 2001 to epri . the non-utility nuclear business contributed $ 3 million in 2003 and 2002 and $ 2 million in 2001 to epri . employees employees are an integral part of entergy's commitment to serving its customers . as of december 31 , 2003 , entergy employed 14773 people. . approximately 4900 employees are represented by the international brotherhood of electrical workers union , the utility workers union of america , and the international brotherhood of teamsters union.

year| 2017 | 2016 | 2015 |
shares |  total compensation expense for stock options and incentive shares|115 | 159 | 30
included in discontinued operations | 5 | 14 | 6
Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.
total compensation expense for stock options and incentive shares was $ 115 , $ 159 and $ 30 for 2017 , 2016 and 2015 , respectively , of which $ 5 , $ 14 and $ 6 was included in discontinued operations . the decrease in expense for 2017 reflects the impact of changes in the stock price . the increase in expense for 2016 reflects an increasing stock price in the current year compared with a decreasing price in 2015 , and overlap of awards . income tax benefits recognized in the income statement for these compensation arrangements during 2017 , 2016 and 2015 were $ 33 , $ 45 and $ 2 , respectively . as of september 30 , 2017 , total unrecognized compensation expense related to unvested shares awarded under these plans was $ 149 , which is expected to be recognized over a weighted-average period of 1.5 years . in addition to the employee stock option and incentive shares plans , in 2017 the company awarded 17984 shares of restricted stock and 2248 restricted stock units under the restricted stock plan for non-management directors . as of september 30 , 2017 , 174335 shares were available for issuance under this plan.

year| 2015 | 2014 | 2013 |
issued to employees | 411636 | 439000 | 556000
compensation expense recognized | $ 9 million | $ 7 million | $ 6 million
Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.
employee share purchase plan united states the company has an employee share purchase plan that provides for the purchase of a maximum of 7.5 million shares of the company's ordinary shares by eligible u.s . the company's ordinary shares were purchased at 6-month intervals at 85% ( 85 % ) of the lower of the fair market value of the ordinary shares on the first or last day of each 6-month period . in 2015 , 2014 , and 2013 , 411636 shares , 439000 shares and 556000 shares , respectively , were issued to employees under the plan . compensation expense recognized was $ 9 million in 2015 , $ 7 million in 2014 , and $ 6 million in 2013 . 
'''
class GenerateData:
    def __init__(self, variable_list, time):
        self.variable_list = variable_list
        self.variable_list_all=['income', 'expenses', 'revenue', 'business_cost', 'cost', 'gross_profit', 'expense', 'gross_margins', 'tax', 'asset_impairment_loss', 'credit_impairment_loss', 'fair_value_variation', 'return_on_investment', 'investment_loss', 'other_income', 'operating_profit', 'non_operating_income', 'non_operating_expenses', 'total_profits', 'income_tax_expense', 'current_income_tax', 'deffered_income_tax', 'taxable_income', 'income_tax_rate', 'original_value', 'net_salvage', 'expected_useful_life', 'annual_depreciation_rate', 'net_salvage_rate', 'expected_workload', 'workload', 'expected_uesful_life', 'depreciation_amortization', 'book_balance', 'impairment_provision', 'net_book_value', 'face_amount_of_notes_receivable', 'interest_on_notes_receivable', 'maturity_of_notes_receivable', 'discount_rate', 'discount_period', 'maturity_value_of_notes_receivable', 'discount_interest']
        self.time_begin = 0
        self.time_end = 0
        self.time = time
        self.time_list = []
        self.sleeptime = 3
        self.have_out=True
        self.few_shot = False
        ###休眠等待时间
        self.text = ''
        self.table = []
        self.table_text = ''
        self.table_value = ''
        self.table_value_all = ''
        self.text_value =''
        self.run()
        
    def generate_time(self):
        time_1 = random.randint(int(self.time[0]), int(self.time[1]))
        time_2 = random.randint(int(self.time[0]), int(self.time[1]))
        if(time_1==time_2):
            time_1=time_1-1
        self.time_begin = min(time_1,time_2)
        self.time_end = max(time_1,time_2)
        if((self.time_end-self.time_begin)>4):
            self.time_end=random.randint(self.time_begin+1,self.time_begin+4)

        self.time_list = []
        for i in range(self.time_begin, self.time_end+1):
            self.time_list.append(i)



    def generate_table(self):
        
        temp_text = 'Please randomly generate a piece of financial statement table snippet with '
        for i in range(0, len(self.variable_list)):
            temp_text += self.variable_list[i]
            if i != len(self.variable_list) - 1:
                temp_text += ', '

        temp_text += ' from '+str(self.time_begin)+' to '+str(self.time_end)+' in json format such as {\"xxxx\": {\"2017\": 190000\n   \"2018\": 295000\n}\n \"xxxx\": {\"2017\": 10000\n   \"2018\": 70000\n}\n }.'

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": temp_text}
            ]
        )
        print(self.table_value_all)
        self.table_value_all = completion.choices[0].message
        self.table_value = completion.choices[0].message.content
        self.table_value = self.table_value.lower()
        
        #去除数字内部逗号
        p = re.compile(r'\d,\d')
        while 1:
            m = p.search(self.table_value)
            if m:
                mm = m.group()
                self.table_value = self.table_value.replace(mm,mm.replace(',',''))
            else:
                break

        self.table_value_all.content=self.table_value

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
        
        temp_text = self.table_value_all.content+'Please randomly generate a piece of irrelevant financial statement text based on the above data.'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": few_shot_table},
                {"role": "user", "content": temp_text}
            ],
        )

        self.table_text = completion.choices[0].message.content


    def generate_text(self):
        temp_text = 'Please randomly generate a piece of financial statement table snippet with '
        for i in range(0, len(self.variable_list)):
            temp_text += self.variable_list[i]
            if i != len(self.variable_list) - 1:
                temp_text += ', '

        temp_text += ' from '+str(self.time_begin)+' to '+str(self.time_end)+' in json format such as {\"xxxx\": {\"2017\": 190000\n   \"2018\": 295000\n}\n \"xxxx\": {\"2017\": 10000\n   \"2018\": 70000\n}\n }.'


        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": temp_text}
            ]
        )
        self.text = completion.choices[0].message
        self.text_value = completion.choices[0].message.content
        self.text_value = self.text_value.lower()
        
        #去除数字内部逗号
        p = re.compile(r'\d,\d')
        while 1:
            m = p.search(self.text_value)
            if m:
                mm = m.group()
                self.text_value = self.text_value.replace(mm,mm.replace(',',''))
            else:
                break

        self.text.content=self.text_value
        self.text_value = json.loads(self.text_value)

        for j in range(0, len(self.variable_list)):
            a=self.text_value[str(self.variable_list[j])]
            for i in range(0, len(self.time_list)):
                b=int(a[str(self.time_list[i])])
                b=b+1

        temp_text = self.text.content + 'Please randomly generate a piece of financial statement text based on the above data, which must contain all the data.'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": few_shot_text},
                {"role": "user", "content": temp_text}
            ],
        )

        self.text_text = completion.choices[0].message.content
        self.conversion()


    def get_text_table(self):
        var= random.randint(2, 3)
        non_variable = random.sample(self.variable_list_all,var)
        temp_text = 'Please only randomly generate a piece of financial statement table snippet with '
        for i in range(0, len(non_variable)):
            temp_text += non_variable[i]
            if i != len(non_variable) - 1:
                temp_text += ', '
        temp_text += ' in array format such as [["year","xxxx","xxxx"],["2013",150000,12000],["2014",180000,18000],].Do not output anything other than an array.'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                self.text,
                {"role": "user", "content": temp_text}
            ]
        )
        
        self.text_table = completion.choices[0].message.content
        


    def conversion(self):
        #处理million
        p = re.compile(r'\d,\d')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                self.text_text = self.text_text.replace(mm,mm.replace(',',''))
            else:
                break
        p = re.compile(r'\d.\d\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.','')
                m2 = m1.replace(' ','')
                self.text_text = self.text_text.replace(mm,m2.replace('million','0000'))
            else:
                break
        p = re.compile(r'\d.\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace('.','')
                m2 = m1.replace(' ','')
                self.text_text = self.text_text.replace(mm,m2.replace('million','00000'))
            else:
                break
    
        p = re.compile(r'\d million')
        while 1:
            m = p.search(self.text_text)
            if m:
                mm = m.group()
                m1 = mm.replace(' ','')
                self.text_text = self.text_text.replace(mm,m1.replace('million','000000'))
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

    def run(self):
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
            self.have_out=False
                    
            




with open('data/all_function.json','r', encoding='utf-8') as file:
    file_test = json.load(file)
#输入路径
num_formula = 5
#每个公式生成几个
file_text_new = []
file_table_new = []
for temp in file_test:
    table_variables=temp['variables']
    print(table_variables)
    #可删，这用来看跑到哪个公式了
    for i in range(0,len(table_variables)):
        table_variables[i]=table_variables[i].replace('*n-1','')
        table_variables[i]=table_variables[i].replace('*n','')
    table_variables = list(set(table_variables))     
    
    for i in range(0,num_formula):
        g = GenerateData(table_variables, ['2010', '2022'])
        if g.have_out:
            table_info={"table":g.table,"text":g.table_text,"table_value":g.table_value}
            text_info={"table":g.text_table,"text":g.text_text,"text_value":g.text_value}
            file_table_new.append(table_info)
            file_text_new.append(text_info)
         
with open('data/table.json','w', encoding='utf-8') as f:
    json.dump(file_table_new, f,indent=4)  

with open('data/text.json','w', encoding='utf-8') as f:
    json.dump(file_text_new, f,indent=4)  
#两个输出路径