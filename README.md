# dnachronYdb-putils
A python utilities used for manipulating the **dnachronYdb** database.

## README.md
- en [English](README.md)
- zh_CN [简体中文](README.zh_CN.md)

## This project is also hosted at
- [GitHub](https://github.com/dnachron/dnachronYdb-putils)
- [Gitee](https://gitee.com/dnachron/dnachronYdb-putils)

## The dnachronYdb repo
- [dnachronYdb GitHub](https://github.com/dnachron/dnachronYdb)
- [dnachronYdb Gitee](https://gitee.com/dnachron/dnachronYdb)

## Why we create this project
To provide a offline, standard, batch process tools for conversion and search on mutation names and positions.
- Based on the database we collated in dnachronYdb.
- You can batch process mutation names and position conversion. 

Welcome to visit our website.
- <https://www.dnachron.com> DNAChron International
- <https://www.dnachron.cn> DNAChron China

## Prepare the environment
### Install python
Need install [python](https://www.python.org/downloads/), or use [anaconda](https://docs.anaconda.com/anaconda/install/) environment  
Please make sure python version > 3.7.0
```
python3 --version
```
or
```
python --version
```
### Install the python dependencies
```
pip3 install django pyfaidx pyliftover
```
or
```
pip install django pyfaidx pyliftover
```

## Install
### Download dnachronYdb-putils
clone or download this repository
### Download dnachronYdb database
Refer to description in [dnachronYdb repo](#the-dnachronydb-repo)
- If you use git, clone the repository to the root directory of dnachronYdb-putils and execute build.sh to generate database
- If you download database directly, put the database to dnachronYdb-putils/dnachronYdb/

### Verify
At the dnachronYdb-putils directory
```
python utils.py
```
If everyting is ok, you will find
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

## Features
### vcf
Generate mutation vcf file for common bio-tools use. E.g., you can annotate the name to your vcf with this vcf by bcftools annotate directly.
```
python utils.py vcf mutations_hg38.vcf.gz
```
#### Arguments
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
Annotate the mutation name to mutation 
#### You can select reference build
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

#### If you provide the reference sequence, it can normalize mutation automatically
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

#### Arguments
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
Transfer mutation name to mutation
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
#### Arguments
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
Lift over positions between different reference builds.
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
#### Current support builds
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
#### Arguments
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
