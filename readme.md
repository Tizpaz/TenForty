# TenForty
This repository provides the tool and the evaluation subjects for the paper ``Metamorphic Testing and Debugging of Tax Preparation Software`` accepted to the 45th International Conference on Software Engineering: Software Engineering in Society track at [ICSE-SEIS 2023](https://arxiv.org/abs/2205.04998).

### Setup
To run the tool, you first need to download the [OpenTaxSolver](https://opentaxsolver.sourceforge.net/) software (we currently support 2018, 2019, 2020, and 2021 versions).  In doing so, you can access to the source code from [this link](https://sourceforge.net/projects/opentaxsolver/files/). Then, you need to include files from this reposirty in the ``tax_form_files/US_1040``. 

### Run Testing
After including the source code, you can simply issue the following command to run the testing for married filing jointly (MFJ) properties (see the paper for more information) of year 2021 when you are at the [`US_1040`](OpenTaxSolver2021_19.07_linux64/tax_form_files/US_1040/):
```
python main_joint_2021_final.py --property X --timeout S
```
where you can simply replace the property number (X) with 1, 2, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, and 16. The time-out S is 900 in the paper (in seconds). For married filing separately (MFS), you can issue:
```
python main_sep_2021_final.py --property X --timeout S
```
where you can replace X with 3, 7, and 9.

To run the tool for a different year, you can simply go to the corresponding ``US_1040`` folder and isse the same command with a different year number, e.g., 
```
python main_joint_2020_final.py --property 1 --timeout 900
```
