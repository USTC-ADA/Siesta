import copy
from minibench import Minibench

class Param:
    def __init__(self) -> None:
        self.cachenum = 0
        self.branchnum = 0
        self.restbranch = 0
        self.nop = 0
        self.div = 0
        self.add = 0
        self.div2 = 0
        self.add2 = 0
        self.pause = 0
        self.iter1 = 0
        self.iter2 = 0
        self.l1cache_ins = 0
        self.l1cache_cyc = 0
        self.l1cache_lst = 0
        self.l2cache_ins = 0
        self.l2cache_cyc = 0
        self.l2cache_lst = 0
        self.msp1 = 0
        self.msp2 = 0
        self.unroll = 100


    def print_param(self) -> None:
        print(self.cachenum,self.branchnum,self.unroll,self.restbranch,self.nop,self.div,self.add,self.pause)

    def all_small_part(self) -> int:
        return self.l1cache_ins+self.l1cache_cyc+self.l1cache_lst

class Block:
    def __init__(self,target,number,perf_sum) -> None:
        self.target = copy.deepcopy(target)
        self.trans = {"lst":0,"l1_dcm":1,"ins":2,"cyc":3,"br_cn":4,"br_msp":5}#,"l2_dcm":6}
        self.blockname = 'block'+str(number)
        self.param = Param()
        self.borrow = 0
        bench = Minibench("")
        self.l1_cache_size = bench.l1_cache_size
        self.l2_cache_size = bench.l2_cache_size
        self.cache_line_size = bench.cache_line_size
        self.int_size = bench.int_size
        self.perf_sum = perf_sum

    def gen_fun_block(self,path,mode='withpapi') -> None:
        self.temp_msp1 = self.param.msp1
        self.temp_msp2 = self.param.msp2
        with open(path,'a') as f:
            f.write("void "+self.blockname+'(){\n')
            if mode == 'withpapi':
                f.write("\tint *a=(int*)malloc(sizeof(int)*100000000);\n")
                f.write("\tpapi_retval = PAPI_start(EventSet);\n")

            f.write(self.gen_start_var())
            f.write(self.gen_add())
            f.write(self.gen_div())
            f.write(self.gen_add2())
            f.write(self.gen_div2())
            f.write(self.gen_l1cache_ins())
            f.write(self.gen_l1cache_cyc())
            f.write(self.gen_l1cache_lst())
            f.write(self.gen_iter1())
            f.write(self.gen_iter2())
            if mode == 'withpapi':
                f.write("\tpapi_retval=PAPI_read(EventSet, values[0]);\n")
                f.write("\tfor (int i = 0; i < event_count; i++) printf(\"%lld \", values[0][i]);\n")
            f.write('}\n')


    def gen_start_var(self) -> str:
        s = "\tlong i1=12345,i2=67890,i3=54321;\n"
        s += "\tregister long i4=12345,i5=67890,i6=54321,i7=54321,i8=54321,i9=54321,i10,i11,i12;\n"
        s += "\tdouble d1=12345,d2=999,d3=123;\n"
        s += "\tint *p;"
        return s

    def gen_add(self) -> str:
        cycle = self.param.add//self.param.unroll
        if cycle == 0:return ""
        msp1_iter = min(self.temp_msp1//cycle,self.param.unroll)
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = min(self.temp_msp2//cycle,self.param.unroll)
        self.temp_msp2 -= msp2_iter*cycle
        s = "\tfor (register long i = 0;i<" + str(cycle) + ";i++){\n"
        for i in range(self.param.unroll):
            s += "\t\ti1 = i2+i3;\n"
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'
        s += "\t}\n"

        return s

    def gen_div(self) -> str:
        if self.param.div == 0:return ""
        cycle = self.param.div//self.param.unroll
        if cycle == 0:return ""
        msp1_iter = min(self.temp_msp1//cycle,self.param.unroll)
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = min(self.temp_msp2//cycle,self.param.unroll)
        self.temp_msp2 -= msp2_iter*cycle      
        s = "\tfor (register long i = 0;i<" + str(cycle) + ";i++){\n"
        for i in range(self.param.unroll):
            s += "\t\td1 = d1/d2;\n"
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'        
        s += "\t}\n"
        return s

    def gen_add2(self) -> str:
        cycle = self.param.add2//self.param.unroll
        if cycle == 0:return ""
        msp1_iter = min(self.temp_msp1//cycle,self.param.unroll)
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = min(self.temp_msp2//cycle,self.param.unroll)
        self.temp_msp2 -= msp2_iter*cycle
        s = "\tfor (register long i = 0;i<" + str(cycle) + ";i++){\n"
        for i in range(self.param.unroll):
            s += "\t\ti1 = i4+i5+i6+i7+i8;\n"
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'
        s += "\t}\n"

        return s

    def gen_div2(self) -> str:
        if self.param.div2 == 0:return ""
        cycle = self.param.div2//self.param.unroll
        if cycle == 0:return ""
        msp1_iter = min(self.temp_msp1//cycle,self.param.unroll)
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = min(self.temp_msp2//cycle,self.param.unroll)
        self.temp_msp2 -= msp2_iter*cycle      
        s = "\tfor (register long i = 0;i<" + str(cycle) + ";i++){\n"
        for i in range(self.param.unroll):
            s += "\t\td1 = i5/i6/i7/i8/i9;\n"
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'        
        s += "\t}\n"
        return s

    def gen_iter1(self) -> str:
        cycle = self.param.iter1
        s = "\tfor (long i = 0;i<" + str(cycle) + ";i++){\n"
        s += "\t}\n"
        return s

    def gen_iter2(self) -> str:
        cycle = self.param.iter2 - self.param.all_small_part()-((self.param.add+self.param.div+self.param.add2+self.param.div2)//self.param.unroll)
        
        s = "\tfor (register long i = 0;i<" + str(self.temp_msp1) + ";i++){\n"
        for i in range(1):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        s += "\t}\n"

        s += "\tfor (register long i = 0;i<" + str(self.temp_msp2) + ";i++){\n"
        for i in range(1):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'               
        s += "\t}\n"

        cycle -= self.temp_msp1+self.temp_msp2
        s += "\tfor (register long i = 0;i<" + str(cycle) + ";i++){\n"
        s += "\t}\n"
        return s

    def gen_l1cache_ins(self) -> str:
        if self.param.l1cache_ins == 0:return ""
        cycle = self.param.l1cache_ins
        if cycle == 0:return ""
        msp1_iter = int(min(self.temp_msp1//cycle,self.param.unroll))
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = int(min(self.temp_msp2//cycle,self.param.unroll))
        self.temp_msp2 -= msp2_iter*cycle    
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = "\tfor (register long i = 0;i<" + str(int(cycle)) + ";i++){\n"
        s += '\t\tregister long i12 = 0;for (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i12]=i4+i5+i6+i7+i8+i9+i10+i11;i12 += {step};\n'*128
        s += '\t\t}\n'
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'        
        s += "\t}\n"

        s += '\t\ti12 = 0;\n'
        s += f'\t\t\ta[i12]=i4/i5/i6;i12 += {step};\n'*int((cycle-int(cycle))*iteration)
        return s
    
    def gen_l1cache_cyc(self) -> str:
        if self.param.l1cache_cyc == 0:return ""
        cycle = self.param.l1cache_cyc
        if cycle == 0:return ""
        msp1_iter = int(min(self.temp_msp1//cycle,self.param.unroll))
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = int(min(self.temp_msp2//cycle,self.param.unroll))
        self.temp_msp2 -= msp2_iter*cycle    
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = "\tfor (register long i = 0;i<" + str(int(cycle)) + ";i++){\n"
        s += '\t\tregister long i12 = 0;for (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i12]=i4/i5/i6;i12 += {step};\n'*128
        s += '\t\t}\n'
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'        
        s += "\t}\n"

        s += '\t\ti12 = 0;\n'
        s += f'\t\t\ta[i12]=i4/i5/i6;i12 += {step};\n'*int((cycle-int(cycle))*iteration)
        return s

    def gen_l1cache_lst(self) -> str:
        if self.param.l1cache_lst == 0:return ""
        cycle = self.param.l1cache_lst
        if cycle == 0:return ""
        msp1_iter = int(min(self.temp_msp1//cycle,self.param.unroll))
        self.temp_msp1 -= msp1_iter*cycle
        msp2_iter = int(min(self.temp_msp2//cycle,self.param.unroll))
        self.temp_msp2 -= msp2_iter*cycle      
        step = self.cache_line_size//self.int_size
        iteration = self.l1_cache_size//self.cache_line_size*2
        s = "\tfor (register long i = 0;i<" + str(int(cycle)) + ";i++){\n"
        s += '\t\tregister long i12 = 0;for (register long j = 0;j <'+f'{iteration//128};j++)'+'{\n'
        s += f'\t\t\ta[i12]=i4;i12 += {step};\n'*128
        s += '\t\t}\n'
        for i in range(msp1_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i5+i6+i7;\n}\t\n'
        for i in range(msp2_iter):
            s += '\t\ti4 = rand()%(1<<20);for (register long j = 0;j <'+f'20;j++)'+'{\n'
            s += '\t\t\tif ((i4>>j)&1) i1 = i7/i6/i5;\n}\t\n'        
        s += "\t}\n"

        s += '\t\ti12 = 0;\n'
        s += f'\t\t\ta[i12]=i4/i5/i6;i12 += {step};\n'*int((cycle-int(cycle))*iteration)
        return s



if __name__=="__main__":
    block = Block([1,2,3,4,5,6],0)
    block.gen_fun_block('./code/code.c','withpapi')