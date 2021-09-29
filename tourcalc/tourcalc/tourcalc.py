""" This module should be used to create a tournament
 """
import sys
import os
import  time
#import pprint # needed for nice prints
from datetime import timedelta
import itertools # for permutations of discipline order
import random
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#some global variables
AGE_INP = ["U16", "U18", "U21", "Adults"] #the supported age catergories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"] # order does not matter -> permutations
#just a name
DIS_CHA = "Discipline change" # indicator of a change of a discipline
DIS_CHA_TIME = 30 #add the changeing time for the change betwenn disciplines in minutes

BREAK = "Break"
BREAK_TIME = 14400 # 4hrs after start of tournamement
BREAK_LENGTH = 30 # 30 min

def create_input(tournament_name):
    ''' to ask for the tournament parameters
    needs ot be called before main
    will ask user for all needed input
    '''

    name = tournament_name  # input("Please enter a name for the tournament: ")
    check_tour(name) #function to check if the tournament exists
    #read in file a file (alywas)
    cat_par_inp, final, tatami, starttime, break_t = read_in_file(name+".txt")

    # here one can ask for the
    cat_par = cat_par_inp
    return cat_par, tatami, final, starttime, break_t

def main(cat_par, tatami, final, starttime, break_t):
    """ the main fuction which calles the algortihm
    needs the input from create_input()
    
    Parameters
    ----------
    cat_par
        contains the number of athletes per category [dict]
    tatami
        number of competitaion areas [int]
    final
        doest the event have a final block [bool]
    stattime
         starttime of the tournamet (default 08:30) [timedelta]
    """

    cat_fights_dict, cat_finals_dict, cat_time_dict, \
        av_time, par_num_total, fight_num_total, \
        tot_time, final_time = calculate_fight_time(cat_par, final, tatami)

    #add an entry for penalty time in dict!
    cat_time_dict[DIS_CHA] = timedelta(minutes=DIS_CHA_TIME)

    #add an entry for the break time in dict!
    cat_time_dict[BREAK] = timedelta(minutes=BREAK_LENGTH)

    #########################
    #print("Scheduled Jobs: \n {} ".format(pprint.pformat(scheduled_jobs)))
    scheduled_jobs, loads, most_abundand = descition_matrix(
        cat_time_dict, av_time, tatami, break_t)

    print("There are ", len(most_abundand), "possible results ")
    test = {k: v for k, v in sorted(most_abundand.items(), key=lambda item: item[1], reverse=True)}
    print(test)


    pen_time = DIS_CHA_TIME//2 #choosen penalty time
    permut_num = int(list(test)[0]) #chosen permutation
    endtime = max(loads[pen_time][permut_num]) + 1800 # add for displaying the end_time in plot
    loads[pen_time][permut_num] = [x+starttime.seconds for x in loads[pen_time][permut_num]] #add starttime to loads
    loads[pen_time][permut_num] = [str(timedelta(seconds=x)) for x in loads[pen_time][permut_num]]
    

    plot_schedule(scheduled_jobs[pen_time][permut_num],
                  cat_time_dict, starttime.seconds,
                  loads[pen_time][permut_num],
                  endtime/3600+starttime.seconds/3600)

    return scheduled_jobs[pen_time][permut_num],cat_time_dict,endtime,loads[pen_time][permut_num]

