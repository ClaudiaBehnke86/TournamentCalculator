""" This module should be used to create a tournament
 """
import os
from datetime import timedelta
import itertools # for permutations of discipline order
import numpy as np

#some global variables
AGE_INP = ["U16", "U18", "U21", "Adults"] #the supported age catergories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"] # order does not matter -> permutations
#just a name
DIS_CHA = "Discipline change" # indicator of a change of a discipline
DIS_CHA_TIME = 30 #add the changeing time for the change betwenn disciplines in minutes

BREAK = "Break"
#BREAK_LENGTH = 30 # 30 min

def descition_matrix(cat_time_dict, av_time, tatami, break_t, breaktime, breaklength):
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
    cat_time_dict_new = np.array([[[None] * tatami] * len(permutations_list)] * DIS_CHA_TIME)
    pen_time_list = list(range(DIS_CHA_TIME//2, DIS_CHA_TIME+DIS_CHA_TIME//2))
    happiness = [x / 10.0 for x in range(0, 20)]

    time_max = np.array([[None] * len(pen_time_list)] * len(happiness))
    time_std = np.array([[None]  * len(pen_time_list)] * len(happiness))
    score = np.array([[None] * len(permutations_list) * len(pen_time_list)] * len(happiness))

    for pen_var_num, pen_var_t in enumerate(pen_time_list): #penalty time
        for j in range(0, loads.shape[1]): #permutaitons
            scheduled_jobs[pen_var_num][j], loads[pen_var_num][j], \
                cat_time_dict_new = distr_cat_alg(cat_time_dict, av_time, \
                    permutations_list[j], pen_var_t, tatami, break_t, breaktime, breaklength)
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

    #all unique values of min_id
    results, counts = np.unique(min_id, return_counts=True)
    most_abundand = dict(zip(results, counts))
    return scheduled_jobs, loads, most_abundand, min_id, \
        pen_time_list, happiness, min_score, cat_time_dict_new

def write_tour_file(tour_name,cat_par,cat_dict_day,i_tatami, days, final,start_time,breaktype):
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
    tour_file.write("Days: " + str(days) + "\n")
    if final is True:
        tour_file.write("Finalblock: YES \n")
    else:
        tour_file.write("Finallblock: NO \n")
    tour_file.write("Breaktype: " + str(breaktype) + "\n")
    tour_file.write("Startime: " + str(start_time.seconds) + "\n")

    for cat_name, par_num in cat_par.items():
        day = cat_dict_day[cat_name]
        tour_file.write(str(cat_name) +" "+ str(par_num) +" "+ str(day)+"\n")

    tour_file.close()

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
    dayss = tour_file.readline() # read in tatami line
    days_inp = dayss.split()
    days = int(days_inp[1])
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
    cat_dict_day = {} #stores day of each dict
    for line in tour_file: # Loop over lines and extract variables of interest
        line = line.strip()
        columns = line.split()
        if(columns[1] == "Duo" or columns[1] == "Show"):
            catname = columns[0] + " "+ columns[1] + " " + columns[2]
            j = int(columns[3])
            k = int(columns[4])
        else:
            catname = columns[0] + " "+ columns[1] + " " + columns[2] +" " + columns[3]
            j = int(columns[4])
            k = int(columns[5])
        cat_par[catname] = int(j)
        cat_dict_day[catname] = int(k)

    return cat_par, cat_dict_day, final, tatami, days, starttime, break_t


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
    weight_w16 = [32, 36, 40, 44, 48, 52, 57, 63, 64]

    weight_m = [56, 62, 69, 77, 85, 94, 95]
    weight_m18 = [46, 50, 55, 60, 66, 73, 81, 82]
    weight_m16 = [38, 42, 46, 50, 55, 60, 66, 73, 74]

    cat_team = {"Female", "Male", "Mixed"}

 

    cat_all = []
    for i in age_select: #Looping AgeCategories
        for j in dis_select: #Looping Disziplines
            if j in ("Duo", "Show"):
                for k in cat_team:
                    cat_all.append(i +" "+ j + " " + k)
            elif i == "U16":
                for k in weight_m16:
                    cat_all.append(i +" "+ j + " Male "+ str(k)+"kg")
                for k in weight_w16:
                    cat_all.append(i +" "+ j + " Female "+ str(k)+"kg")
            elif i == "U18":
                for k in weight_m18:
                    cat_all.append(i +" "+ j + " Male "+ str(k)+"kg")
                for k in weight_w18:
                    cat_all.append(i +" "+ j + " Female "+ str(k)+"kg")
            else:
                for k in weight_m:
                    cat_all.append(i +" "+ j + " Male "+ str(k)+"kg")
                for k in weight_w:
                    cat_all.append(i +" "+ j + " Female "+ str(k)+"kg")

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

    time_inp = {"U16 Fighting":timedelta(minutes=6, seconds=00),
                "U18 Fighting":timedelta(minutes=7, seconds=00),
                "U21 Fighting":timedelta(minutes=7, seconds=00),
                "Adults Fighting":timedelta(minutes=7, seconds=00),
                "U16 Duo":timedelta(minutes=5),
                "U18 Duo":timedelta(minutes=7),
                "U21 Duo":timedelta(minutes=7),
                "Adults Duo":timedelta(minutes=7),
                "U16 Show":timedelta(minutes=4),
                "U18 Show":timedelta(minutes=4),
                "U21 Show":timedelta(minutes=4),
                "Adults Show":timedelta(minutes=4),
                "U16 Jiu-Jitsu":timedelta(minutes=5),
                "U18 Jiu-Jitsu":timedelta(minutes=6),
                "U21 Jiu-Jitsu":timedelta(minutes=7),
                "Adults Jiu-Jitsu":timedelta(minutes=8)}
    #timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    for cat_name in dict_inp: #loop over dictionary
        par_num = int(dict_inp.get(cat_name)) #number of fights per catergory
        fight_num = 0 # reset counter
        if "Show" in cat_name:
            if final is True and par_num > 5:
                for keys in time_inp:
                    if keys in cat_name: #if name of Discipline is in string of categoroy:
                        cat_finals_dict[cat_name] = time_inp[keys]
                        final_time += time_inp[keys]*par_num
                fight_num = par_num
        else:
            if final is True and par_num > 5:
                fight_num = -1 #remove final
                for keys in time_inp:
                    if keys in cat_name: #if name of Discipline is in string of category:
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

    return cat_fights_dict, cat_finals_dict, cat_time_dict, \
        av_time, par_num_total, fight_num_total, tot_time, final_time

def distr_cat_alg(jobs, av_time, cur_per, cur_pen_time, tatami, break_t, breaktime, breaklength):
    '''
    Run the algorithm. Create List of dictionaries with,
    where each diszipline has its own dictionary. And fill
    it with the existing catergories Sort each disctiinary
    by size (longest competitions in beginning of list)

    Parameters
    ----------
    jobs
        dict of catergories that need to be distributed (dict)
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
        "block" ; "Individual" [str]
    '''
    jobs_new  = jobs.copy() #dict to have the parts entries
    distr_list = [] # List of dictionaries with, where each dizipline has its own dictionary
    loads = []      # List of list which stores the times per tatami as a list
    scheduled_jobs = [] # List of list which stores the names per tatami as a list
    time_needed = [] # list for calcuating the total needed times per discipline
    distr_sor_list = distr_list
    #import pdb; pdb.set_trace()
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
                if distr_sor_list[i][job].seconds > 0:
                    minload_tatami = minloadtatami(loads)
                    if break_t == "Individual":
                        if loads[minload_tatami] > breaktime.seconds and BREAK not in scheduled_jobs[minload_tatami] and len(scheduled_jobs[minload_tatami]) > 0 and scheduled_jobs[minload_tatami][-1] is not DIS_CHA:
                            if remove is True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t )< breaktime.seconds):
                                pass # ignore extra time
                            else:
                                scheduled_jobs[minload_tatami].append(BREAK)
                                loads[minload_tatami] += breaklength.seconds
                        scheduled_jobs[minload_tatami].append(job)
                        loads[minload_tatami] += distr_sor_list[i][job].seconds
                    elif break_t == "One Block":
                        if (loads[minload_tatami] + distr_sor_list[i][job].seconds) > breaktime.seconds and BREAK not in scheduled_jobs[minload_tatami] and len(scheduled_jobs[minload_tatami]) > 0 and scheduled_jobs[minload_tatami][-1] is not DIS_CHA:
                            if remove is True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t )< breaktime.seconds):
                                pass # ignore extra time
                            else:
                                job1 = job + " part 1 "
                                job2 = job + " part 2 "
                                time2 =  loads[minload_tatami] + distr_sor_list[i][job].seconds - breaktime.seconds
                                time1 =  distr_sor_list[i][job].seconds - time2

                                scheduled_jobs[minload_tatami].append(job1)
                                loads[minload_tatami] += time1
                                scheduled_jobs[minload_tatami].append(BREAK)
                                loads[minload_tatami] += breaklength.seconds
                                scheduled_jobs[minload_tatami].append(job2)
                                loads[minload_tatami] += time2
                                del jobs_new[job]
                                jobs_new[job1] = timedelta(seconds=time1)
                                jobs_new[job2] = timedelta(seconds=time2)

                        else:
                            scheduled_jobs[minload_tatami].append(job)
                            loads[minload_tatami] += distr_sor_list[i][job].seconds
                    else:
                        scheduled_jobs[minload_tatami].append(job)
                        loads[minload_tatami] += distr_sor_list[i][job].seconds
                if  remove is True:
                    loads[remove_tat] -= (extra_time_t) #removed the time to the tatami.
                    # if(cur_pen_time == 25 and cur_per == ('Fighting', 'Show', 'Duo', 'Jiu-Jitsu') ): print(remove_tat ," break removed ", scheduled_jobs[remove_tat] )
                    remove = False

            #add dis change after each distribution
            for tat_used in range(0, len(loads)):
                if scheduled_jobs[tat_used][-1] is not DIS_CHA and scheduled_jobs[tat_used][-1] is not BREAK:
                    scheduled_jobs[tat_used].append(DIS_CHA)
                    loads[tat_used] += cur_pen_time*60

    for tat_used in range(0, len(loads)):
        if scheduled_jobs[tat_used][-1] is DIS_CHA:
            scheduled_jobs[tat_used].pop()
            loads[tat_used] -= cur_pen_time*60
    #if(cur_pen_time == 25 and cur_per == ('Fighting', 'Show', 'Duo', 'Jiu-Jitsu') ):
    #   print("--- breaktime --- ",breaktime.seconds)

    return scheduled_jobs, loads, jobs_new

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

def changes_per_permutation(scheduled_jobs):
    '''calculates amount of discipline changes per permutation '''
    disz_changes = [0] * len(scheduled_jobs)
    for i, tat in enumerate(scheduled_jobs):  #results for each permutaton
        for cat in tat: #
            if cat == DIS_CHA:
                disz_changes[i] += 1
    return disz_changes
