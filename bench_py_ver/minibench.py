from ctypes import sizeof
from numpy import polyfit
import numpy as np
import os
import copy

class Minibench:
    def __init__(self,my_cmd_papi) -> None:
        self.env_var = 'PAPI_TOT_CYC:PAPI_TOT_INS:PAPI_LST_INS:PAPI_L2_DCA:PAPI_BR_CN:PAPI_BR_MSP'
        self.env_num = 6
        self.add = 0
        self.pause = 0
        self.nop = 0
        self.div = 0
        self.tempcode = './temp_minibench.c'
        self.cmd = "gcc " + self.tempcode + my_cmd_papi + "-o " + "temp_minibench"
        self.l1_cache_size = 0
        self.l2_cache_size = 0
        self.cache_line_size = 0
        self.int_size = 4
        self.get_cache_info()
    
    def get_cache_info(self):
        f = os.popen('cat /sys/devices/system/cpu/cpu0/cache/index0/size')
        r = f.readline()
        if r[-2] == 'K':
            self.l1_cache_size = int(r[:-2])*1024
        f = os.popen('cat /sys/devices/system/cpu/cpu0/cache/index2/size')
        r = f.readline()
        if r[-2] == 'K':
            self.l2_cache_size = int(r[:-2])*1024
        f = os.popen('cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size')
        self.cache_line_size = int(f.readline()[:-1])

    def fit(self):
        l = []
        l.append(self.add_fit())
        l.append(self.add2_fit())
        l.append(self.div_fit())
        l.append(self.div2_fit())
        l.append(self.cycle1_fit())
        l.append(self.cycle2_fit())
        l.append(self.msp1_fit())
        l.append(self.msp2_fit())
        l.append(self.l1cache_ins_fit())
        l.append(self.l1cache_cyc_fit())
        l.append(self.l1cache_lst_fit())
        cache_intercept = [self.l1cache_ins_fit(3),self.l1cache_cyc_fit(3),self.l1cache_lst_fit(3)]
        #print(cache_intercept)
        for i in range(3):
            for j in range(len(cache_intercept[0])):
                cache_intercept[i][j] = 3*(cache_intercept[i][j] - l[-3+i][j])
        l = list(map(list, zip(*l)))
        return l,cache_intercept


    def get_metrics(self,s):
        env0 = self.env_var[:38]
        env1 = self.env_var[39:]
        metric0 = self.get_temp_code(s,env0)
        metric1 = []
        if env1:metric1 = self.get_temp_code(s,env1)
        return metric0 + metric1


    def get_temp_code(self,s,env):
        with open(self.tempcode,'w') as f:
            with open('./fstart.txt','r') as start:
                f.writelines(start.readlines())

            f.write("void "+'block'+'(){\n')
            f.write("int *a=(int*)malloc(sizeof(int)*100000000);\n")
            f.write("\tpapi_retval = PAPI_start(EventSet);\n")
            f.write(s)
            f.write("\tpapi_retval=PAPI_read(EventSet, values[0]);\n")
            f.write("\tfor (int i = 0; i < event_count; i++) printf(\"%lld \", values[0][i]);\n")
            f.write('}\n')

            with open('./fend.txt','r') as end:
                f.writelines(end.readlines())
            f.write('block'+"();\n}\n")
        os.system(self.cmd)
        os.environ["PAPI_MON_EVENTS"] = env
        f = os.popen("./temp_minibench")
        metric = f.readline().strip().split(" ")
        #print(metric)
        return [int(i) for i in metric]

    def add_fit(self):
        l = []
        t = 10
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\tlong i1=12345;long i2=67890, i3=54321,i4=100,i5=100,i6=100;\n\tfor (register long i = 0;i<{t};i++) \n'
            s += '{i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;}'
            metric = self.get_metrics(s)
            metric[1] -= t*3
            metric[0] -= t
            metric[-2] -= t
            metric[-1] = 0.0
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0]/100)
        return l

    def add2_fit(self):
        l = []
        t = 10
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\tlong i1=12345;register long i2=67890, i3=54321,i4=100,i5=100,i6=100,i7=10000,i8,i9,i10;\n\tfor (register long i = 0;i<{t};i++) \n'
            #s += '{i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;i1 = i2 + i3;}'
            s += '{i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;i1=i2+i3+i4+i5+i6;}'
            metric = self.get_metrics(s)
            metric[1] -= t*3
            metric[0] -= t
            metric[-2] -= t
            metric[-1] = 0.0
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0]/100)
        return l

    def div_fit(self):
        l = []
        t = 10
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\tdouble d1=12345678;double d2=98,d3=90;\n\tfor (register long i = 0;i<{t};i++) \n'
            s += '{d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;}'
            #s += '{d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;d1 = d3 / d2;}'
            metric = self.get_metrics(s)
            metric[1] -= t*3
            metric[0] -= t
            metric[-2] -= t
            metric[-1] = 0.0
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0]/100)
        return l

    def div2_fit(self):
        l = []
        t = 10
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\tdouble d1=12345678;register long d2=98,d3=90,d4=111,d5=222,d6=333;\n\tfor (register long i = 0;i<{t};i++) \n'
            #s += '{d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;d1 = d1 / d2;}'
            s += '{d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;d1=d2/d3/d4/d5/d6;}'
            metric = self.get_metrics(s)
            metric[1] -= t*3
            metric[0] -= t
            metric[-2] -= t
            metric[-1] = 0.0
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0]/100)
        return l

    def cycle1_fit(self):
        l = []
        t = 1000
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\t\n\tfor (long i = 0;i<{t};i++) \n'
            s += '{ }'
            metric = self.get_metrics(s)
            #metric[1] -= t*3
            #metric[0] -= t
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0])
        return l

    def cycle2_fit(self):
        l = []
        t = 1000
        x = []
        y = [[] for i in range(self.env_num)]
        for i in range(4):
            t*=10
            x.append(t)
            s = f'\t\n\tfor (register long i = 0;i<{t};i++) \n'
            s += '{ }'
            metric = self.get_metrics(s)
            for k in range(len(y)):
                y[k].append(metric[k])
        for k in range(len(y)):
            coeff = polyfit(x, y[k], 1)
            l.append(coeff[0])
        return l

    def l1cache_ins_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i3,i4,i5,i6,i7,i8,i9,i10,i11;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{register int i2 = 16;\n\t\tfor (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1+i3+i4+i5+i6+i7+i8+i9;i2 += {step};\n'*128
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        metric[-1] = 0.0
        return [i/t for i in metric]

    def l1cache_cyc_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i3=22,i4=33,i5=44,i6,i7,i8,i9,i10,i11;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{register int i2 = 16;\n\t\tfor (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1/i3/i4;i2 += {step};\n'*128
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        metric[-1] = 0.0
        return [i/t for i in metric]

    def l1cache_lst_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i2=0,i3=22;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{\n\t\ti2 = 0;for (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1;i2+={step};\n'*128
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        metric[-1] = 0.0
        return [i/t for i in metric]

    def l2cache_ins_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size*8
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i3,i4,i5,i6,i7,i8,i9,i10,i11;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{register int i2 = 16;\n\t\tfor (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1+i3+i4+i5+i6+i7+i8+i9;i2 += {step};\n'*128
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        return [i/t for i in metric]

    def l2cache_cyc_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size*8
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i3=22,i4=33,i5=44,i6,i7,i8,i9,i10,i11;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{register int i2 = 16;\n\t\tfor (register long j = 0;j <'+f'{iteration//8};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1/i3/i4;i2 += {step};\n'*8
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        return [i/t for i in metric]

    def l2cache_lst_fit(self,t=10000):
        x = []
        y = [[] for i in range(self.env_num)]
        step = self.cache_line_size//self.int_size*8
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = f'\tregister long i1=12345,i3=22,i4=33,i5=44,i6,i7,i8,i9,i10,i11;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{\n\t\tregister int i2 = 16;for (register long j = 0;j <'+f'{iteration//8};j++)'+'{\n'
        s += f'\t\t\ta[i2]=i1;i2+={step};\n'*8
        s += '}\n}\n' + 'int i = i1;'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        return [i/t for i in metric]

    def msp1_fit(self,t=1000):
        x = []
        y = [[] for i in range(self.env_num)]
        s = f'\tregister long i1=12345,i3=22,i4=33,i5=44;long i0 = 0;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{\n\t\tregister int i2 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
        s += f'\t\t\tif ((i2>>j)&1) i0 = i3+i4+i5;\n'
        s += '}\n}\n'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        return [i/t for i in metric]


    def msp2_fit(self,t = 1000):
        x = []
        y = [[] for i in range(self.env_num)]
        s = f'\tregister long i1=12345,i3=22,i4=33,i5=44;long i0 = 0;\n\tfor (register long i = 0;i<{t};i++) \n'
        s += '{\n\t\tregister int i2 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
        s += f'\t\t\tif ((i2>>j)&1) i0 = i1/i2/i3;\n'
        s += '}\n}\n'
        metric = self.get_metrics(s)
        #print(metric)
        metric[1] -= t*3
        metric[0] -= t
        metric[-2] -= t
        return [i/t for i in metric]
