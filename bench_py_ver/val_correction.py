from typing import Dict
from opt import Convexopt
from cvxopt import matrix, solvers
from block import Block

class Correction:
    def __init__(self,data:Dict,perf_sum,performanceDict,param_for_x,flag = 0) -> None:
        self.block = Block([],0,[])
        self.flag = flag
        self.data = data
        for i in self.data.keys():
            if flag:break
            val = self.data[i]
            self.data[i] = [val[self.block.trans['cyc']],val[self.block.trans['ins']],val[self.block.trans['lst']],
                val[self.block.trans['l1_dcm']],val[self.block.trans['br_cn']],val[self.block.trans['br_msp']]]
        self.perf_sum = [perf_sum[self.block.trans['cyc']],perf_sum[self.block.trans['ins']],perf_sum[self.block.trans['lst']],
            perf_sum[self.block.trans['l1_dcm']],perf_sum[self.block.trans['br_cn']],perf_sum[self.block.trans['br_msp']]]
        self.perfdict = performanceDict
        self.param = param_for_x
        self.corrected = {}
        for i in data.keys():
            self.corrected[i] = 0

    def re(self):
        for i in self.data.keys():
            if self.flag:break
            val = self.data[i]
            self.data[i] = [val[2],val[3],val[1],
                val[0],val[4],val[5]]

    def correction(self):
        l = len(self.data.keys())
        if l <= 1:
            return self.data
        while(True):
            l = l - 1
            if self.correction_step() == -1:break
            #print(self.data)
            for i in self.data.values():
                for j in range(len(i)):
                    if i[j]<0:i[j] = 0
            if l <= 1:
                self.re()
                return self.data
        self.re()
        return self.data

    def correction_step(self):
        data = self.data
        perf_sum = self.perf_sum
        x = {}
        now_data = []
        for i in data.keys():
            if self.corrected[i] != 0:
                continue
            y = data[i]
            Opt = Convexopt(y,self.param,perf_sum)
            x[i] = Opt.findmin()
            #print(x[i])
            diff = list(matrix(list(map(list, zip(*self.param))))*matrix(x[i])-matrix(y))
            #print(diff)
            loss = matrix(diff,(1,len(diff)))*matrix(diff)
            now_data.append((i,loss[0]*(self.perfdict[i]**2)))
        now_data = sorted(now_data,key=lambda x:x[1],reverse=True)
        return(self.corr_val(now_data,x))
        
        
    def corr_val(self,now_data,x):
        #print(now_data)
        percent = [sum([self.perfdict[now_data[v][0]]*self.data[now_data[v][0]][u] for v in range(1,len(now_data))]) for u in range(len(self.data[now_data[0][0]]))]
        print(percent)
        for i in range(1):
            self.corrected[now_data[i][0]] = 1
            y = self.data[now_data[i][0]]
            diff = list(matrix(y)-matrix(list(map(list, zip(*self.param))))*matrix(x[now_data[i][0]]))
            print(now_data[i][0],'\n',y,'\n',list(matrix(list(map(list, zip(*self.param))))*matrix(x[now_data[i][0]])))
            diff = [diff[u]*self.perfdict[now_data[i][0]] for u in range(len(y))]
            diff[3] -= 200*self.perfdict[now_data[i][0]]
            #print(diff)
            for j in range(1,len(now_data)):
                for u in range(len(y)):
                    corr = self.data[now_data[j][0]][u]/percent[u]*diff[u]
                    if corr > 0:
                        corr = min(corr,0.1*self.data[now_data[j][0]][u])
                    else:
                        corr = max(corr,-0.1*self.data[now_data[j][0]][u])
                    self.data[now_data[j][0]][u] = self.data[now_data[j][0]][u]+corr
            print(diff)
            diff = [diff[u]/(y[u]*self.perfdict[now_data[i][0]]) for u in range(len(y))]
            loss = matrix(diff,(1,len(diff)))*matrix(diff)
            print(loss[0])
            if loss[0] < 1e-6 or loss[0] > 1000:return -1
        return 0

