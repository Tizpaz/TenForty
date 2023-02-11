import sys
sys.path.append("./")
#sys.path.append("../")
import numpy as np
import os
import time
import copy
from scipy.stats import randint
import csv
import argparse
import xml_parser
import xml_parser_domains
from subprocess import call
import math

def handle_debugging(base, failed, feature_val, csv_columns, index_follow_up):
    filename = 'taxsolve_US_1040_2020.c'
    ret = call(["gcov", filename], cwd ='../../src/')
    input_coverage = '../../src/taxsolve_US_1040_2020.c.gcov'
    current_feature_val = {}
    with open(input_coverage, 'r') as read_cov:
        for line in read_cov:
            if "        -:" in line:
                continue
            line_split = line.split()
            feature_name = line_split[1] + line_split[2] if len(line_split) >= 3 else line_split[1]
            if feature_name not in csv_columns:
                csv_columns.append(feature_name)
            if not base:
                if "#####" in line_split[0]:
                    if len(feature_val) >= 1:
                        current_feature_val[feature_name] = 0 if feature_name not in feature_val[-index_follow_up].keys() else feature_val[-index_follow_up][feature_name]
                    else:
                        current_feature_val[feature_name] = count             
                else:
                    count = int(line_split[0].replace("*:","")) if "*:" in line_split[0] else int(line_split[0].replace(":","")) 
                    if len(feature_val) >= 1:
                        current_feature_val[feature_name] = count if feature_name not in feature_val[-index_follow_up].keys() else count + feature_val[-index_follow_up][feature_name]
                    else:
                        current_feature_val[feature_name] = count             
            else:
                if "#####" in line_split[0]:
                    current_feature_val[feature_name] = 0
                else:
                    count = int(line_split[0].replace("*:","")) if "*:" in line_split[0] else int(line_split[0].replace(":",""))
                    current_feature_val[feature_name] = count
    if 'NoneType' in str(type(failed)) :
        current_feature_val["pass"] = 'None'
    else:
        current_feature_val["pass"] = failed
    os.system('rm -rf ../../src/taxsolve_US_1040_2020.gcda')
    feature_val.append(current_feature_val)


def AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind):
    charity = 0
    for index in char_ind:
        charity += inp[index]

    #print('charity',charity)
    total_inc = 0
    for index in tot_inc_ind:
        total_inc += inp[index]
    #print('total incom',total_inc)
    cap_gain = 0   
    for index in cap_gain_ind:
        cap_gain += inp[index]  
    #print('cap gain',cap_gain)
    adj_to_inc = 0   
    for index in adj_to_inc_ind:
        adj_to_inc += inp[index]
    #print('adj to inc',adj_to_inc)
   
    total_adj = adj_to_inc + charity
    total_income = total_inc + cap_gain
    #print('agi ', total_income - total_adj)
    #print('----------------------------')
    return total_income - total_adj


