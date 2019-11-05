""" This module should be used to create a tournament
But moslty it is used for me to have a hands on example for python
 """
import sys
import os
import time

from datetime import timedelta


def main():
    """ The main function """
    print("-------------------------")
    print("- Tournament Calculator -")
    print("-------------------------")
    print("Part 1 - Create tournament")
    print("")
    name = input("Please enter a name for the tournament: ")
    print("")

    check_tour(name)
    cat_par, final, par_count, tatami = read_in_file(name+".txt")

    print("")
    print("")
    print("----------------------------")
    print("-- Please check your input: -")
    print("----------------------------")
    print("")
    print("Catergories and Participants")

    print_dict(cat_par)
    i = 0

    while i < 1:
        check = input("Please type in name of category you want to correct \"OK\" to continue to next step ")
        if check in cat_par:
            print("Change catergory", check)
            par_count -= cat_par[check]
            new_val = int(check_num())
            cat_par[check] = new_val
            par_count += new_val
            print("Updated\nTo show list again type \"SHOW ALL\" ")
        elif check == "SHOW ALL":
            print_dict(cat_par)
        elif check == "OK":
            i = 1
        else:
            print("Catergory", check, "not known. Please try again")

    cat_fights_dict, cat_finals_dict, cat_time_dict = calculate_fight_time(cat_par, final, tatami)
    print("")
    print("----------------------------")
    print("----------- Part 3 ---------")
    print("---- distribute matches ----")
    print("----------------------------")
    print("")

    # Startime
    starttime = timedelta(hours=8, minutes=30)
    print("startime tournament ", starttime)
    print("Change time?")
    ch_time = check_yes_no()
    if ch_time == True:
        print("Please give NEW startime\nHours: ")
        h_new = -1
        while(h_new > 24 or h_new < 0):
            h_new = check_num()
            if(h_new > 24 or h_new < 0):
                print("Hours must between 0 and 24")
        print("Minutes:")
        m_new = -1
        while(m_new > 60 or m_new < 0):
            m_new = check_num()
            if(m_new > 60 or m_new < 0):
                print("Minutes must between 0 and 60")
        starttime = timedelta(hours=h_new, minutes=m_new)
    #########################
    sys.exit()

def check_yes_no():
    ''' Function to convert Yes No in a Bool'''
    check = False
    inp1 = input("Please type Yes / No : ")
    while check == False:
        if inp1 == "Yes":
            inp1 = True
            check = True
        elif inp1 == "No":
            inp1 = False
            check = True
        else:
            inp1 = input("Invaid! Please enter YES or NO")
    return inp1

def check_num():
    ''' Check if the input is a int'''
    user_input = input("Please enter a number ")
    try:
        val = int(user_input)
    except ValueError:
        print("Please enter a valid number")
    return val

