# dnachronYdb-putils
操作**dnachronYdb**数据库的python工具集.

## README.md
- en [English](README.md)
- zh_CN [简体中文](README.zh_CN.md)

## 该项目同时托管于
- [GitHub](https://github.com/dnachron/dnachronYdb-putils)
- [Gitee](https://gitee.com/dnachron/dnachronYdb-putils)

## dnachronYdb仓库
- [dnachronYdb GitHub](https://github.com/dnachron/dnachronYdb)
- [dnachronYdb Gitee](https://gitee.com/dnachron/dnachronYdb)

## 为什么创建该项目
为祖源爱好者们提供一个离线可用的、标准化的、可批量处理的突变名、坐标转换、查询工具
- 基于我们整理好的数据库dnachronYdb。
- 可批量处理突变名、坐标互相转换。

欢迎访问我们的网站
- <https://www.dnachron.com> 基因志国际站
- <https://www.dnachron.cn> 基因志中国站

## 环境准备
### 安装python
需要安装[python](https://www.python.org/downloads/)，或直接使用[anaconda](https://docs.anaconda.com/anaconda/install/)环境  
请确保python版本>3.7.0
```
python3 --version
```
或者
```
python --version
```
### 安装python依赖包
```
pip3 install django pyfaidx pyliftover
```
或者
```
pip install django pyfaidx pyliftover
```

## 安装
### 下载dnachronYdb-putils
克隆或下载整个仓库
### 下载dnachronYdb数据库
参考[dnachronYdb仓库](#dnachronydb仓库)说明。
- 如果用git方式，把仓库克隆到dnachronYdb-putils根目录下，执行build.sh生成数据库
- 如果直接下载数据库，把下载的数据库放到dnachronYdb-putils/dnachronYdb/下

### 验证
进入dnachronYdb-putils目录
```
python utils.py
```
如果环境安装正常，您将看到
```
usage: utils.py [-h] {vcf,annot,trans,lift} ...

positional arguments:
  {vcf,annot,trans,lift}
    vcf                 generate mutation vcf file for common bio-tools use
    annot               annotate positions with mutation name and other info
    trans               transfer mutation name to position, ancestral, derived
    lift                lift over positions between different reference builds

optional arguments:
  -h, --help            show this help message and exit
```

## 主要功能
### vcf
生成一个标准vcf格式文件，可用于通用的生物信息工具。比如您可用bcftools，通过生成的vcf文件，注释突变名到您自己的vcf文件中。
```
python utils.py vcf mutations_hg38.vcf.gz
```
#### 参数
```
usage: utils.py vcf [-h] [-v] [-O {v,z}] [output]

Generate mutation vcf file for common bio-tools use. E.g., you can annotate the name to your vcf with this vcf by bcftools annotate directly.

positional arguments:
  output                the output file, you can output to STDOUT by -

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         include all duplicated names, otherwise only the first name
  -O {v,z}, --output-type {v,z}
                        v/z: un/compressed VCF, if not specified, it will be detected automatically by output file name, or u if can't
```
### annot
注释突变的突变名  
#### 可设置参考序列
```
python utils.py annot -b hg19 -v testdata/hg19_mutation.csv
```
| POS      | REF  | ALT  | NORM_POS | NORM_REF | NORM_ALT | ID         |
| :------- | :--- | :--- | :------- | :------- | :------- | :--------- |
| 2661694  | A    | G    | 2793653  | A        | G        | MF653471   |
| 2663708  | A    | T    | 2795667  | A        | T        | M8944/E260 |
| 2667926  | T    | C    | 2799885  | T        | C        | F2         |
| 2668456  | T    | C    | 2800415  | T        | C        | MF653477   |
| 59033300 | C    | T    | 56887153 | C        | T        | BY42595    |
| 59033357 | A    | C    | 56887210 | A        | C        | TY6164     |
| 59033730 | G    | A    | 56887583 | G        | A        | F26843     |
| 60033730 | G    | A    |

#### 传入参考序列，可实现对突变的自动标准化
```
python utils.py annot -r path/to/hg38_ref.fasta -a testdata/hg38_mutation.csv
```
| position | anc  | der  | NORM_POS | NORM_REF | NORM_ALT | ID       | YCC          | ISOGG            | reference                 | comment               |
| :------- | :--- | :--- | :------- | :------- | :------- | :------- | :----------- | :--------------- | :------------------------ | :-------------------- |
| 13871775 | G    | A    | 13871775 | G        | A        | FGC93673 |              |                  | Full Genomes Corp. (2020) |
| 17397552 | G    | C    | 17397552 | G        | C        | MF160961 | O            | O                | 23mofang (2020)           |
| 6848774  | a    | g    | 6848774  | A        | G        | A11751   | R1b-FGC20747 | R1b              | Rachel Unkefer (2016)     | Below DF27 > FGC20747 |
| 8933332  | GG   | tg   | 8933332  | G        | T        | MF159779 | O            | O                | 23mofang (2020)           |
| 8933333  | G    | A    | 8933333  | G        | A        |
| 8933332  | G    | A    | 8933332  | G        | A        |
| 14735008 | TTT  | T    | 14735006 | ATT      | A        | ACT2377  | C3-M217      | C2a1a2a2a1-F3555 | Ryan Lan-Hai Wei (2018)   | Downstream F3555      |

#### 参数
```
usage: utils.py annot [-h] [-o [OUTPUT]] [-b {hg19,hg38,cp086569.1,cp086569.2}] [-r [REFERENCE]] [-v] [-a] [-H] [input]

Annotate positions with mutation name and other info. The input should be a list of mutations: position, ancestral, derived, seprated by comma, and each mutation one line. Or simply use csv format file. You
can test with hg19_mutation.csv and hg38_mutation.csv in testdata. Duplicated mutations will be removed.

positional arguments:
  input                 the input file, you can input from STDIN by -

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT], --output [OUTPUT]
                        the output file, default to STDOUT if not specified
  -b {hg19,hg38,cp086569.1,cp086569.2}, --build {hg19,hg38,cp086569.1,cp086569.2}
                        the reference build, default is hg38
  -r [REFERENCE], --reference [REFERENCE]
                        if you provide HG38 reference file, it can try to normalize INDELs before annotate
  -v, --verbose         include all duplicated names, otherwise only the first name
  -a, --appendix        annotate appendix info
  -H, --hide_header     don't output header
```
### trans
转换突变名为突变
```
python utils.py trans -b cp086569.2 testdata/names.csv
```
| ORI_ID   | ID       | HG38_POS | CP086569.2_POS | REF      | ALT  |
| :------- | :------- | :------- | :------------- | :------- | :--- |
| FGC47649 | FGC47649 | 2814614  | 2491454        | CTTTTTTT | C    |
| MF121480 | MF121480 | 23187988 | 24015181       | C        | G    |
| FT145229 | FT145229 | 5103294  | 4782829        | T        | C    |
| ft299719 | FT299719 | 26591050 | 27403001       | C        | A    |
| F793     | F793     | 6787706  | 6440023        | T        | C    |
#### 参数
```
usage: utils.py trans [-h] [-o [OUTPUT]] [-b {hg19,hg38,cp086569.1,cp086569.2}] [-H] [-B] [-N] [input]

Transfer mutation name to position, ancestral, derived. The input should be a list of mutation names, each name one line. Or simply use csv format file. You can test with testdata/names.csv. Duplicated names
will be removed.

positional arguments:
  input                 the input file, you can input from STDIN by -

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT], --output [OUTPUT]
                        the output file, default to STDOUT if not specified
  -b {hg19,hg38,cp086569.1,cp086569.2}, --build {hg19,hg38,cp086569.1,cp086569.2}
                        the reference build, default is hg38
  -H, --hide_header     don't output header
  -B, --hide_db_pos     don't output HG38 position if build is not HG38
  -N, --hide_real_name  don't output real name in database
```
### lift
转换坐标到不同参考序列
```
python utils.py lift -s hg38 -t cp086569.2 testdata/hg38_mutation.csv
```
| position | CP086569.2 |
| :------- | :--------- |
| 13871775 | 14778426   |
| 17397552 | 18304070   |
| 6848774  | 6501097    |
| 8933332  | 8589436    |
| 8933333  | 8589437    |
| 8933332  | 8589436    |
| 14735008 | 15641644   |
#### 当前支持的转换
```
python utils.py lift -l
```
```
supported builds convert:
HG19 -> HG38
HG38 -> HG19
HG38 -> CP086569.1
HG38 -> CP086569.2
CP086569.1 -> HG38
CP086569.1 -> CP086569.2
CP086569.2 -> HG38
CP086569.2 -> CP086569.1
```
#### 参数
```
usage: utils.py lift [-h] [-l] [-s {hg19,hg38,cp086569.1,cp086569.2}] [-t {hg19,hg38,cp086569.1,cp086569.2}] [-o [OUTPUT]] [-H] [input]

Lift over positions between different reference builds. The input should be a list of positions, each position one line. And ignore extra columns. You can test with hg19_mutation.csv and hg38_mutation.csv in
testdata. Duplicated positions will be removed.

positional arguments:
  input                 the input file, you can input from STDIN by -

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list all support lift over builds
  -s {hg19,hg38,cp086569.1,cp086569.2}, --source_build {hg19,hg38,cp086569.1,cp086569.2}
                        the souce reference build
  -t {hg19,hg38,cp086569.1,cp086569.2}, --target_build {hg19,hg38,cp086569.1,cp086569.2}
                        the target reference build
  -o [OUTPUT], --output [OUTPUT]
                        the output file, default to STDOUT if not specified
  -H, --hide_header     don't output header
```
