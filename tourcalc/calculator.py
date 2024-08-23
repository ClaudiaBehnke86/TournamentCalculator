""" This module should be used to create a tournament

it does all the mathematics and return the right order of the categories
"""

from datetime import timedelta
import itertools  # for permutations of discipline order
import pandas as pd
import numpy as np


# some global variables
AGE_INP = ["U10", "U12", "U14", "U16", "U18", "U21", "Adults", "Master"]  # the supported age divisions
# order does not matter -> permutations
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting", "Jiu-Jitsu NoGi"]  # supported disciplines
# just a name
DIS_CHA = "Discipline change"  # indicator of a change of a discipline
# add the changing time for the change between disciplines in minutes
DIS_CHA_TIME = 30

BREAK = "Break"


def descition_matrix(cat_time_dict,
                     av_time,
                     tatami,
                     break_t,
                     breaktime,
                     breaklength,
                     max_tatamis_per_discipline):
    ''' to find the best solution based on penalty and weighting of the results

    Parameters
    ----------
    cat_time_dict
        dictionary with categories and time of each category [dict]
    av_time
        reference time for average tatami [float] (sec)
    tatami
        number of tatamis [int]
    break_t
        type of the break that is used [individual, block, no break]
    breaktime
        time when the break should happen [dateime]
    breaklength
        length of the break [datetime]

    '''
    # run all with permutations of dis_inp
    permutations_object = itertools.permutations(DIS_INP)
    permutations_list = list(permutations_object)

    # array for all possible outcomes
    scheduled_jobs = np.array([[[None] * tatami] * len(permutations_list)] * DIS_CHA_TIME)
    loads = np.array([[[None] * tatami] * len(permutations_list)] * DIS_CHA_TIME)
    cat_time_dict_new = np.array([[None] * len(permutations_list)] * DIS_CHA_TIME)
    pen_time_list = list(range(DIS_CHA_TIME // 2, DIS_CHA_TIME+DIS_CHA_TIME // 2))
    happiness = [x / 10.0 for x in range(0, 20)]

    time_max = np.array([[None] * len(pen_time_list)] * len(happiness))
    time_std = np.array([[None] * len(pen_time_list)] * len(happiness))
    score = np.array([[None] * len(permutations_list) * len(pen_time_list)] * len(happiness))

    for pen_var_num, pen_var_t in enumerate(pen_time_list):  # penalty time
        for j in range(0, loads.shape[1]):  # permutations
            scheduled_jobs[pen_var_num][j], loads[pen_var_num][j], \
                cat_time_dict_new[pen_var_num][j] \
                = distr_cat_alg(cat_time_dict, av_time,
                                permutations_list[j],
                                pen_var_t, tatami,
                                break_t, breaktime,
                                breaklength, max_tatamis_per_discipline)

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

    # all unique values of min_id
    results, counts = np.unique(min_id, return_counts=True)
    most_abundand = dict(zip(results, counts))
    return scheduled_jobs, most_abundand, min_id, \
        pen_time_list, happiness, min_score, cat_time_dict_new


def write_tour_file(tour_name,
                    df,
                    i_tatami,
                    days,
                    final,
                    start_time,
                    date,
                    break_t):
    ''' create a new tournament file

    Parameters
    ----------
    tour_name
        name of the tournament [str]
    cat_par
        dict that links the category to
        a number of participants [dict (string -> int)]
    cat_dict_day
        dict that links the category to a day [dict (string -> int)]
    i_tatami
        number of tatamis [int]
    days
        number of days [int]
    final
        does the event have a final block [bool]
    start_time
        time when the event should happen [dateime]
    date
        date of the first day of the event [dateime]
    break_t
        type of the break that is used [individual, block, no break]
    '''
    tour_file = open(tour_name + ".csv", "w")

    # write the file
    tour_file.write("categories;participants;day\n")
    tour_file.write("tatamis;" + str(i_tatami) + "\n")
    tour_file.write("days;" + str(days) + "\n")
    if final is True:
        tour_file.write("finalblock;YES\n")
    else:
        tour_file.write("finalblock;NO\n")
    tour_file.write("breaktype;" + str(break_t) + "\n")
    tour_file.write("startime;" + str(start_time) + "\n")
    tour_file.write("date;" + str(date) + "\n")
    df.to_csv(tour_file, mode='a', index=False, header=False, sep=';')
    tour_file.close()
    return tour_file


def read_in_file(fname):
    ''' Read in file
     - HELPER FUNCTION TO READ IN THE CSV FILE

    Parameters
    ----------
    fname
        name of the tournament [str]

    '''
    tour_file = pd.read_csv(fname, sep=';')
    tour_file.fillna(0, inplace=True)
    tatami = int(tour_file['participants'][tour_file['categories'] == 'tatamis'].values[0])
    days = int(tour_file['participants'][tour_file['categories'] == 'days'].values[0])
    final_inp = str(tour_file['participants'][tour_file['categories'] == 'finalblock'].values[0])
    final = bool(final_inp == 'YES')
    break_t = str(tour_file['participants'][tour_file['categories'] == 'breaktype'].values[0])
    starttime = str(tour_file['participants'][tour_file['categories'] == 'startime'].values[0])
    date = str(tour_file['participants'][tour_file['categories'] == 'date'].values[0])
    tour_file_data = tour_file[6:].copy()
    tour_file_data['day'] = tour_file_data['day'].astype(int)
    tour_file_data['participants'] = tour_file_data['participants'].astype(int)
    cat_par = tour_file_data[
        ['participants', 'categories']
    ].set_index('categories').to_dict()['participants']
    cat_dict_day = tour_file_data[
        ['day', 'categories']
    ].set_index('categories').to_dict()['day']

    return cat_par, cat_dict_day, final, tatami, days, starttime, break_t, date


def cal_cat(age_select, dis_select):
    '''calculation of weight categories

    Parameters
    -----------
    age_select
        selected age divisions [list]
    dis_select
        selected disciplines [list]
    '''

    weight_w = ['-45', '-48', '-52', '-57', '-63', '-70', '+70']
    weight_w18 = ['-40', '-44', '-48', '-52', '-57', '-63', '-70', '+70']
    weight_w16 = ['-32', '-36', '-40', '-44', '-48', '-52', '-57', '-63', '+63']
    weight_w14 = ['-25', '-28', '-32', '-36', '-40', '-44', '-48', '-52', '-57', '+57']
    weight_w12 = ['-22', '-25', '-28', '-32', '-36', '-40', '-44', '-48', '+48']
    weight_w10 = ['-20', '-22', '-25', '-28', '-32', '-36', '-40', '+40']

    weight_m = ['-56', '-62', '-69', '-77', '-85', '-94', '+94']
    weight_m18 = ['-48', '-52', '-56', '-62', '-69', '-77', '-85', '+85']
    weight_m16 = ['-40', '-44', '-48', '-52', '-56', '-62', '-69', '-77', '+77']
    weight_m14 = ['-32', '-36', '-40', '-44', '-48', '-52', '-56', '-62', '-69', '+69']
    weight_m12 = ['-25', '-28', '-32', '-36', '-40', '-44', '-48', '-52', '+52']
    weight_m10 = ['-22', '-25', '-28', '-32', '-36', '-40', '-44', '+44']

    cat_team = {"Women", "Men", "Mixed", "Open"}

    cat_all = []
    for i in age_select:  # Looping AgeDivisions
        for j in dis_select:  # Looping Disciplines
            if j in ("Duo", "Show"):
                for k in cat_team:
                    if i != "Master":
                        cat_all.append(i + " " + j + " " + k)
                    if i == "Master":
                        for n in ["M1", "M2", "M3", "M4"]:
                            cat_all.append(i + " "+n + " " + j + " " + k)
            if i == "U10":
                for k in weight_m10:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w10:
                    cat_all.append(i + " " + j + " Women " + k + " kg")
            elif i == "U12":
                for k in weight_m12:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w12:
                    cat_all.append(i + " " + j + " Women " + k + " kg")
            elif i == "U14":
                for k in weight_m14:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w14:
                    cat_all.append(i + " " + j + " Women " + k + " kg")
            elif i == "U16":
                for k in weight_m16:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w16:
                    cat_all.append(i + " " + j + " Women " + k + " kg")
            elif i == "U18":
                for k in weight_m18:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w18:
                    cat_all.append(i + " " + j + " Women " + k + " kg")
            elif i == "Master":
                for n in ["M1", "M2", "M3", "M4"]:
                    for k in weight_m:
                        cat_all.append(i + " "+n + " " + j + " Men " + k + " kg")
                    for k in weight_w:
                        cat_all.append(i + " "+n + " " + j + " Women " + k + " kg")
            else:
                for k in weight_m:
                    cat_all.append(i + " " + j + " Men " + k + " kg")
                for k in weight_w:
                    cat_all.append(i + " " + j + " Women " + k + " kg")

    return cat_all


def calculate_fight_time(dict_inp, final, bronze_final, ms_mode):
    '''calculate the fight time

    Parameters
    ----------
    dict_inp
        contains the number of athletes per category [dict]
    tatami
        number of competition areas [int]
    final
        does the event have a final block [bool]
    ms_mode
        add an extra fight for bronze[bool]

    '''
    fight_num_total = 0
    par_num_total = 0
    cat_fights_dict = {}  # categories & number of fights
    cat_finals_dict = {}  # categories of finale block & time
    cat_time_dict = {}  # categories & time
    cat_bfinals_dict = {}  # categories of bronze finale block & time

    tot_time = timedelta()
    final_time = timedelta()
    bfinal_time = timedelta()
    # fights for low numbers of participants
    low_par_num = {0: 0, 1: 0, 2: 3, 3: 3, 4: 6, 5: 10, 6: 9, 7: 11}
    # 8:11 from 8 on its always +2

    time_inp = {
                "U10 Fighting": timedelta(minutes=5, seconds=00),
                "U12 Fighting": timedelta(minutes=5, seconds=00),
                "U14 Fighting": timedelta(minutes=6, seconds=00),
                "U16 Fighting": timedelta(minutes=6, seconds=00),
                "U18 Fighting": timedelta(minutes=7, seconds=00),
                "U21 Fighting": timedelta(minutes=7, seconds=00),
                "Adults Fighting": timedelta(minutes=7, seconds=00),
                "Master M1 Fighting": timedelta(minutes=6, seconds=00),
                "Master M2 Fighting": timedelta(minutes=6, seconds=00),
                "Master M3 Fighting": timedelta(minutes=6, seconds=00),
                "Master M4 Fighting": timedelta(minutes=6, seconds=00),
                "U10 Duo": timedelta(minutes=0, seconds=45),
                "U12 Duo": timedelta(minutes=0, seconds=45),
                "U14 Duo": timedelta(minutes=1, seconds=10),
                "U16 Duo": timedelta(minutes=1, seconds=30),
                "U18 Duo": timedelta(minutes=1, seconds=30),
                "U21 Duo": timedelta(minutes=1, seconds=30),
                "Adults Duo": timedelta(minutes=1, seconds=30),
                "Master M1 Duo": timedelta(minutes=1, seconds=30),
                "Master M2 Duo": timedelta(minutes=1, seconds=30),
                "Master M3 Duo": timedelta(minutes=1, seconds=30),
                "Master M4 Duo": timedelta(minutes=1, seconds=30),
                "U10 Show": timedelta(minutes=3),
                "U12 Show": timedelta(minutes=3),
                "U14 Show": timedelta(minutes=3),
                "U16 Show": timedelta(minutes=4),
                "U18 Show": timedelta(minutes=4),
                "U21 Show": timedelta(minutes=4),
                "Adults Show": timedelta(minutes=3, seconds=30),
                "Master M1 Show": timedelta(minutes=3, seconds=30),
                "Master M2 Show": timedelta(minutes=3, seconds=30),
                "Master M3 Show": timedelta(minutes=3, seconds=30),
                "Master M4 Show": timedelta(minutes=3, seconds=30),
                "U10 Jiu-Jitsu": timedelta(minutes=3, seconds=30),
                "U12 Jiu-Jitsu": timedelta(minutes=3, seconds=30),
                "U14 Jiu-Jitsu": timedelta(minutes=3, seconds=30),
                "U16 Jiu-Jitsu": timedelta(minutes=4, seconds=30),
                "U18 Jiu-Jitsu": timedelta(minutes=4, seconds=30),
                "U21 Jiu-Jitsu": timedelta(minutes=5, seconds=30),
                "Adults Jiu-Jitsu": timedelta(minutes=5, seconds=30),
                "Master M1 Jiu-Jitsu": timedelta(minutes=5, seconds=30),
                "Master M2 Jiu-Jitsu": timedelta(minutes=5, seconds=30),
                "Master M3 Jiu-Jitsu": timedelta(minutes=5, seconds=30),
                "Master M4 Jiu-Jitsu": timedelta(minutes=5, seconds=30)
                }

    dict_finals_duo = {
        1: 0,
        2: 1,    # one final
        3: 2.5,  # one final, one table with 3
        4: 3,    # one final, two semi finals
        5: 3,    # one final, two semi finals
        6: 4,    # two finals, two semi finals
        7: 5.5,  # two finals, two semi finals, one table with 3
        8: 6,    # two finals, four semi finals,
        9: 6,    # two finals, four semi finals,
        10: 7,   # three finals, four semi finals,
        11: 8.5,  # three finals, four semi finals, one table with 3
        12: 9     # three finals, six semi finals,
    }  # based on the 2024 duo rules.. not the most elegant but it works

    for cat_name in dict_inp:  # loop over dictionary
        par_num = int(dict_inp.get(cat_name))  # number of fights per category
        fight_num = 0  # reset counter

        if "Show" in cat_name and par_num > 1:
            if final is True and par_num > 5:
                for keys in time_inp:
                    # if name of Discipline is in string of category:
                    if keys in cat_name:
                        cat_finals_dict[cat_name] = time_inp[keys]
                        final_time += time_inp[keys] * par_num
            fight_num = par_num
        if "Duo" in cat_name and par_num > 1:
            if final is True and par_num > 2:
                for keys in time_inp:
                    # if name of Discipline is in string of category:
                    if keys in cat_name:
                        cat_finals_dict[cat_name] = time_inp[keys]
                        final_time += time_inp[keys] * 2 *1.5
                        # finals have more attacks
                        fight_num = -1  # remove final of world division

            if ("Adults" or "U21" or "U18") in cat_name:
                # three rounds of preliminaries
                fight_num_pre = par_num * 3
            else:
                # youth categories only have 2 rounds
                fight_num_pre = par_num * 2

            if par_num <= 12:
                num_duo_finals = int(dict_finals_duo[par_num])
            else:
                num_duo_finals = 9

            # each couple shows attacks and finals have more attacks
            fight_num = fight_num_pre + num_duo_finals*2*1.5

        else:
            if final is True and par_num > 5:
                fight_num = -1  # remove final
                for keys in time_inp:
                    # if name of Discipline is in string of category:
                    if keys in cat_name:
                        cat_finals_dict[cat_name] = time_inp[keys]
                        final_time += time_inp[keys]
                if bronze_final is True and par_num > 6:
                    if ms_mode is True:
                        # the "normal" bronze finals stay in preliminary
                        for keys in time_inp:
                            # if name of Discipline is in string of category:
                            if keys in cat_name:
                                cat_bfinals_dict[cat_name] = time_inp[keys]
                                bfinal_time += time_inp[keys]
                                # add one bronze final
                    else:
                        fight_num = - 3  # remove bronze finals too
                        for keys in time_inp:
                            # if name of Discipline is in string of category:
                            if keys in cat_name:
                                cat_bfinals_dict[cat_name] = time_inp[keys]
                                bfinal_time += 2*time_inp[keys]

            if par_num < 8:
                fight_num += low_par_num.get(par_num)
            else:
                fight_num += (par_num - 8) * 2 + 11

        fight_num_total += fight_num
        par_num_total += par_num  # add all participants

        for keys in time_inp:
            # if name of Discipline is in string of category:
            if keys in cat_name:
                cat_time_dict[cat_name] = time_inp[keys] * fight_num
                tot_time += time_inp[keys] * fight_num
                cat_fights_dict[cat_name] = fight_num
        fight_num_total += len(cat_finals_dict)

    return cat_fights_dict, cat_finals_dict, cat_time_dict, \
        par_num_total, fight_num_total, tot_time, final_time, cat_bfinals_dict, bfinal_time


def split_categories(cat_time_dict, av_time):
    '''
    If a category is longer than the average time for the day plus 30 min (1800 sec),
    the category is split in 1/3 and 2/3 and can be planned parallel

    Parameters
    ----------
    cat_time_dict
        dict that links the category to a day [dict (string -> int)]
    av_time
        average time per day [timedelta]
    '''
    for key, value in cat_time_dict.copy().items():
        if value.seconds > (av_time.seconds + 1800):
            cat_p1 = key + " part 1 "
            cat_p2 = key + " part 2 "
            time_1 = value.seconds* 2 / 3
            time_2 = value.seconds* 1 / 3
            del cat_time_dict[key]
            cat_time_dict[cat_p1] = timedelta(seconds=time_1)
            cat_time_dict[cat_p2] = timedelta(seconds=time_2)

    return cat_time_dict


def distr_cat_alg(jobs, av_time, cur_per, cur_pen_time,
                  tatami, break_t, breaktime, breaklength, max_tatamis_per_discipline):
    '''
    Run the algorithm. Create a list of dictionaries, where each discipline
    has its own dictionary, and fill it with the existing categories.
    Sort each dictionary by size (longest competitions at the beginning of the list).

    Parameters
    ----------
    jobs : dict
        dict of categories that need to be distributed.
    av_time : float
        reference time for average tatami [s].
    cur_per : list
        current order of disciplines.
    cur_pen_time : float
        penalty time for changing a discipline [s].
    tatami : int
        number of tatamis.
    break_t : str
        "block" or "Individual".
    breaktime : datetime
        time when the break should happen.
    breaklength : datetime
        length of the break.
    max_tatamis_per_discipline : dict
        maximum number of tatamis allowed for each discipline.

    Returns
    -------
    scheduled_jobs : list
        the final schedule per tatami.
    loads : list
        the time loads on each tatami.
    jobs_new : dict
        the updated job list after potential splitting due to breaks.
    '''

    # dict to have the parts entries
    jobs_new = jobs.copy()
    # List of dictionaries with, where each discipline has its own dictionary
    distr_list = []
    # List of list which stores the times per tatami as a list
    loads = []
    # List of list which stores the names per tatami as a list
    scheduled_jobs = []
    # list for calculating the total needed times per discipline
    time_needed = []
    distr_sor_list = distr_list

    # Step 1
    for i in cur_per:
        distr_list.append({})  # add a new list for each discipline
    for key, value in jobs.items():
        for i, j in enumerate(cur_per):  # loop over all entries in the input
            if j in key:  # Check if key is the same add pair to new dictionary
                distr_list[i][key] = value

    # Step 2
    # sort individual list by length of categories
    for i, j in enumerate(distr_list):
        distr_sor_list[i] = {k: v for k, v in sorted(distr_list[i].items(),
                                                     key=lambda item: item[1],
                                                     reverse=True)}
    par_tat_need = []
    par_tat_need.clear()
    for i, j in enumerate(distr_sor_list):
        time_needed.append(0)  # add 0 as starting time for discipline
        for key, value in distr_list[i].items():
            time_needed[i] += value.seconds
        par_tat_need.append(time_needed[i] / av_time.seconds
                            - time_needed[i] // av_time.seconds)

    remove_tat = 0
    # Step 3

    for i, j in enumerate(distr_sor_list):
        # Get the maximum number of tatamis for the current discipline
        max_tatamis = max_tatamis_per_discipline.get(cur_per[i], tatami)
        if time_needed[i] != 0:  # ignore empty disciplines
            # add  time block for penalties
            extra_time_t = (1 - par_tat_need[i]) * av_time.seconds
            # remove for half tatamis
            remove = False
            # remove for max tatamis
            remove_maxT = False

            # Step a) creates all of "full" tatamis
            for _ in range(0, time_needed[i] // av_time.seconds):
                # create  all tatamis or the max number
                if len(loads) < tatami:
                    loads.append(0)  # create loads for tatamis
                    scheduled_jobs.append([])  # create tatamis

            # Step b) checks if half empty tatami is needed.
            # (with no tatami exists or we need more time than is left)
            if len(loads) >= tatami:  # max number of tatamis is reached
                pass
            elif len(loads) == 0:  # if no tatamis would be created in step a)
                loads.append(0)  # create loads for tatamis
                scheduled_jobs.append([])  # create tatamis
            elif i == 0:  # extra tatami is needed for first rounds
                scheduled_jobs.append([])  # add empty tatami
                loads.append(extra_time_t + cur_pen_time)
                remove = True
                remove_tat = len(scheduled_jobs) - 1
            elif loads[remove_tat] > (extra_time_t - cur_pen_time):
                # extra tatami is needed
                scheduled_jobs.append([])  # add empty tatami
                loads.append(extra_time_t + cur_pen_time)
                remove = True
                remove_tat = len(scheduled_jobs) - 1
            else:
                pass

            # Step c) create blocks to reduce number of available tatamis
            if len(loads) > max_tatamis:
                # find out how many tatamis need to be removed
                N = len(loads) - max_tatamis
                sres = sorted(range(len(loads)), key = lambda sub: loads[sub])[-N:]
                for q in sres:
                    loads[q] += timedelta(hours=12).seconds
                remove_maxT = True

            # Step d) distribute categories
            for job in distr_sor_list[i]:
                if distr_sor_list[i][job].seconds > 0:
                    minload_tatami = minloadtatami(loads)
                    if break_t == "Individual":
                        if loads[minload_tatami] > breaktime.seconds and BREAK not in scheduled_jobs[minload_tatami] and len(scheduled_jobs[minload_tatami]) > 0 and scheduled_jobs[minload_tatami][-1] is not DIS_CHA:
                            if remove is True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t) < breaktime.seconds):
                                pass  # ignore extra time
                            else:
                                scheduled_jobs[minload_tatami].append(BREAK)
                                loads[minload_tatami] += breaklength.seconds
                        scheduled_jobs[minload_tatami].append(job)
                        loads[minload_tatami] += distr_sor_list[i][job].seconds
                    elif break_t == "One Block":
                        if (loads[minload_tatami] + distr_sor_list[i][job].seconds) > breaktime.seconds and BREAK not in scheduled_jobs[minload_tatami]:
                            if remove is True and minload_tatami is remove_tat and ((loads[minload_tatami] - extra_time_t) < breaktime.seconds):
                                pass  # ignore extra time
                            else:
                                job1 = job + " part 1 "
                                job2 = job + " part 2 "
                                time2 = loads[minload_tatami] + distr_sor_list[i][job].seconds - breaktime.seconds
                                time1 = distr_sor_list[i][job].seconds - time2

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

            # remove added time blocks
            if remove is True:
                # removed the time from the tatami.
                loads[remove_tat] -= (extra_time_t)
                remove = False
            if remove_maxT is True:
                for p in sres:
                    loads[p] -= timedelta(hours=12).seconds
                remove_maxT = False

            # add discipline change after each distribution
            for tat_used in range(0, len(loads)):
                if len(scheduled_jobs[tat_used]) > 0 and scheduled_jobs[tat_used][-1] is not DIS_CHA and scheduled_jobs[tat_used][-1] is not BREAK:
                    scheduled_jobs[tat_used].append(DIS_CHA)
                    loads[tat_used] += cur_pen_time * 60

    for tat_used in range(0, len(loads)):
        if len(scheduled_jobs[tat_used]) > 0 and scheduled_jobs[tat_used][-1] is DIS_CHA:
            scheduled_jobs[tat_used].pop()
            loads[tat_used] -= cur_pen_time * 60

    return scheduled_jobs, loads, jobs_new


def minloadtatami(loads):
    """Find the tatami with the minimum load.
    Break the tie of tatamis having same load on
    first come first serve basis.

    Parameters
    ----------
    loads
        list of loads [float]

    """
    minload = min(loads)
    for tat_min, load in enumerate(loads):
        if load == minload:
            return tat_min
        else:
            pass