def new_tour(name):
    ''' create a new tournament'''
    tour_file = open(name + ".txt", "w")
    print("How many tatmis will be there: ")
    tatami = check_num()
    print("")
    print("Will there be a final block")
    final = check_yes_no()

    print("Tournament:", name, "will be created with ", tatami, " tatamis")

    tour_file.write("Tournament: " + name + "\n")
    tour_file.write("Tatamis: " + str(tatami) + "\n")

    if final == True:
        print("Tournament has a final block")
        tour_file.write("Finalblock: YES \n")
    elif final == False:
        print("Tournament has NO final block")
        tour_file.write("Finallblock: NO \n")
    else:
        print("You should never see this. Something is VERY wrong here!!!")

    time.sleep(2)
    print("------------------------")
    print("--- Age catergories ---")
    print("------------------------")
    print("Which age catergories will compete?")
    new_inp = ["U16", "U18", "U21", "Adults"]
    print("Possible catergories", new_inp)
    print()
    print("Type: \"ALL\" to add all categories")

    i = 0
    new_select = []
    while i < len(new_inp):
        add_cat = input("Please type in name of category or type \
        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            new_select = new_inp.copy()
            print("All categories are added")
            break
        elif add_cat in new_inp:
            new_select.append(add_cat)
            print(add_cat, "added")
            i += 1
        elif add_cat == "OK":
            if i == 0:
                print("You must add minimum ONE Age category")
            else:
                break
        else:
            print("Categorie ", add_cat, "not known. Please try again")
    print("")
    print("The following age categories are added")
    print(new_select)
    time.sleep(2)

    print("")
    print("------------------------")
    print("--- Disciplines -------")
    print("------------------------")
    print("Which disciplines will compete?")
    dis_in = ["Fighting", "Duo", "Show", "Ne-Waza"]
    print("Possible categories:", dis_in)
    print("Type: ""ALL"" to add all categories")

    i = 0
    dis_sel = []
    while i < len(dis_in):
        add_cat = input("Please type in name of diszipline or type \
                        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            dis_sel = dis_in.copy()
            print("All disziplines are added")
            break
        elif add_cat in dis_in:
            dis_sel.append(add_cat)
            print(add_cat, "added")
            i += 1
        elif add_cat == "OK":
            if i == 0:
                print("You must add minimum ONE discipline")
            else:
                break
        else:
            print("Diszipline ", add_cat, "not known. Please try again")
    print("")
    print("The following disciplines are added:", dis_sel)
    #print(dis_sel)
    time.sleep(2)

    print("------------------------")
    print("calcualtion of weight categories")

    weight_w = [45, 48, 52, 57, 63, 70, 71]
    weight_w18 = [40, 44, 48, 52, 57, 63, 70, 71]
    weight_w16 = [32, 36, 40, 44, 48, 52, 57, 63, 61]

    weight_m = [56, 62, 69, 77, 85, 94, 95]
    weight_m18 = [46, 50, 55, 60, 66, 73, 81, 82]
    weight_m16 = [38, 42, 46, 50, 55, 60, 66, 73, 74]

    cat_team = {"Women", "Men", "Mixed"}

    cat_all = []
    for i in new_select: #Looping AgeCategories
        for j in dis_sel: #Looping Disziplines
            if(j == "Duo" or j == "Show"):
                for k in cat_team:
                    cat_all.append(i +" "+ j + " " + k)
            elif i == "U16":
                for k in weight_m16:
                    cat_all.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weight_w16:
                    cat_all.append(i +" "+ j + " Women "+ str(k)+"kg")
            elif i == "U18":
                for k in weight_m18:
                    cat_all.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weight_w18:
                    cat_all.append(i +" "+ j + " Women "+ str(k)+"kg")
            else:
                for k in weight_m:
                    cat_all.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weight_w:
                    cat_all.append(i +" "+ j + " Women "+ str(k)+"kg")
    time.sleep(2)
    print(" ")
    print("You have created the following categories")
    print(cat_all)
    print("In total ", len(cat_all), "catergories have been created for Tournament", name)
    print()
    time.sleep(2)

    print("----------------------------")
    print("- Part 2 - Add Competitors -")
    print("----------------------------")
    cat_par = {}#number of particpants
    print("Please add the number of participants for each category: ")
    for i in cat_all:
        print("Number of competitors in", i)
        inp = check_num()
        if inp <= 0:
            continue
        cat_par[i] = int(inp)

    time.sleep(1)

    for cat_name, par_num in cat_par.items():
        tour_file.write(str(cat_name) +" "+ str(par_num) + "\n")

    tour_file.close()

def check_tour(name):
    ''' compare test input with existing text files'''
    fname = name + ".txt"
    check = 0
    while check < 1:
        if os.path.isfile(fname):
            print("Tournament with name ", name, "already exist")
            print("What do you want to do?")
            print("1. Do you want to override? Type: \"OVERRIDE\"")
            print("!!! Overrinding will delete the exisiting file !!!")
            print("2. Do you want to use the datebase? Type \"USE\"")
            print("3. Do you want to use a different name? Type \"NEW\"")
            newf = input("Please type: \"OVERRIDE\" , \"USE\" or \"NEW\" : ")
            if newf == "OVERRIDE":
                print("New tournament will be created")
                check = 1
                new_tour(name)
                continue
            elif newf == "NEW":
                name = input("Please type new name ")
                fname = name + ".txt"
            elif newf == "USE":
                #read_in_file(fname)
                check = 1
            else:
                newf = input("This is not valid. Please try again. ")
        else:
            print("New tournament will be created")
            check = 1
            new_tour(name)

def read_in_file(fname):
    ''' Read in file'''
    tour_file = open(fname, "r")
    tour_file.readline() # Read and ignore header lines
    tatamis = tour_file.readline() # read in tatami line
    tatami_inp = tatamis.split()
    tatami = int(tatami_inp[1])
    #---
    final_t = tour_file.readline()
    final_inp = final_t.split()
    if final_inp[1] == "YES":
        final = True
    elif final_inp[1] == "NO":
        final = False
    else:
        print("something is wrong with ", final_inp)
    #------
    par_count = 0
    cat_par = {} #number of particpants

    for line in tour_file: # Loop over lines and extract variables of interest
        line = line.strip()
        columns = line.split()
        if(columns[1] == "Duo" or columns[1] == "Show"):
            catname = columns[0] + " "+ columns[1] + " " + columns[2]
            j = int(columns[3])
        else:
            catname = columns[0] + " "+ columns[1] + " " + columns[2] +" " + columns[3]
            j = int(columns[4])
        cat_par[catname] = int(j)
        par_count += int(j)
    time.sleep(1)
    print(cat_par)
    return cat_par, final, par_count, tatami

def print_dict(dict_inp):
    ''' Helper function to print full dict'''
    for cat_name, par_num in dict_inp.items():
        print(cat_name, par_num)

def calculate_fight_time(dict_inp, final, tatami):
    '''calculate the fight time '''
    
    fight_num_total = 0
    par_num_total = 0
    cat_fights_dict = {}  #categories & number of fights
    cat_finals_dict = {} #catergories of finale block & time
    cat_time_dict = {}  #categories & time

    tot_time = timedelta()
    final_time = timedelta()
    low_par_num = {0:0, 1:0, 2:3, 3:3, 4:6, 5:10, 6:9, 7:12} #fights for low numbers of participants
    # 8:11 from 8 on its always +2

    time_inp = {"Fighting":timedelta(minutes=5, seconds=30),
                "Duo":timedelta(minutes=7),
                "Show":timedelta(minutes=2),
                "NeWaza":timedelta(minutes=7)}
    #fight time.
    #timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    for cat_name in dict_inp: #loop over dictionary
        par_num = int(dict_inp.get(cat_name)) #number of fights per catergory
        fight_num = 0 # reset counter

        if final == True and par_num > 5:
            fight_num = -1 #remove final
            for keys in time_inp:
                if keys in cat_name: #if name of Discipline is in string of categoroy:
                    cat_finals_dict[cat_name] = time_inp[keys]
                    final_time += time_inp[keys]
        if par_num < 8:
            fight_num += low_par_num.get(par_num)
        else:
            fight_num += (par_num-8)*2 + 11

        fight_num_total += fight_num
        par_num_total += par_num #add all participants

        for keys in time_inp:
            if keys in cat_name: #if name of Discipline is in string of categoroy:
                cat_time_dict[cat_name] = time_inp[keys] * fight_num
                tot_time += time_inp[keys] * fight_num
                cat_fights_dict[cat_name] = fight_num

    fight_num_total += len(cat_finals_dict)

    print("")
    print("----------------------------")
    print("--------- Summary ----------")
    print("----------------------------")
   
    print("You have",
          par_num_total, "participants, which will fight ",
          fight_num_total, " matches in ",
          len(dict_inp), "categories with a total time fight time of (HH:MM:SS)",
          tot_time+final_time)
    print("You have", len(cat_finals_dict), "finals which will take", final_time)
    print("Average time per tatami will be", tot_time/int(tatami), "with", tatami, "tatamis")


    return cat_fights_dict, cat_finals_dict, cat_time_dict

main()