def property_generation(property_id, start_time, max_time):
    input_program_tree = './input_married_sep_1.xml'
    num_args = 110
    arr_min, arr_max, arr_type, arr_default, arr_name = xml_parser_domains.xml_parser_domains(input_program_tree, num_args)
    inp_0 = []
    time_to_first_failed = -1
    feature_val = []        # internal features to their values 
    csv_columns = ["pass"]        # the feature set
    
    with open('output_random_debugging_property_' + str(property_id) + "_" + str(start_time) + '.csv', 'w') as writer,open("coverage_property_" + str(property_id) + "_" + str(start_time) + ".csv", 'w') as f_cov:
        for i in range(len(arr_min)):
            if(arr_type[i] == 'bool'):
                inp_0.append(int(arr_default[i]))
            elif(arr_type[i] == 'int'):
                inp_0.append(int(arr_default[i]))
            elif(arr_type[i] == 'float'):
                inp_0.append(float(arr_default[i]))
        for i in range(len(arr_name)):
            if arr_name[i] == None:
                writer.write(",")
            else:
                writer.write("%s," % (arr_name[i]))
        num_qualified_child = 1
        results = []

        if(property_id == 3):
            L27_index = 23 # Earned Income Credit (EIC)
            L1_index = 7 #  Wages, salaries, tips (W-2's Box-1).
            writer.write("AGI,")
            writer.write("EIC,")
            writer.write("failed,")
            writer.write("return\n")
            counter = 0
            while((time.time() - start_time) <= max_time):
                inp = inp_0.copy()
                index = np.random.choice([L1_index])
                if(arr_type[index] == 'bool'):
                    inp[index] = 1 - inp[index]
                elif(arr_type[index] == 'int'):
                    minVal = int(arr_min[index])
                    maxVal = int(arr_max[index])
                    inp[index] = np.random.randint(minVal,maxVal+1)
                elif(arr_type[index] == 'float'):
                    minVal = float(arr_min[index])
                    maxVal = float(arr_max[index])
                    inp[index] = np.random.randint(math.floor(minVal),math.floor(maxVal)+1)
                    inp[index] += round(np.random.uniform(0,0.99),2)
                inp[L27_index] = np.random.randint(1,1000)
                FTR1 = test_cases(input_program_tree, inp, writer)
                handle_debugging(True, None, feature_val, csv_columns, 0)
                AGI1 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                #AGI1 = (inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                EIC1 = inp[L27_index]
                writer.write(str(AGI1)+",")
                writer.write(str(EIC1)+",")
                writer.write(str(FTR1)+",")
                writer.write("Base")
                writer.write("\n")
                
                K = 0
                while(K < 1):
                    inp[L27_index] = 0
                    FTR2 = test_cases(input_program_tree, inp, writer)
                    AGI2 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                    #(inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                    EIC2 = inp[L27_index]
                    
                    if(EIC1 > 0 and EIC2 == 0 and abs(FTR2 - FTR1) > 0.1):
                        writer.write(str(AGI2)+",")
                        writer.write(str(EIC2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("False")
                        writer.write("\n")
                        if(time_to_first_failed < 0):
                            time_to_first_failed = time.time() - start_time
                        results.append(False)
                        handle_debugging(False, False, feature_val, csv_columns, K)
                        break
                    else:
                        writer.write(str(AGI2)+",")
                        writer.write(str(EIC2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("True")
                        writer.write("\n")
                        results.append(True)
                        handle_debugging(False, True, feature_val, csv_columns, K)
                    K = K + 1
                counter += 1
            try:
                f_cov_writer = csv.DictWriter(f_cov, fieldnames=csv_columns)
                f_cov_writer.writeheader()
                for data in feature_val:
                    if data["pass"] == None:
                        continue
                    f_cov_writer.writerow(data)
            except IOError:
                print("I/O error")
            return results, time_to_first_failed

        if(property_id == 7):
            Depend_ind = 5#2020
            L19_ind = 18#2020
            L1_ind = 7 #  Wages, salaries, tips (W-2's Box-1).
            writer.write("AGI,")
            writer.write("#QC,")
            writer.write("C,")
            writer.write("return,")
            writer.write("failed\n")
            counter = 0
            while((time.time() - start_time) <= max_time):
                inp = inp_0.copy()
                index = np.random.choice([Depend_ind])
                inp[L1_ind] = np.random.randint(10000,200000)
                if(arr_type[index] == 'bool'):
                    inp[index] = 1 - inp[index]
                elif(arr_type[index] == 'int'):
                    minVal = int(arr_min[index])
                    maxVal = int(arr_max[index])
                    inp[index] = np.random.randint(minVal,maxVal+1)
                elif(arr_type[index] == 'float'):
                    minVal = float(arr_min[index])
                    maxVal = float(arr_max[index])
                    inp[index] = np.random.randint(math.floor(minVal),math.floor(maxVal)+1)
                    inp[index] += round(np.random.uniform(0,0.99),2)
                num_child_1 = inp[Depend_ind] - 1
                c1 = num_child_1 * 2000
                inp[L19_ind] = c1
                FTR1 = test_cases(input_program_tree, inp, writer)
                handle_debugging(True, None, feature_val, csv_columns, 0)
                AGI1 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                #(inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                writer.write(str(AGI1)+",")
                writer.write(str(num_child_1)+",")
                writer.write(str(c1)+",")
                writer.write(str(FTR1)+",")
                writer.write("Base\n")

                K = 0
                while(K < 1):                
                    num_child_2 = np.random.randint(1, inp[Depend_ind]+1) - 1
                    c2 = num_child_2 * 2000
                    inp[L19_ind] = c2
                    FTR2 = test_cases(input_program_tree, inp, writer)
                    AGI2 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                    #(inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                    
                    if(c1 > 0 and c2 > 0 and (FTR1 - FTR2 < -1.0)):
                        writer.write(str(AGI2)+",")
                        writer.write(str(inp[Depend_ind])+",")
                        writer.write(str(c2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("False\n")
                        if(time_to_first_failed < 0):
                            time_to_first_failed = time.time() - start_time
                        results.append(False)
                        handle_debugging(False, False, feature_val, csv_columns, K)
                        break
                    else:
                        writer.write(str(AGI2)+",")
                        writer.write(str(inp[Depend_ind])+",")
                        writer.write(str(c2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("True\n")
                        results.append(True)
                        handle_debugging(False, True, feature_val, csv_columns, K)
                    K = K + 1
                counter += 1
            try:
                f_cov_writer = csv.DictWriter(f_cov, fieldnames=csv_columns)
                f_cov_writer.writeheader()
                for data in feature_val:
                    if data["pass"] == None:
                        continue
                    f_cov_writer.writerow(data)
            except IOError:
                print("I/O error")
            return results, time_to_first_failed

        if(property_id == 9):
            L1_ind = 7 #  Wages, salaries, tips (W-2's Box-1).
            L29_ind = 25#2020
            writer.write("AGI,")
            writer.write("ETC,")
            writer.write("return,")
            writer.write("failed\n")
            counter = 0
            while((time.time() - start_time) <= max_time):
                inp = inp_0.copy()
                index = np.random.choice([L1_ind])
                if(arr_type[index] == 'bool'):
                    inp[index] = 1 - inp[index]
                elif(arr_type[index] == 'int'):
                    minVal = int(arr_min[index])
                    maxVal = int(arr_max[index])
                    inp[index] = np.random.randint(minVal,maxVal+1)
                elif(arr_type[index] == 'float'):
                    minVal = float(arr_min[index])
                    maxVal = float(arr_max[index])
                    inp[index] = np.random.randint(math.floor(minVal),math.floor(maxVal)+1)
                    inp[index] += round(np.random.uniform(0,0.99),2)
                inp[L29_ind] = np.random.randint(1,1000)
                FTR1 = test_cases(input_program_tree, inp, writer)
                handle_debugging(True, None, feature_val, csv_columns, 0)
                AGI1 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                #(inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                ETC1 = inp[L29_ind]
                writer.write(str(AGI1)+",")
                writer.write(str(ETC1)+",")
                writer.write(str(FTR1)+",")
                writer.write("Base")
                writer.write("\n")
                K = 0
                while(K < 1):
                    inp[L29_ind] = 0
                    FTR2 = test_cases(input_program_tree, inp, writer)
                    AGI2 = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
                    #(inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])
                    ETC2 = inp[L29_ind]
                
                    if(ETC1 > 0 and ETC2 == 0 and abs(FTR2 - FTR1)>0.1):
                        writer.write(str(AGI2)+",")
                        writer.write(str(ETC2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("False")
                        writer.write("\n")
                        if(time_to_first_failed < 0):
                            time_to_first_failed = time.time() - start_time
                        results.append(False)
                        handle_debugging(False, False, feature_val, csv_columns, K)
                        break
                    else:
                        writer.write(str(AGI2)+",")
                        writer.write(str(ETC2)+",")
                        writer.write(str(FTR2)+",")
                        writer.write("True")
                        writer.write("\n")
                        results.append(True)
                        handle_debugging(False, True, feature_val, csv_columns, K)
                    K = K + 1
                counter += 1
            try:
                f_cov_writer = csv.DictWriter(f_cov, fieldnames=csv_columns)
                f_cov_writer.writeheader()
                for data in feature_val:
                    if data["pass"] == None:
                        continue
                    f_cov_writer.writerow(data)
            except IOError:
                print("I/O error")
            return results, time_to_first_failed


def test_cases(input_program_tree, inp, writer):
    AGI = 0
    # include default value
    index_withheld = 19
    inp[index_withheld] = 0
    AGI = AGI_calc(inp,cap_gain_ind, tot_inc_ind, char_ind, adj_to_inc_ind)
    #AGI = (inp[7] + inp[8] + inp[9] + inp[10] + inp[11] + inp[12] + inp[13] + inp[14] + inp[15] + inp[16])

    arr, features = xml_parser.xml_parser(input_program_tree,inp)

    filename =  "US_1040_testing_married_sep_schedule_A_4.txt"

    with open(filename, 'w') as out:
        out.write("Title:  US Federal 1040 Tax Form - 2020")
        out.write("\n\n")
        count = 0
        for i in range(len(arr)):
            out.write(features[i])
            out.write(" ")
            if(arr[i] == 0.00):
                out.write("")
            else:
                out.write(str(arr[i]))
            # other processing
            if(count > 6):
                out.write(" ;")
            out.write("\n")
            if(features[i] == 'S1_18a'):
                out.write("AlimRecipSSN: \n")
                out.write("AlimRecipName: \n")
            count += 1
        out.write("Your1stName:	 F, D. \n")
        out.write("YourLastName:   Smy \n")
        out.write("YourSocSec#: 	 109-11-1111 \n")
        out.write("Spouse1stName:  S, M \n")
        out.write("SpouseLastName:  Smy \n")
        out.write("SpouseSocSec#:   109-11-1112 \n")
        out.write("Number&Street:  1567 W. Hamptonshire \n")
        out.write("Apt#: \n")
        out.write("Town/City:	Springfield \n")
        out.write("State:   	IL \n")
        out.write("ZipCode:	62722\n")
        out.write("YourOccupat: Merchant\n")
        out.write("SpouseOccupat: Welder\n")
        out.close()
    ret = call(["../../bin/taxsolve_US_1040_2020", filename])

    tax_return = 0.0
    with open("US_1040_testing_married_sep_schedule_A_4_out.txt", 'r') as read_f:
        try:
            for line in read_f:
                if "L34" in line:
                    tax_return = float(line.split(" ")[2])
                elif "L37" in line:
                    tax_return = -1 * float(line.split(" ")[2])
        except ValueError as VE:
            tax_return = 0.0
    for i in range(len(inp)):
        if inp[i] == None:
            writer.write(",")
        else:
            writer.write("%s," % inp[i])
    return tax_return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--property", help='Property Number')
    parser.add_argument("--timeout", help='Time Budget in seconds')
    args = parser.parse_args()
    cap_gain_ind = [28,29,30]# 2020
    tot_inc_ind = [7,9,11,13,15,48]#2020
    char_ind = [73,74]#2020
    adj_to_inc_ind = [50,51,52,53,54,55,56,57,58,61,62,63]
    #AGI_index = [7,8,9,10,11,12,13,14,15,16]
    start_time = time.time()
 
    property = int(args.property)
    max_time = int(args.timeout)

    res, time_1_failed = property_generation(property, start_time, max_time)

    f = open("Results_debugging_property_" + str(property) + "_" + str(start_time).split(".")[0] + ".txt" , 'w')
    f.write("Results_debugging_property_" + str(property) + ": ")

    if(res == None):
        print("No test cases were generated!")
        f.write("No test cases were generated!")
        f.close()
    else:            
        total_size = len(res)
        false_size = res.count(False)
        true_size = res.count(True)
        if(false_size > 0):
            print("failed")
            f.write("failed\n") 
        else:
            print("passed")
            f.write("passed\n") 
        comp_time = time.time() - start_time
        print("Total Cases: " + str(total_size))
        print("False Cases: " + str(false_size))
        print("True Cases: " + str(true_size))
        print("Time to First Failure: " + str(time_1_failed))
        print("Computation Time: " + str(comp_time))
        f.write("Total Cases: " + str(total_size) + ", " ) 
        f.write("False Cases: " + str(false_size) + ", ")
        f.write("True Cases: " + str(true_size) + ", ")
        f.write("Time to First Failure: " + str(time_1_failed) + ", ")
        f.write("Computation Time: " + str(comp_time) + "\n")
        f.close()
