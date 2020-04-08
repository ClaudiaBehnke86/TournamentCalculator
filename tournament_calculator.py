""" This module should be used to create a tournament
But mostly it is used for me to have a hands on example for python
 """
import sys
import os
import  time
import pprint # needed for nice prints
from datetime import timedelta
import matplotlib.pyplot as plt
import itertools # for permutations of discipline order
import statistics # for standard devitation (to desicde which order is the best)
def main():
    """ The main function """
    print("-------------------------")
    print("- Tournament Calculator -")
    print("Part 1 - Create tournament")
    print("-------------------------")
    print("")
    name = input("Please enter a name for the tournament: ")
    print("")

    age_inp = ["U16", "U18", "U21", "Adults"] #the supported age catergories
    #dis_inp = ["Ne-Waza", "Fighting", "Duo", "Show"] #the supported disciplines
    #dis_inp = ["Fighting", "Duo", "Show","Ne-Waza"] #the supported disciplines
    dis_inp = ["Duo", "Show","Ne-Waza","Fighting"] # crashes...
    ### if you modify this, you will also need to change calculate_fight_time()

    check_tour(name, age_inp, dis_inp) #function to check if the tournament exists
    cat_par_inp, final, tatami = read_in_file(name+".txt")

    print("")
    print("")
    print("----------------------------")
    print("----------- Part 2 ---------")
    print("-- Please check your input: -")
    print("----------------------------")
    print("")
    print("Catergories and Participants")
    cat_par = check_input(cat_par_inp)
    cat_fights_dict, cat_finals_dict, cat_time_dict, av_time = calculate_fight_time(cat_par, final, tatami)
    starttime = starttime_calc()
    print("")
    print("----------------------------")
    print("----------- Part 3 ---------")
    print("---- distribute matches ----")
    print("----------------------------")
    print("")

    
    #########################
    
   
    #print("Scheduled Jobs: \n {} ".format(pprint.pformat(scheduled_jobs)))
    
    #####
    # run all with permutaitons of dis inp
    permutations_object = itertools.permutations(dis_inp)
    permutations_list = list(permutations_object)
    
    scheduled_jobs = [None] * len(permutations_list)
    loads =  [None] * len(permutations_list)
    loads_dev =  [None] * len(permutations_list)
    endtime_planned =  [None] * len(permutations_list)
    disz_changes =  [None] * len(permutations_list)

    for i, j in enumerate(permutations_list):
        #print(i, " i: j ", j)
        scheduled_jobs[i], loads[i], endtime_planned[i], disz_changes[i] = lpt_algorithm(cat_time_dict, av_time, permutations_list[i])
        loads_dev[i] = statistics.stdev(loads[i])
        
    # shortes endtime
    indexes_min_endtime= [i for i, x in enumerate(endtime_planned) if x == min(endtime_planned)]
    print("min enddime ", indexes_min_endtime)
    print("Shortest endtime will be after " , "{:.2f}".format(min(endtime_planned)/3600) , " hrs ")
    
    #check for standarddeviation
    loads_dev_min = []
    for i in indexes_min_endtime:
        loads_dev_min.append(loads_dev[i])
        print(i ," : " ,permutations_list[i])
    
    indexes= [i for i, x in enumerate(loads_dev_min) if x == min(loads_dev_min)]
    

    
    n = endtime_planned.index(min(endtime_planned))
    
    print(loads_dev_min)
    
    #m = endtime_planned.index(min(loads_dev))
    #print("Shortest endtime will be after " , "{:.2f}".format(min(endtime_planned)/3600) , " hrs ")
        
    indexes= [i for i, x in enumerate(disz_changes) if x == min(disz_changes)]
    print(indexes)
   
    #print(endtime_planned)
    
    #print(loads_dev)
    #loads_dev.index(min(loads_dev))
    
    
    #print("End time: {}".format(pprint.pformat(loads[n])))
    print("----------------------------")
    print("----------- Part 4 ---------")
    print("------ draw schedule  ------")
    print("----------------------------")
    print("")
    loads[n] = [x+starttime.seconds for x in loads[n]] #add starttime to loads
    loads[n] = [str(timedelta(seconds=x)) for x in loads[n]]
    plot_schedule(scheduled_jobs[n], cat_time_dict, starttime.seconds,
                  loads[n], endtime_planned[n]/3600+starttime.seconds/3600)


    sys.exit()

def check_yes_no():
    ''' Function to convert YES NO in a Bool'''
    check = False
    inp1 = input("Please type YES / NO : ")
    while check is False:
        if inp1 == "YES":
            inp1 = True
            check = True
        elif inp1 == "NO":
            inp1 = False
            check = True
        else:
            inp1 = input("Invaid! Please enter YES or NO ")
    return inp1