def descition_matrix(cat_time_dict, av_time, tatami, break_t):
    ''' to find the best solution based on penalty and weighting of the resutls
    
    Parameters
    ----------
    cat_time_dict
        dictionary with catergories and time of eath catergory [dict]
    av_time
        reference time for average tatami [float] (sec)
    tatami
        number of tatamis [int]
    '''
    # run all with permutaitons of dis inp
    permutations_object = itertools.permutations(DIS_INP)
    permutations_list = list(permutations_object)

    #array for all possible outcomes
    scheduled_jobs = np.array([[[None] * tatami] * len(permutations_list)] * DIS_CHA_TIME)
    loads = np.array([[[None] * tatami] * len(permutations_list)] * DIS_CHA_TIME)
    pen_time_list = list(range(DIS_CHA_TIME//2, DIS_CHA_TIME+DIS_CHA_TIME//2))
    happiness = [x / 10.0 for x in range(0, 20)]

    time_max = np.array([[None] * len(pen_time_list)] * len(happiness))
    time_std = np.array([[None]  * len(pen_time_list)] * len(happiness))
    score = np.array([[None] * len(permutations_list) * len(pen_time_list)] * len(happiness))

    for pen_var_num, pen_var_t in enumerate(pen_time_list): #penalty time
        for j in range(0, loads.shape[1]): #permutaitons
            scheduled_jobs[pen_var_num][j], loads[pen_var_num][j] = distr_cat_alg(cat_time_dict, av_time, permutations_list[j], pen_var_t, tatami, break_t)
    min_id = np.array([[0.1] * len(happiness)] * len(pen_time_list))
    min_score = np.array([[0.1] * len(happiness)] * len(pen_time_list))

    for idx, loads_id in enumerate(loads):
        time_max = np.array([i.max() for i in loads_id])
        if tatami > 1:
            time_std = np.array([i.std(ddof=1) for i in loads_id])
        else:
            time_std = 1
        score = np.array([time_max + i * time_std for i in happiness])
        min_score[idx] = np.array([i.min() for i in score])
        min_id[idx] = np.array([i.argmin() for i in score])
    fig, ax = plt.subplots()

    im, _ = heatmap(min_id, pen_time_list, happiness, ax=ax,
                    cmap="YlGn", cbarlabel=" min_id")
    texts = annotate_heatmap(im, valfmt="{x:.0f}")
    ax.set_title("Happyness_value")
    plt.ylabel("time to change diszipline [min]")

    fig, ax2 = plt.subplots()
    im, _ = heatmap(min_score, pen_time_list, happiness, ax=ax2,
                    cmap="YlGn", cbarlabel=" min_score")
    texts = annotate_heatmap(im, valfmt="{x:.0f}")
    ax.set_title("Happyness_value")

    #all unique values of min_id
    results, counts = np.unique(min_id, return_counts=True)
    most_abundand = dict(zip(results, counts))
    return scheduled_jobs, loads, most_abundand

def break_type():
    '''
    Ask for the type of break
    - HELPER FUNCTION
    '''
    check = False
    inp1 = input("Please enter break type [no ; block ; individual ]")
    while check is False:
        if inp1 == "no":
            inp1 = no_break
            check = True
        elif inp1 == "block":
            inp1 = block
            check = True
        elif inp1 == "individual":
            inp1 = indi
            check = True
        else:
            inp1 = input("Invaid! Please enter break type [no ; block ; individual ] ")
    return inp1

def check_input(cat_par):
    '''function to correct input file
    
    Parameters
    ----------
    cat_par
        catergories and number of participants [dict]
    '''
    i = 0
    while i < 1:
        print_dict(cat_par)
        print("Please type in name of category you want to correct")
        check = input(" or \"OK\" to continue to next step ")
        if check in cat_par:
            print("Change catergory", check)
            new_val = int(check_num())
            cat_par[check] = new_val
            print("Updated\nTo show list again type \"SHOW ALL\" ")
        elif check == "SHOW ALL":
            print_dict(cat_par)
        elif check == "OK":
            i = 1
        else:
            print("Catergory", check, "not known. Please try again")
    return cat_par

def new_tour(tour_name,cat_par,i_tatami,final,start_time,breaktype):
    ''' create a new tournament file
    
    Parameters
    ----------
    name
        name of the tour nament [str]
    '''
    tour_file = open(tour_name + ".txt", "w")

    #write the file
    tour_file.write("Tournament: " + tour_name + "\n")
    tour_file.write("Tatamis: " + str(i_tatami) + "\n")
    if final is True:
        tour_file.write("Finalblock: YES \n")
    else:
        tour_file.write("Finallblock: NO \n")
    tour_file.write("Breaktype: " + str(breaktype) + "\n")
    tour_file.write("Startime: " + str(start_time.seconds) + "\n")

    for cat_name, par_num in cat_par.items():
        tour_file.write(str(cat_name) +" "+ str(par_num) + "\n")

    tour_file.close()

def check_tour(name):
    ''' compare test input with existing text files
    
    Parameters
    ----------
    name
        name of the tour nament [str]
    
    '''
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
            if name == "random":
                print("New tournament will be created")
                check = 1
                new_tour(name) #creates a new tournament
                continue
            else:
                newf = input("Please type: \"OVERRIDE\" , \"USE\" or \"NEW\" : ")
                if newf == "OVERRIDE":
                    print("New tournament will be created")
                    check = 1
                    new_tour(name) #creates a new tournament
                    continue
                if newf == "NEW":
                    name = input("Please type new name ")
                    fname = name + ".txt"
                elif newf == "USE":
                    check = 1
                else:
                    newf = input("This is not valid. Please try again. ")
        else:
            print("New tournament will be created")
            check = 1
            new_tour(name)  #creates a new tournament

def read_in_file(fname):
    ''' Read in file
     - HELPER FUNCTION
     
    Parameters
    ----------
    fname
        name of the tour nament [str]

    '''
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
    
    break_t_in = tour_file.readline() # read in break line
    break_tt = break_t_in.split()
    break_t = break_tt[1]
    #read in starttime
    starttimes = tour_file.readline() # read in tatami line
    starttime_inp = starttimes.split()
    starttime_sec = int(starttime_inp[1])
    starttime = timedelta(seconds=starttime_sec)
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
    return cat_par, final, tatami, starttime, break_t

def print_dict(dict_inp):
    ''' Helper function to print full dict
     - HELPER FUNCTION

    Parameters
    ----------
    dict_inp
        name of the dict

    '''
    for cat_name, par_num in dict_inp.items():
        print(cat_name, par_num)

def age_cat():
    ''' add age catergories for tournaments'''
    print("------------------------")
    print("--- Age catergories ---")
    print("------------------------")
    print("Which age catergories will compete?")
    print("Possible catergories ", AGE_INP)
    print()
    print("Type: \"ALL\" to add all categories ")

    i = 0
    age_select = []
    while i < len(AGE_INP):
        add_cat = input("Please type in name of category or type \
        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            age_select = AGE_INP.copy()
            print("All categories are added")
            break
        if add_cat in AGE_INP:
            age_select.append(add_cat)
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
    print(age_select)
    time.sleep(2)
    return age_select

def dis_cat():
    ''' add the pariciparting disziplines'''
    print("")
    print("------------------------")
    print("--- Disciplines -------")
    print("------------------------")
    print("Which disciplines will compete?")
    print("Possible categories:", DIS_INP)
    print("Type: ""ALL"" to add all categories")

    i = 0
    dis_select = []
    while i < len(DIS_INP):
        add_cat = input("Please type in name of diszipline or type \
                        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            dis_select = DIS_INP.copy()
            print("All disziplines are added")
            break
        if add_cat in DIS_INP:
            dis_select.append(add_cat)
            print(add_cat, "added")
            i += 1
        elif add_cat == "OK":
            if i == 0:
                print("You must add minimum ONE discipline")
            else:
                break
        else:
            print("Diszipline ", add_cat, "not known. Please try again")
    print("The following disciplines are added:", dis_select)
    return dis_select

def cal_cat(age_select, dis_select):
    '''calculation of weight categories
    
    Parameters
    -----------
    age_select
         selected age caterogries [list]
         
    dis_select
        selected disciplines [list]
           
    '''

    weight_w = [45, 48, 52, 57, 63, 70, 71]
    weight_w18 = [40, 44, 48, 52, 57, 63, 70, 71]
    weight_w16 = [32, 36, 40, 44, 48, 52, 57, 63, 61]

    weight_m = [56, 62, 69, 77, 85, 94, 95]
    weight_m18 = [46, 50, 55, 60, 66, 73, 81, 82]
    weight_m16 = [38, 42, 46, 50, 55, 60, 66, 73, 74]

    cat_team = {"Women", "Men", "Mixed"}

    cat_all = []
    for i in age_select: #Looping AgeCategories
        for j in dis_select: #Looping Disziplines
            if j in ("Duo", "Show"):
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
    
    return cat_all

def calculate_fight_time(dict_inp, final, tatami):
    '''calculate the fight time
    
    Parameters
    ----------
    dict_inp
        contains the number of athletes per category [dict]
    tatami
        number of competitaion areas [int]
    final
          does the event have a final block [bool]
    
    '''
    fight_num_total = 0
    par_num_total = 0
    cat_fights_dict = {}  #categories & number of fights
    cat_finals_dict = {} #catergories of finale block & time
    cat_time_dict = {}  #categories & time

    tot_time = timedelta()
    final_time = timedelta()
    low_par_num = {0:0, 1:0, 2:3, 3:3, 4:6, 5:10, 6:9, 7:11} #fights for low numbers of participants
    # 8:11 from 8 on its always +2

    time_inp = {"Fighting":timedelta(minutes=6, seconds=30),
                "Duo":timedelta(minutes=7),
                "Show":timedelta(minutes=3),
                "Jiu-Jitsu":timedelta(minutes=8)}
    #timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    for cat_name in dict_inp: #loop over dictionary
        par_num = int(dict_inp.get(cat_name)) #number of fights per catergory
        fight_num = 0 # reset counter
        if "Show" in cat_name:
            if final is True and par_num > 5:
                if keys in cat_name: #if name of Discipline is in string of categoroy:
                    cat_finals_dict[cat_name] = time_inp[keys]
                    final_time += time_inp[keys]*par_num
            fight_num = par_num
        else:
            if final is True and par_num > 5:
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


    av_time = tot_time/int(tatami)
    print("You have", par_num_total, "participants, which will fight ",
          fight_num_total, " matches in ",
          len(dict_inp), "categories with a total time fight time of (HH:MM:SS)",
          tot_time+final_time)
    print("You have", len(cat_finals_dict), "finals which will take", final_time)
    print("Optimal solution time per tatami will be", av_time, "with", tatami, "tatamis")

    return cat_fights_dict, cat_finals_dict, cat_time_dict, av_time, par_num_total, fight_num_total, tot_time, final_time

def distr_cat_alg(jobs, av_time, cur_per, cur_pen_time, tatami, break_t):
    '''
    Run the algorithm. Create List of dictionaries with, where each diszipline has its own dictionary. And fill it with the existing catergories Sort each disctiinary by size (longest competitions in beginning of list)
    
    Parameters
    ----------
    jobs
        list of catergories that need to be distributed (list)
    av_time
        reference time for average tatami (float [s])
    cur_per
        current order of disziplines [list]
    DIS_CHA_TIME
        pentaly time for changing a diszipline [fload [s]]
    DIS_CHA
        indicate change of diszipline [str]
    tatami
        number of tatamis [int]
    break_type
        "block" ; "indi" [str]
    '''

    distr_list = [] # List of dictionaries with, where each dsizipline has its own dictionary
    loads = []      # List of list which stores the times per tatami as a list
    scheduled_jobs = [] # List od list which stores the names per tatami as a list
    time_needed = [] # list for calcuating the total needed times per discipline
    distr_sor_list = distr_list

    #
    #print(" ----- ",cur_per," ----- ")
    # Step 1
    for i in  cur_per:
        distr_list.append({}) #add a new list for each diszipline
    for (key, value) in jobs.items():
        for i, j in enumerate(cur_per): #loop over all entries in the input
            if j in key: # Check if key is the same add pair to new dictionary
                distr_list[i][key] = value
    # Step 2
    for i, j in enumerate(distr_list): # sort individual list by lenth of catergories
        distr_sor_list[i] = {k: v for k, v in sorted(distr_list[i].items(),
                                                     key=lambda item: item[1], reverse=True)}
    par_tat_need = []
    par_tat_need.clear()
    for i, j in enumerate(distr_sor_list):
        time_needed.append(0)                 #add 0 as starting time for diszipline
        for (key, value) in distr_list[i].items():
            time_needed[i] += value.seconds
        par_tat_need.append(time_needed[i]/av_time.seconds-time_needed[i]//av_time.seconds)
      #  print("Tatamis needed for", cur_per[i], " : ",
      #      "{:.2f}".format(time_needed[i]/av_time.seconds))
      #  print("Time needed for", cur_per[i], " : ",
      #       "{:.2f}".format(time_needed[i]/3600))

    remove_tat = 0
    # Step 3
    for i, j in enumerate(distr_sor_list):
       # print(" --- next diszipline is ---  ",  DIS_INP[i] )
        if time_needed[i] != 0: #ignore empty disciplicnes
            extra_time_t = (1-par_tat_need[i])*av_time.seconds
            remove = False #to check extra time, if added time need to be later removed

            #Step a) creates all of "full" tatamis
            for _ in range(0, time_needed[i]//av_time.seconds): #creates number of full tatamis
                if len(loads) < tatami:
                   # print("a) i am creating a new tatami")
                    loads.append(0)           #create loads for tatamiss
                    scheduled_jobs.append([]) #create tatamis

            #Step b) checks if half empty tatami is needed.
            #(eith no tatami exists or we neeed more time than is left)
            #print("len(loads) ", len(loads))
            if len(loads) >= tatami: #max num of tatamis is reached
                #print("max num of tatamis is reached")
                pass
            elif len(loads) == 0: #if no tatmis would be created in step a)
                #print("if no tatmis would be created in step a)")
                loads.append(0)  #create loads for tatamiss
                scheduled_jobs.append([]) #create tatamis
            elif i == 0: #extra tatami is needed for first rounds
                #print("iextra tatami is needed for first rounds")
                scheduled_jobs.append([]) # add empty tatami
                loads.append(extra_time_t+cur_pen_time) #adds the time to the tatami
                remove = True
                remove_tat = len(scheduled_jobs)-1
            elif loads[remove_tat] > (extra_time_t-cur_pen_time): #extra tatami is needed
                #print("extra tatami is needed")
                scheduled_jobs.append([]) # add empty tatami
                loads.append(extra_time_t+cur_pen_time) #adds the time to the tatami
                remove = True
                remove_tat = len(scheduled_jobs)-1
            else:
                pass

            #Step c) distribute categories
            for job in distr_sor_list[i]:
                minload_tatami = minloadtatami(loads)
                
                if break_t == "indi":
                    if loads[minload_tatami] > BREAK_TIME and BREAK not in scheduled_jobs[minload_tatami] and len(scheduled_jobs[minload_tatami]) > 0 and scheduled_jobs[minload_tatami][-1] is not DIS_CHA:
                        if remove == True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t )< BREAK_TIME):
                            pass # ignore extra time
                        else:
                            scheduled_jobs[minload_tatami].append(BREAK)
                            loads[minload_tatami] += BREAK_LENGTH
                    scheduled_jobs[minload_tatami].append(job)
                    loads[minload_tatami] += distr_sor_list[i][job].seconds
                elif break_t == "block":
                     if loads[minload_tatami] + distr_sor_list[i][job].seconds > BREAK_TIME and BREAK not in scheduled_jobs[minload_tatami]:
                        if remove == True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t )< BREAK_TIME):
                            pass # ignore extra time
                        else:
                            job1 = job + "part 1 "
                            job2 = job + "part 2 "
                            time1 =  loads[minload_tatami] + distr_sor_list[i][job].seconds - BREAK_TIME
                            time2 = loads[minload_tatami] + distr_sor_list[i][job].seconds - BREAK_TIME
                            if(cur_pen_time == 25 and cur_per == ('Fighting', 'Show', 'Duo', 'Jiu-Jitsu') ):
                                print(job1," ", job2, " ", time1 , " " , time2)

                            scheduled_jobs[minload_tatami].append(job1)
                            scheduled_jobs[minload_tatami].append(BREAK)
                            scheduled_jobs[minload_tatami].append(job2)
                            
                            if(cur_pen_time == 25 and cur_per == ('Fighting', 'Show', 'Duo', 'Jiu-Jitsu') ):
                                print(scheduled_jobs[minload_tatami])
                else:
                    scheduled_jobs[minload_tatami].append(job)
                    loads[minload_tatami] += distr_sor_list[i][job].seconds
            if  remove is True:
                loads[remove_tat] -= (extra_time_t) #removed the time to the tatami.
                # if(cur_pen_time == 25 and cur_per == ('Fighting', 'Show', 'Duo', 'Jiu-Jitsu') ): print(remove_tat ," break removed ", scheduled_jobs[remove_tat] )
                remove = False

            #add dis change after each distributuion
            for tat_used in range(0, len(loads)):
                if scheduled_jobs[tat_used][-1] is not DIS_CHA and scheduled_jobs[tat_used][-1] is not BREAK:
                    scheduled_jobs[tat_used].append(DIS_CHA)
                    loads[tat_used] += cur_pen_time*60

    for tat_used in range(0, len(loads)):
        if scheduled_jobs[tat_used][-1] is DIS_CHA:
            scheduled_jobs[tat_used].pop()
            loads[tat_used] -= cur_pen_time*60
    return scheduled_jobs, loads

def minloadtatami(loads):
    """Find the tatami with the minimum load.
    Break the tie of tatamis having same load on
    first come first serve basis.
    """
    minload = min(loads)
    for tat_min, load in enumerate(loads):
        if load == minload:
            return tat_min
        else:
            pass

def autolabel(cat_draw, rects, i, l_x):
    """ Attach labels with disziplines.
     - HELPER FUNCTION DRAW
    """
    for lab, rect in enumerate(rects):
        text = cat_draw[i][lab]
        if text != 0:
            text_sep = text.replace(" ", " \n")
            l_x.text(rect.get_x() + rect.get_width() / 2.,
                     rect.get_y() + rect.get_height() / 2.,
                     text_sep, ha='center', va='center')

def sumlabel(rects, endtime, loads, l_x):
    '''creates lables for each catergory to dosply them in plot
    - HELPER FUNCTION DRAW
    '''
    for lab, rect in enumerate(rects):
        l_x.text(rect.get_x() + rect.get_width() / 2., endtime,
                 loads[lab], ha='center', va='center')

def plot_schedule(scheduled_jobs, cat_time_dict, start_time, loads, endtime):
    '''creates lables for each catergory to disply them in plot - HELPER FUNCTION DRAW'''
    max_col = len(scheduled_jobs[0])
    for row in scheduled_jobs:
        row_length = len(row)
        if row_length > max_col:
            max_col = row_length
        time_draw = []
        cat_draw = []
    for col_index in range(max_col):
        time_draw.append([])
        cat_draw.append([])
        for row in scheduled_jobs:
            if col_index < len(row):
                job = cat_time_dict.get(row[col_index])
                time_draw[col_index].append(job.seconds/3600)
                cat_draw[col_index].append(row[col_index])
            else:
                time_draw[col_index].append(0)
                cat_draw[col_index].append(0)

    labels = list(range(0, len(time_draw[0])))
    fig, l_x = plt.subplots()
    width = 0.8       # the width of the bars: can also be len(x) sequence
    time_draw_helper = [start_time/3600]*len(time_draw[0])

    for i, dis in enumerate(time_draw):
        if i == 0:
            rect = l_x.bar(labels, time_draw[i], width, yerr=0, bottom=time_draw_helper, label='')
            autolabel(cat_draw, rect, i, l_x)
            sumlabel(rect, endtime, loads, l_x)
        else:
            time_draw_helper = [sum(x) for x in zip(time_draw_helper, time_draw[i-1])]
            #create helper as sum over time_draw n-1
            rect = l_x.bar(labels, time_draw[i], width, yerr=0, bottom=time_draw_helper, label='')
            autolabel(cat_draw, rect, i, l_x)

    l_x.set_ylabel('Time [hh:min]')
    l_x.set_xlabel('Tatami')
    #  plt.show()
    return fig

def changes_per_permutation(scheduled_jobs):
    '''calculates amount of discipline changes per permutation '''
    disz_changes = [0] * len(scheduled_jobs)
    for i, tat in enumerate(scheduled_jobs):  #results for each permutaton
        for cat in tat: #
            if cat == DIS_CHA:
                disz_changes[i] += 1
    return disz_changes

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels. - HELPER FUNCTION DRAW

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap. - HELPER FUNCTION DRAW

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

#a,b,c,d,e = create_input()
#main(a,b,c,d,e)
