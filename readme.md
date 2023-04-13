# Automatic Benchmark Synthesis

## Requirements

本项目依赖于papi监控硬件性能计数器，故需要安装papi[https://bitbucket.org/icl/papi/wiki/Home]。

部分功能依赖于libunwind，需要编译生成对应的库。

python依赖的环境在requirements.txt当中。

## Quick Start

### 生成trace

在执行待测试应用前，需要利用LD_PRELOAD加载修改后的mpip动态链接库，同时需要修改环境变量PAPI_MON_EVENTS。根据硬件支持的硬件性能计数器的数目，设置该环境变量，例如说：

```shell
export PAPI_MON_EVENTS="PAPI_LST_INS:PAPI_L1_DCM:PAPI_TOT_INS:PAPI_TOT_CYC:PAPI_BR_CN:PAPI_BR_MSP"
```

### 拼接trace

由于不同CPU型号硬件计数器数量不同的限制，部分CPU无法同时监控六个性能指标，需要分批次生成性能指标。本项目可以通过`splice.py`来拼接不同长度性能指标的trace。

```shell
mpiexec -np $nprocs python splice.pt -t /path/to/trace/ -o /new/trace/output/path/
```

### 生成benchmark代码

本项目可以通过MPI程序运行的一次trace生成其相应的benchmark代码。也可以同时根据相同MPI程序在不同平台上生成的trace，生成更贴近源程序的benchmark代码。

#### 根据单平台trace生成benchmark代码

```shell
mpiexec -np $nprocs python main.py -t /path/to/trace/ -o /benchmark/output/path/
```

#### 根据多平台trace生成benchmark代码

不同平台数据可以通过配置文件的方式传入到程序当中。只需要在程序运行时指定配置文件的地址即可。

```shell
mpiexec -np $nprocs python multi_platform.py -y /path/to/config.yaml
```

##### 多平台配置文件解释

```yaml
# 当前平台trace地址
curPlatformPath: '/gpfs/home/cs/sunjw/addition/run/sequitur-main/BT_D_36/'    

# 其他平台trace地址，是一个数组，每个元素包含两个内容，分别是trace地址和minibench地址
platform:    
  - tracePath: '/gpfs/home/cs/sunjw/addition/run/sequitur-main/BT_D_36/e3v5/'
    minibenchPath: '/gpfs/home/cs/sunjw/addition/run/sequitur-main/platbench/e3v5/minibench'

# 输出文件的位置
outputPath: '/gpfs/home/cs/sunjw/addition/run/sequitur-main/BT_D_36/'    

# 是否压缩主函数，默认true
compress: True    
```

### 代码块拟合

在生成benchmark的同时，还会生成一份计算代码块压缩的结果，单平台的压缩结果为`data_bucket`，多平台的压缩结果为`two_plat_data_bucket`。拟合代码块时通过运行的参数指定该文件的地址就可以拟合生成相应的代码块。

```shell
python code_gen.py -o /path/to/data_bucket    # 单进程版本
mpiexec -np $nprocs code_gen.py -o /path/to/data_bucket # 多进程版本 
```

### 运行minibench

在需要运行minibench的平台上，进入`bench_py_ver`文件夹，运行`platbench.py`即可。

```shell
python platbench.py
```

## 文件说明

code_generation.py: 代码生成

Combine_comm.py: 合并文法

constant.py: 程序中用到的一些常量定义

Dump_trace2time.py: 将trace中的时间信息导出

editDistance.py: 计算编辑距离

global_val.py: 一些全局变量保存的位置

main.py: 主函数

Merge_main_rule.py: 合并主规则

MPI_define.py: 一些MPI定义的常量

Multi_platform.py: 多平台的主函数

nonterminal_dict.py: 非终结符的合并

platbench.py: 在平台上运行minibench

sequitur.py: sequitur算法的实现

utils.py: 一些辅助功能的函数的实现

With_compute.py: 计算代码库的进程间压缩和进程内压缩

#### bench_analyze

一些分析trace的工具

#### configs

多平台配置文件的地址

#### tools

需要用到的trace生成工具，修改后的mpip