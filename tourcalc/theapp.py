""" This module created the GUI

It can be run with

streamlit run theapp.py


more details see installation

"""
import os
from datetime import time, datetime, date, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import streamlit as st
import itertools # for permutations of discipline order
from calculator import write_tour_file
from calculator import descition_matrix
from calculator import cal_cat
from calculator import read_in_file
from calculator import calculate_fight_time

AGE_INP = ["U16", "U18", "U21", "Adults"] #the supported age categories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"] # order does not matter -> permutations

AGE_SEL = [] #an empty list to select the age categories
DIS_SEL = [] #an empty list to select the age categories

DIS_CHA = "Discipline change" # indicator of a change of a discipline
DIS_CHA_TIME = 30 #add the changing time for the change between disciplines in minutes

BREAK = "Break"
#BREAK_TIME = 14400 # 4hrs after start of tournament
BREAK_LENGTH = 30 # 30 min

def plot_schedule(scheduled_jobs, cat_time_dict, start_time, loads, endtime):
    '''plots a schedule'''

    df = pd.concat([pd.DataFrame([l, [i+1]*len(l)]).T for i, l in enumerate(scheduled_jobs)])
    df.columns = ['category', 'tatami']
    df['time'] = df['category'].replace(cat_time_dict)
    df['time'] = df['time'] + pd.to_datetime('1970/01/01')

    df['cat_type'] = df['category']

    df['cat_type'].where(~(df['cat_type'].str.contains("Jiu-Jitsu")), \
        other="Jiu-Jitsu", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Fighting")), other="Fighting", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Duo")), other="Duo", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Show")), other="Show", inplace=True)

    df['gender'] = df['category']
    df['gender'].where(~(df['gender'].str.contains("Men")), other="Men", inplace=True)
    df['gender'].where(~(df['gender'].str.contains("Women")), other="Women", inplace=True)
    df['gender'].where(~(df['gender'].str.contains("Mixed")), other="Mixed", inplace=True)

    order_d = {str(i+1): j for i, j in enumerate(scheduled_jobs)}
    fig = px.bar(df, x='tatami', y='time', color='cat_type', hover_name = 'category',\
        text ='category', pattern_shape= 'gender',  category_orders= order_d)
    #fig = px.bar(df, x='tatami', y='time', \
    #category_orders= {str(i+1): j for i, j in enumerate(scheduled_jobs)})

    #st.write(order_d)
    #st.write(df)

    #fig._layout(yaxis={'categoryorder':'array', 'categoryarray':df.index})
    #fig.update_layout(yaxis=dict(type='tatami'))

    return fig

def plot_schedule_go(scheduled_jobs, cat_time_dict, start_time, loads, endtime):
    '''plots a schedule'''

    fig = go.Figure()

  #str.contains("Fighting"))

   # color_map = {
   #     f: 'red'
    x = ["Tatami"]*len(scheduled_jobs)
    t = 0
    for tatami in scheduled_jobs:
        y = []
        for cat in tatami:
            y.append(cat_time_dict[cat].seconds)
        fig.add_trace(go.Bar(x=x, y=y, text=tatami,
            textposition='auto',hovertext =cat + '\n Time: ' + str(cat_time_dict[cat])))
        #fig.add_annotation(x=x, y= 150000,
        #    text=str(loads[t]),
        #    showarrow=False,
        #    yshift=10)
        t +=1

    fig.update_layout(legend_title_text = "Category")

    fig.update_xaxes(title_text="Tatami")
    fig.update_yaxes(title_text="Time")
    #fig.update_yaxes(tickformat= "%H:%M")
        #fig.update_yaxes(range=(start_time, endtime))

    return fig

def heatmap(data, row_labels, col_labels, str_title):
    """
    Create a heatmap from a numpy array and two lists of labels. - HELPER FUNCTION DRAW

    Parameters
    ----------
    data
        A 2D pandas data frame array of shape (N = row_labels, M = col_labels). [df]
    row_labels
        A list or array of length N with the labels for the rows. [list]
    col_labels
        A list or array of length M with the labels for the columns. [list]
    str_title
        A string that contains the tittle    [string]
    """

    #create the hover text
    perm_map = {
        i: permutations_list[i] for i in range(
            0, len(permutations_list)
        )
    }
    _x = len(col_labels)
    _y = len(row_labels)
    _hover = []
    for i in range(0, _y):
        _hover.append(
            [str(perm_map[int(data[i][j])]) for j in range(0, _x)]
            )


    fig1 = ff.create_annotated_heatmap(
        data,
        x=col_labels,
        y=row_labels,
        colorscale='Viridis',
        text=_hover,
        hoverinfo='text'
    )
    fig1.update_layout(legend_title_text = str_title)
    fig1.update_layout(title= str_title)
    fig1.update_xaxes(title_text="Happiness value [a.u]")
    fig1.update_yaxes(title_text="Discipline Change [min]")

    return fig1

