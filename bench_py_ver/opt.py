from copy import copy
from typing import List
#from scipy.optimize import minimize
#from scipy.optimize import differential_evolution
from cvxopt import matrix, solvers
import copy
import numpy as np
import math
import random

solvers.options['show_progress'] = False

class Data:
    def __init__(self,y,param_for_x,perf_sum) -> None:
        self.y = y
        self.param = param_for_x
        self.perf_sum = perf_sum

class Convexopt:
    def __init__(self,y,param_for_x,perf_sum) -> None:
        self.data = Data(y,param_for_x,perf_sum)
        self.min = -1

    def findmin(self):
        e = 1e-10
        y = self.data.y
        param = self.data.param
        perf_sum = self.data.perf_sum
        cache_start = 8
        cycle0 = 5
        #result = self.find_best_ans()#solvers.qp(P,q,G,h)
        g = []
        for i in range(len(y)):
            if y[i] == 0:y[i] = 1
        for i in range(len(param[0])):
            if i == cycle0:
                g.append([0.01,0.01,0.01,0.01,0,-1,0.01,0.01,1,1,1])
            else:
                g.append([])
            for j in range(len(param[0])):
                if i != j:
                    if i != cycle0:g[i].append(0.0)
                else:
                    if i != cycle0:g[i].append(-1.0)
        h = matrix(0.0,(len(param[0]),1))
        G = matrix(list(map(list, zip(*g))))
        P = matrix(0.0,(len(param[0]),len(param[0])))
        q = matrix(0.0,(len(param[0]),1))
        for i in range(len(param)):
            P += 2*matrix(param[i])*matrix(param[i],(1,len(param[0])))/(float(y[i])**2)
            q += -2*matrix(param[i])/(y[i])
        result = solvers.qp(P,q,G,h)
        #diff = list(matrix(list(map(list, zip(*param))))*result['x']-matrix(y))
        #print(result['x'])
        return self.getint(matrix(list(map(list, zip(*param)))),list(result['x']),y)#[int(i+0.8) for i in result['x']]#result#[int(i+0.5) for i in result]#ans#list(result['x'])

    def getint(self,param,result,y):
        ans = []
        M = 100000
        for k in range(2**len(result)):
            result_temp = copy.deepcopy(result)
            count = k
            judge = 0
            for i in range(len(result_temp)):
                judge = count%2
                count /= 2
                if judge == 0:
                    result_temp[i] = int(result_temp[i])
                else:
                    result_temp[i] = int(result_temp[i]+1)
            diff = list(param*matrix(result_temp)-matrix(y))
            #print(diff)
            for u in range(len(diff)):
                diff[u] /= y[u]
            loss = matrix(diff,(1,len(diff)))*matrix(diff)
            if k == 0 or loss[0] < M:
                M = loss[0]
                ans = result_temp
        return ans