def check_num():
    ''' Check if the input is an int'''
    user_input = input("Please enter a number ")
    while True:
        try:
            val = int(user_input)
            return val
        except ValueError:
            print("This is not a number. Please enter a valid number")
            user_input = input("Please enter a number ")

def starttime_calc():
    ''' change the startime of the tournament'''
    starttime = timedelta(hours=8, minutes=30)
    print("startime tournament ", starttime)
    print("Change time?")
    ch_time = check_yes_no()
    if ch_time is True:
        h_new = print("Please give NEW startime\nHours: ")
        while(h_new > 24 or h_new < 0):
            h_new = check_num()
            if(h_new > 24 or h_new < 0):
                print("Hours must between 0 and 24")
        m_new = print("Minutes: ")
        while(m_new > 60 or m_new < 0):
            m_new = check_num()
            if(m_new > 60 or m_new < 0):
                print("Minutes must between 0 and 60")
        starttime = timedelta(hours=h_new, minutes=m_new)
    return starttime

def check_input(cat_par):
    '''function to correct input file '''
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

def new_tour(name, age_inp, dis_inp):
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

    if final is True:
        print("Tournament has a final block")
        tour_file.write("Finalblock: YES \n")
    else:
        print("Tournament has NO final block")
        tour_file.write("Finallblock: NO \n")

    age_select = age_cat(age_inp) # select age catergories
    dis_select = dis_cat(dis_inp) # select disxiplines
    cat_all = cal_cat(age_select, dis_select) # calculate catergories

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

def check_tour(name, age_inp, dis_inp):
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
                new_tour(name, age_inp, dis_inp) #creates a new tournament
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
            new_tour(name, age_inp, dis_inp)  #creates a new tournament

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
    return cat_par, final, tatami

def print_dict(dict_inp):
    ''' Helper function to print full dict'''
    for cat_name, par_num in dict_inp.items():
        print(cat_name, par_num)