cat_par = {}#number of participants
cat_dict_day = {}#day per category

tatami = 1
days = 1
final = 'NO'

tour_name = st.text_input("Name of the tournament", key = 1)
fname = tour_name + ".txt"

permutations_object = itertools.permutations(DIS_INP)
permutations_list = list(permutations_object)


if len(tour_name) > 0 and os.path.isfile(fname) and tour_name != "random":
    st.write("Tournament with name ", tour_name, "already exist")
    newf = st.selectbox('What do you want to do?', ['USE', 'OVERRIDE'])
    if newf == 'USE':
        cat_par_inp, cat_dict_day, final, tatami, days, \
            start_time, breaktype  = read_in_file(tour_name+".txt")
        cat_par = cat_par_inp

        for cat_name in cat_par_inp: #loop over dictionary
            if ("U16" in cat_name) and ("U16" not in AGE_SEL):
                AGE_SEL.append("U16")
            if ("U18" in cat_name) and ("U18" not in AGE_SEL):
                AGE_SEL.append("U18")
            if ("U21" in cat_name) and ("U21" not in AGE_SEL):
                AGE_SEL.append("U21")
            if ("Adults" in cat_name) and ("Adults" not in AGE_SEL):
                AGE_SEL.append("Adults")
            if len(AGE_SEL) == 0:
                st.write("No age categories in input file")

            if ("Show" in cat_name) and ("Show" not in DIS_SEL):
                DIS_SEL.append("Show")
            if ("Duo" in cat_name) and ("Duo" not in DIS_SEL):
                DIS_SEL.append("Duo")
            if ("Fighting" in cat_name) and ("Fighting" not in DIS_SEL):
                DIS_SEL.append("Fighting")
            if ("Jiu-Jitsu" in cat_name) and ("Jiu-Jitsu" not in DIS_SEL):
                DIS_SEL.append("Jiu-Jitsu")
            if len(DIS_SEL) == 0:
                st.write("No disciplines in input file")

left_column, right_column = st.columns(2)

with left_column:

    tatami = st.number_input("Number of tatamis",  value = tatami)
    days = st.number_input("Number of days",  value = days)

with right_column:
    final = st.selectbox('Does the event have a final block',
    ('YES', 'NO'))
    breaktype = st.selectbox('What type of break do you want',
    ('Individual','One Block' ,'No break'))

if final == 'YES':
    final = True
else: final = False

with st.expander("Advanced settings"):
    st.write("with this settings you can fine tune your event ")
    breaklength_wid = st.time_input('Length of the break', time(0, 30))
    breaktime_wid = st.time_input('Start time of the break', time(13, 00))
    start_time_wid = st.time_input('Start time of the event', time(9, 00))

start_time = datetime.combine(date.min, start_time_wid) - datetime.min
breaktime = datetime.combine(date.min, breaktime_wid) - datetime.min - start_time
breaklength = datetime.combine(date.min, breaklength_wid) - datetime.min

tatami_day = [int(tatami)] * days
start_time_day =[start_time] * days
bt_day = [breaktime] * days
breaklength_day = [breaklength] * days

j = 0
while j < days:
    with st.expander("Change settings for day" + str(j+1)):
        st.write("with this settings you can fine tune your event ")
        breakl_wid_day = st.time_input('Length of the break', time(0, 30), key = j)
        bt_wid_day = st.time_input('Start time of the break', time(13, 00), key = j)
        start_time_wid_day = st.time_input('Start time of the event', time(9, 00), key = j)
        tatami_day[j] = int(st.number_input("Number of tatamis", value = tatami, key = j))

        start_time_day[j] = (datetime.combine(date.min, start_time_wid_day) - datetime.min)
        bt_day[j] = (datetime.combine(date.min, bt_wid_day) - datetime.min - start_time_day[j])
        breaklength_day[j] = (datetime.combine(date.min, breakl_wid_day) - datetime.min)
    j += 1

age_select = st.multiselect('Select the participating age categories', AGE_INP, AGE_SEL)
dis_select = st.multiselect('Select the participating disciplines', DIS_INP, DIS_SEL)

cat_all = cal_cat(age_select, dis_select) # calculate categories

tot_par = 0
with st.expander("Hide categories"):
    left_column1, right_column2 = st.columns(2)
    for i in cat_all:
        if tour_name == "random":
            _rtmp = round(np.random.normal(8, 5.32))
            while _rtmp < 0:
                _rtmp = round(np.random.normal(8, 5.32))
            with left_column1:
                inp = st.number_input("Number of athletes " + i,  \
                    min_value= 0, value = _rtmp, key = i )
            day_rtmp = np.random.randint(1,days+1)
            with right_column2:
                day = st.number_input("Competition day " + i,  \
                    min_value= 0, value = day_rtmp, key = i)
        else:
            val = cat_par.get(i)
            val1 = cat_dict_day.get(i)
            with left_column1:
                if val is None:
                    val =  0
                inp = st.number_input("Number of athletes " + i, min_value=0, key = i, value = val)
            with right_column2:
                if val1 is None:
                    val1 =  1
                day = st.number_input("Competition day " + i, min_value= 0, key = i,value = val1)

        tot_par +=  int(inp)
        cat_par[i] = int(inp)
        cat_dict_day[i] = int(day)

