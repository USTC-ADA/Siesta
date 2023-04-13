from typing import List
from block import Block

class Code:
    def __init__(self,path,blocks:List[Block],mode='withpapi',name = 'block') -> None:
        self.codec = path+name+'.c'
        self.codeh = path+name+'.h'
        self.blocks = blocks
        self.mode = mode


    def gen_code(self) -> None:
        if self.mode == 'withpapi':
            with open(self.codec,'w') as f:
                f.write(self.gen_asm())
                with open('./fstart.txt','r') as start:
                    f.writelines(start.readlines())
            self.blocks[0].gen_fun_block(self.codec,'withpapi')
            with open(self.codec,'a') as f:
                with open('./fend.txt','r') as end:
                    f.writelines(end.readlines())
                f.write(self.blocks[0].blockname+"();\n}\n")
        else:
            with open(self.codec,'w') as f:
                f.write("#include \"block.h\"\n")
                f.write("int initial(){a=(int*)malloc(sizeof(int)*100000000);}\n")
                f.write(self.gen_asm())
            for block in self.blocks:
                block.gen_fun_block(self.codec,'withoutpapi')
            with open(self.codeh,'w') as f:
                f.write("#include <stdlib.h>\n")
                f.write("int *a;\n")
                f.write("int initial();\n")
                for block in self.blocks:
                    f.write("void "+block.blockname+'();\n')

    def gen_asm(self) -> str:
        s = "#if defined  __aarch64__\n"
        s += "#define ASM_PAUSE \"yield\\n\\t\"\n"
        s += "#define ASM_MOV \"mov   %[a], %[POINT]\\n\\t\":[POINT] \"=r\" (p):[a] \"r\" (a)\n"
        s += "#define ASM_READ \"ldr %[I5], [%[POINT]]\\n\\t\"\"add %[POINT], %[POINT], #8192\\n\\t\"\n"
        s += "#elif defined __x86_64__\n"
        s += "#define ASM_PAUSE \"pause\\n\\t\"\n"
        s += "#define ASM_MOV \"movq   %[a], %[POINT]\\n\\t\":[POINT] \"=r\" (p):[a] \"r\" (a)\n"
        s += "#define ASM_READ \"movslq (%[POINT]), %[I5]\\n\\t\"\"addq $8192,%[POINT]\\n\\t\"\n"
        s += "#endif\n"
        return s