def age_cat(age_inp):
    ''' add age catergories for tournaments'''
    print("------------------------")
    print("--- Age catergories ---")
    print("------------------------")
    print("Which age catergories will compete?")
    print("Possible catergories ", age_inp)
    print()
    print("Type: \"ALL\" to add all categories ")

    i = 0
    age_select = []
    while i < len(age_inp):
        add_cat = input("Please type in name of category or type \
        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            age_select = age_inp.copy()
            print("All categories are added")
            break
        if add_cat in age_inp:
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

def dis_cat(dis_inp):
    ''' add the pariciparting disziplines'''
    print("")
    print("------------------------")
    print("--- Disciplines -------")
    print("------------------------")
    print("Which disciplines will compete?")
    print("Possible categories:", dis_inp)
    print("Type: ""ALL"" to add all categories")

    i = 0
    dis_select = []
    while i < len(dis_inp):
        add_cat = input("Please type in name of diszipline or type \
                        \"OK\" to continue to next step ")
        if add_cat == "ALL":
            dis_select = dis_inp.copy()
            print("All disziplines are added")
            break
        if add_cat in dis_inp:
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
    '''calculation of weight categories'''
    print("------------------------")
    print("calculation of weight categories")

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
    print(" ")
    print("You have created the following categories")
    print(cat_all)
    print("In total ", len(cat_all), "catergories have been created for Tournament")
    print()
    return cat_all

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
    
    #fight_num_show

    time_inp = {"Fighting":timedelta(minutes=6, seconds=30),
                "Duo":timedelta(minutes=7),
                "Show":timedelta(minutes=2),
                "Ne-Waza":timedelta(minutes=8)}
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

    print("")
    print("----------------------------")
    print("--------- Summary ----------")
    print("----------------------------")

    av_time = tot_time/int(tatami)
    print("You have", par_num_total, "participants, which will fight ",
          fight_num_total, " matches in ",
          len(dict_inp), "categories with a total time fight time of (HH:MM:SS)",
          tot_time+final_time)
    print("You have", len(cat_finals_dict), "finals which will take", final_time)
    print("Average time per tatami will be", av_time, "with", tatami, "tatamis")

    return cat_fights_dict, cat_finals_dict, cat_time_dict, av_time

def lpt_algorithm(jobs, av_time, dis_inp):
    """Run the algorithm:
    1. Create List of dictionaries with, where each diszipline has its own dictionary.
       And fill it with the existing catergories
    2. Sort each disctiinary by size (longest competitions in beginning of list)
    3.
    """
    distr_list = [] # List of dictionaries with, where each dsizipline has its own dictionary
    loads = []      # List of list which stores the times per tatami as a list
    scheduled_jobs = [] # List od list which stores the names per tatami as a list
    ftime = []          # List which stores the total times per discipline
    distr_sor_list = distr_list

    # Step 1
    for i in dis_inp:
        distr_list.append({}) #add a new list for each diszipline
    for (key, value) in jobs.items():
        for i, j in enumerate(dis_inp): #loop over all entries in the input
            if j in key: # Check if key is the same add pair to new dictionary
                distr_list[i][key] = value
    # Step 2
    for i, j in enumerate(distr_list):
        distr_sor_list[i] = {k: v for k, v in sorted(distr_list[i].items(),
                                                     key=lambda item: item[1], reverse=True)}
    
    time_needed = [] # list for calcuating the total needed times per discipline
    for i, j in enumerate(distr_sor_list):
        time_needed.append(0)                 #add 0 as starting time for diszipline
        for (key, value) in distr_list[i].items():
            time_needed[i] += value.seconds
        #print("Tatamis needed for", dis_inp[i], " : ",
        #    "{:.2f}".format(time_needed[i]/av_time.seconds))
        #print("Time needed for", dis_inp[i], " : ",
        #    "{:.2f}".format(time_needed[i]/3600))
    time_needed = list(filter(lambda num: num != 0, time_needed))
    
    disz_changes = 0
    # Step 3
    for i, j in enumerate(distr_sor_list):
        ftime.append(0)                 #add 0 as starting time for diszipline
        for (key, value) in distr_list[i].items():
            ftime[i] += value.seconds
        if ftime[i] != 0:
            extra_time = (1-((ftime[i]/av_time.seconds)-(ftime[i]//av_time.seconds)))*av_time.seconds
            for tat_add in range(0, ftime[i]//av_time.seconds):
                loads.append(0)           #create loads for tatamiss
                scheduled_jobs.append([]) #create tatamis
            remove = False #to check extra time, if added time need to be later removed
            if  len(loads) > 0 and min(loads) < extra_time:
                scheduled_jobs.append([])
                if i <= len(time_needed):
                    loads.append(extra_time+2000) #adds the time to the tatami.
                    disz_changes += 1
                    remove = True
                else: #if last discipline, no extra time is needed
                    loads.append(0)
            if len(loads) == 0:
                loads.append(0)           #create loads for tatamiss
                scheduled_jobs.append([]) #create tatamis
            for job in distr_sor_list[i]:
                minload_tatami = minloadtatami(loads)
                scheduled_jobs[minload_tatami].append(job)
                loads[minload_tatami] += distr_sor_list[i][job].seconds
            if  remove is True:
                loads[len(loads)-1] -= (extra_time+2000) #removed the time to the tatami.
                remove = False

    endtime_planned = max(loads) + 1800 # for displaying the end_time in plot
    return scheduled_jobs, loads, endtime_planned , disz_changes

def minloadtatami(loads):
    """Find the tatami with the minimum load.
    Break the tie of tatamis having same load on
    first come first serve basis.
    """
    minload = min(loads)
    for tat_min, load in enumerate(loads):
        if load == minload:
            return tat_min

def autolabel(cat_draw, rects, i, l_x):
    """ Attach labels with disziplines."""
    for lab, rect in enumerate(rects):
        text = cat_draw[i][lab]
        if text != 0:
            text_sep = text.replace(" ", " \n")
            l_x.text(rect.get_x() + rect.get_width() / 2.,
                     rect.get_y() + rect.get_height() / 2.,
                     text_sep, ha='center', va='center')

def sumlabel(rects, endtime_planned, loads, l_x):
    '''creates lables for each catergory to dosply them in plot'''
    for lab, rect in enumerate(rects):
        l_x.text(rect.get_x() + rect.get_width() / 2., endtime_planned,
                 loads[lab], ha='center', va='center')

def plot_schedule(scheduled_jobs, cat_time_dict, start_time, loads, endtime_planned):
    '''creates lables for each catergory to dosply them in plot'''
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
               # print("job ", row[col_index], " was appended as job no ",
                        #col_index , " to tatami ", row , "with ", job)
                del cat_time_dict[row[col_index]]
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
            sumlabel(rect, endtime_planned, loads, l_x)
        else:
            time_draw_helper = [sum(x) for x in zip(time_draw_helper, time_draw[i-1])]
            #create helper as sum over time_draw n-1
            rect = l_x.bar(labels, time_draw[i], width, yerr=0, bottom=time_draw_helper, label='')
            autolabel(cat_draw, rect, i, l_x)

    l_x.set_ylabel('Time [hh:min]')
    plt.show()

main()