if st.button('all info is correct'):
    write_tour_file(tour_name,cat_par,cat_dict_day,tatami, days,final,start_time,breaktype)
    if tot_par == 0:
        st.write("Please add at least one athlete")
    elif tatami > len(cat_all):
        st.write("You have more tatamis than disciplines, please add disciplines or reduce tatamis")
    else:
        j = 0
        st.write("Tournament: ", tour_name)
        cat_fights_dict, cat_finals_dict, cat_time_dict, \
            av_time, par_num_total, fight_num_total, \
            tot_time, final_time = calculate_fight_time(cat_par, final, tatami)
        st.write("There are",tot_par, "participants, which will fight", \
            fight_num_total, " matches in ", \
        len(cat_all), "categories with a total time fight time of (HH:MM:SS)", tot_time+final_time)
        st.markdown("---")

        while j < days:
            cat_par_day = {}
            for i in cat_par:
                if cat_dict_day[i] == j+1:
                    cat_par_day[i] = int(cat_par.get(i))

            cat_fights_dict, cat_finals_dict, cat_time_dict, \
                av_time, par_num_total, fight_num_total, \
                tot_time, final_time = calculate_fight_time(cat_par_day, final, int(tatami_day[j]))

            st.write("Day: " , str(j+3)  , " Nov.  There are",par_num_total, \
                "participants, which will fight", fight_num_total, " matches in ", \
            len(cat_time_dict), "categories with a total time fight time of (HH:MM:SS)",\
                tot_time+final_time)
            st.write("You have", len(cat_finals_dict), "finals which will take", final_time)
            st.write("Optimal solution time per tatami will be", av_time, \
                "with", tatami_day[j], "tatamis")
            st.write("Start time day:",start_time_day[j] ,"Final can start at: ",\
                av_time+start_time_day[j])

            #add an entry for penalty time in dict!
            cat_time_dict[DIS_CHA] = timedelta(minutes=DIS_CHA_TIME)
            #add an entry for the break time in dict!
            cat_time_dict[BREAK] = breaklength

            scheduled_jobs, loads, most_abundand, min_id, pen_time_list, happiness, \
            min_score, cat_time_dict_new= descition_matrix(cat_time_dict, av_time, \
                 int(tatami_day[j]), breaktype, bt_day[j], breaklength_day[j])

            #st.write(cat_time_dict_new)
            best_res = {k: v for k, v in sorted(most_abundand.items(), \
                key=lambda item: item[1], reverse=True)}

            pen_time = DIS_CHA_TIME//2 #chosen penalty time
            permut_num = int(list(best_res)[0]) #chosen permutation
            # add for displaying the end_time in plot
            endtime = max(loads[pen_time][permut_num]) + 1800

            #add start_time to loads
            #loads[pen_time][permut_num] = [x+start_time.seconds for x in loads[pen_time][permut_num]]
            #loads[pen_time][permut_num] = [str(timedelta(seconds=x)) for x in loads[pen_time][permut_num]]
            #st.write(scheduled_jobs[pen_time][permut_num])
            st.write("Permutation ",permut_num, " ", permutations_list[permut_num], \
                "gives best result ", best_res[permut_num], "times")
            st.write(plot_schedule_go(scheduled_jobs[pen_time][permut_num],
                cat_time_dict_new, start_time.seconds,
                loads[pen_time][permut_num],
                endtime/3600+start_time.seconds/3600))

            label = "There are " + str(len(most_abundand)) + " possible results for day "\
                + str(j+1)+". Open Details"

            with st.expander(label):
                k = 1
                st.write("other options")
                while k < len(best_res):
                    permut_num = int(list(best_res)[k]) #chosen permutation
                    st.write("Permutation number",permut_num, " ", permutations_list[permut_num],\
                        "gives best result ", best_res[permut_num], "times")
                    # add for displaying the end_time in plot
                    endtime = max(loads[pen_time][permut_num]) + 1800
                    st.write(plot_schedule_go(scheduled_jobs[pen_time][permut_num],
                        cat_time_dict_new, start_time.seconds,
                        loads[pen_time][permut_num],
                        endtime/3600+start_time.seconds/3600))
                    k += 1

                st.write("Matrix with the results")
                fig1 = heatmap(min_id, pen_time_list, happiness, "Which permutation gives the best result")
                st.write(fig1)

            cat_par_day.clear()
            st.markdown("---")
            j += 1
            