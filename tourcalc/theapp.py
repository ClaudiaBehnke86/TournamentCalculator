""" This module created the GUI

It can be run with

streamlit run theapp.py

more details see installation

"""
import os
from datetime import time, datetime, timedelta
import itertools  # for permutations of discipline order
from pathlib import Path
import math
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st
import numpy as np
# [Bug] to create the sub module doc 
# correctly one needs to add tourcalc.calculator to the import statement.
# Otherwise the docs html is not created
from calculator import write_tour_file
from calculator import descition_matrix
from calculator import cal_cat
from calculator import read_in_file
from calculator import calculate_fight_time

AGE_INP = ["U16", "U18", "U21", "Adults"]  # the supported age categories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"]  # supported disciplines

AGE_SEL = []  # an empty list to select the age categories
DIS_SEL = []  # an empty list to select the age categories

DIS_CHA = "Discipline change"  # indicator of a change of a discipline
DIS_CHA_TIME = 30  # add the changing time between disciplines in minutes

BREAK = "Break"


def plot_schedule_time(scheduled_jobs_i, cat_time_dict_i, start_time_i, date_i, final_time):
    """
    plots a schedule horizontal

    Parameters
    ----------
    scheduled_jobs
        a list of lists of all categories per tatami [[str]]
    cat_time_dict
        a dict that maps the strings in "scheduled_jobs" to times [dict]
    start_time
        the start time of the day [datetime]
    date
        The date of the current day [datetime]

    """

    l_master = [pd.DataFrame([l, [i+1]*len(l)]).T for i, l in enumerate(scheduled_jobs_i)]

    for df_tatami in l_master:
        df_tatami.columns = ['category', 'tatami']
        df_tatami['time'] = df_tatami['category'].replace(cat_time_dict_i)
        df_tatami['end_time'] = np.cumsum(df_tatami['time']).values.astype('datetime64[ns]')
        df_tatami['end_time'] += timedelta(seconds=start_time_i)
        df_tatami['start_time'] = df_tatami['end_time'].shift(
            periods=1
            ).astype('datetime64[ns]')

        df_tatami['time'] = df_tatami['time'].values.astype('datetime64[ns]')

    df = pd.concat(l_master)

    str_start = str(date) + " " + str(timedelta(seconds=start_time_i))
    df.fillna(str_start, inplace=True)
    df['cat_type'] = df['category']

    df['cat_type'].where(~(df['cat_type'].str.contains("Jiu-Jitsu")),
                         other="Jiu-Jitsu", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Fighting")),
                         other="Fighting", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Duo")),
                         other="Duo", inplace=True)
    df['cat_type'].where(~(df['cat_type'].str.contains("Show")),
                         other="Show", inplace=True)

    df['end_time'] = str(date_i) + ' ' + \
        df['end_time'].apply(lambda x: str(x)[-8:])
    df['start_time'] = str(date_i) + ' ' + \
        df['start_time'].apply(lambda x: str(x)[-8:])

    # see bug https://github.com/plotly/plotly.py/issues/3065
    end_time_prelim = datetime.strptime(df['end_time'].max(), "%Y-%m-%d %H:%M:%S").timestamp() * 1000

    end_time_final_c = datetime.strptime(df['end_time'].max(), "%Y-%m-%d %H:%M:%S") + final_time

    if final_time.seconds > 0:
        df2 = df.append(
            dict(category="Final Block",
                 tatami=math.ceil(TATAMI/2),
                 end_time=end_time_final_c,
                 start_time=df['end_time'].max(),
                 cat_type='Final Block'),
            ignore_index=True)
    else:
        df2 = df

    fig = px.timeline(
        df2,
        x_start='start_time',
        x_end='end_time',
        y='tatami',
        color='cat_type',
        color_discrete_map={
                "Jiu-Jitsu": 'rgb(243, 28, 43)',
                "Fighting": 'rgb(0,144,206)',
                "Duo": 'rgb(211,211,211)',
                "Show": 'rgb(105,105,105)',
                "Discipline change": 'rgb(255,255,255)',
                "Break": 'rgb(255,255,255)'},
        hover_name='category',
        text='category'
    )

    fig.add_vline(x=end_time_prelim,
                  line_width=3,
                  line_dash="dash",
                  line_color="white",
                  annotation_text=str(df['end_time'].max())[-8:],
                  annotation_position="top right")

    return fig, end_time_final_c, df['end_time'].max()


def heatmap(data, row_labels, col_labels, str_title):
    """
    Create a heat map from a numpy array and two lists of labels.
    - HELPER FUNCTION DRAW

    Parameters
    ----------
    data
        A 2D pandas data frame array of shape
        (N = row_labels, M = col_labels). [df]
    row_labels
        A list or array of length N with the labels for the rows. [list]
    col_labels
        A list or array of length M with the labels for the columns. [list]
    str_title
        A string that contains the tittle    [string]
    """

    # create the hover text
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
        colorscale='Bluered',
        text=_hover,
        hoverinfo='text'
    )
    fig1.update_layout(legend_title_text=str_title)
    fig1.update_layout(title=str_title)
    fig1.update_xaxes(title_text="Happiness value [a.u]")
    fig1.update_yaxes(title_text="Discipline Change [min]")

    return fig1


cat_par = {}  # number of participants
cat_dict_day = {}  # day per category

tour_name = st.text_input("Name of the tournament", key='unique')
fname = tour_name + ".txt"
check_file = Path('tourcalc/example_tours') / fname

if st.button("Show example tournaments"):
    st.write('You can read in the event by copying the name \
        without .txt into the "Name of the tournament" field')
    filenames = os.listdir('tourcalc/example_tours')
    st.write(filenames)

permutations_object = itertools.permutations(DIS_INP)
permutations_list = list(permutations_object)

link = '[Click here for tutorial](https://tournamentcalculator.readthedocs.io/en/latest/tutorial.html)'
st.markdown(link, unsafe_allow_html=True)


if len(tour_name) > 0 and os.path.isfile(check_file) and tour_name != "random":
    st.write("Tournament with name ", tour_name, "already exist")
    newf = st.selectbox('What do you want to do?', ['USE', 'OVERRIDE'])
    if newf == 'USE':
        cat_par_inp, cat_dict_day, FINAL, TATAMI, days, \
            start_time, breaktype = read_in_file(tour_name+".txt")
        cat_par = cat_par_inp

        for cat_name in cat_par_inp:  # loop over dictionary
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
else:
    TATAMI = 1
    days = 1
    FINAL = 'NO'

left_column, right_column = st.columns(2)

with left_column:

    TATAMI = st.number_input("Number of tatamis",  value=TATAMI, key='tatami')
    days = st.number_input("Number of days",  value=days, key='days')

with right_column:
    FINAL = st.selectbox('Does the event have a final block',
                         ('YES', 'NO'), key='final')
    breaktype = st.selectbox('What type of break do you want',
                             ('Individual', 'One Block', 'No break'), key='breakt')

FINAL = bool(FINAL == 'YES')    

date = st.date_input('First day of the event', value=datetime.today(), key='date')
tatami_day = [int(TATAMI)] * int(days)
start_time_day = [time(9, 00)] * int(days)
bt_day = [time(13, 00)] * int(days)
breaklength_day = [time(0, 30)] * int(days)
end_time_final = [time(00, 00)] * int(days)
end_time_prelim = [time(00, 00)] * int(days)


age_select = st.multiselect('Select the participating age categories',
                            AGE_INP,
                            AGE_SEL)
dis_select = st.multiselect('Select the participating disciplines',
                            DIS_INP,
                            DIS_SEL)

cat_all = cal_cat(age_select, dis_select)  # calculate categories

tot_par = 0
with st.expander("Hide categories"):
    left_column1, right_column2 = st.columns(2)
    for i in cat_all:
        if tour_name == "random":
            _rtmp = round(np.random.normal(8, 5.32))
            while _rtmp < 0:
                _rtmp = round(np.random.normal(8, 5.32))
            with left_column1:
                inp = st.number_input("Number of athletes " + i,
                                      min_value=0, value=_rtmp, key=i)
            day_rtmp = np.random.randint(1, days+1)
            with right_column2:
                day = st.number_input("Competition day " + i,
                                      min_value=0, value=day_rtmp, key=i)
        else:
            val = cat_par.get(i)
            val1 = cat_dict_day.get(i)
            with left_column1:
                if val is None:
                    val = 0
                inp = st.number_input("Number of athletes " + i,
                                      min_value=0,
                                      key=i,
                                      value=val)
            with right_column2:
                if val1 is None:
                    val1 = 1
                day = st.number_input("Competition day " + i,
                                      min_value=0, key=i, value=val1)

        tot_par += int(inp)
        cat_par[i] = int(inp)
        cat_dict_day[i] = int(day)

j = 0
while j < int(days):
    with st.expander("Change settings for day "
                     + str(j+1) + " : " + str(date+timedelta(days=j))):
        st.write("with this settings you can fine tune your event ")
        breakl_wid_day = st.time_input('Length of the break',
                                       time(0, 30), key=j)
        bt_wid_day = st.time_input('Start time of the break',
                                   time(13, 00), key=j)
        start_time_wid_day = st.time_input('Start time of the event',
                                           time(9, 00), key=j)
        tatami_day[j] = int(st.number_input("Number of tatamis",
                                            value=TATAMI, key=j))

        start_time_day[j] = (datetime.combine(date.min,
                             start_time_wid_day) - datetime.min)
        bt_day[j] = (datetime.combine(date.min, bt_wid_day)
                     - datetime.min - start_time_day[j])
        breaklength_day[j] = (datetime.combine(date.min,
                                               breakl_wid_day) - datetime.min)
    j += 1

if st.button('all info is correct'):
    write_tour_file(tour_name,
                    cat_par,
                    cat_dict_day,
                    TATAMI,
                    days,
                    FINAL,
                    start_time_day[0],
                    breaktype)
    if tot_par == 0:
        st.write("Please add at least one athlete")
    elif TATAMI > len(cat_all):
        st.write("You have more tatamis than disciplines, \
                 please add disciplines or reduce tatamis")
    else:
        j = 0
        st.write("Tournament: ", tour_name)
        cat_fights_dict, cat_finals_dict, cat_time_dict, \
            av_time, par_num_total, fight_num_total, \
            tot_time, final_time = calculate_fight_time(cat_par, FINAL, TATAMI)
        st.write("There are", tot_par, "participants, which will fight",
                 fight_num_total, " matches in ", len(cat_all),
                 "categories with a total time fight time of (HH:MM:SS)",
                 tot_time+final_time)
        st.markdown("---")

        while j < days:
            cat_par_day = {}
            for i in cat_par:
                if cat_dict_day[i] == j+1:
                    cat_par_day[i] = int(cat_par.get(i))

            cat_fights_dict, cat_finals_dict, cat_time_dict, \
                av_time, par_num_total, fight_num_total, \
                tot_time, \
                final_time = calculate_fight_time(cat_par_day,
                                                  FINAL,
                                                  int(tatami_day[j]))

            stringheader = "Day: " + str(date+timedelta(days=j))
            st.header(stringheader)
            st.write("There are", par_num_total,
                     "participants, which will fight", fight_num_total,
                     " matches in ", len(cat_time_dict),
                     "categories with a total time fight time of (HH:MM:SS)",
                     tot_time+final_time, "  \n You have",
                     len(cat_finals_dict),
                     "finals which will take", final_time,
                     "   \n Optimal solution time per tatami will be",
                     av_time, "with", tatami_day[j],
                     "tatamis.")

            # add an entry for penalty time in dict!
            cat_time_dict[DIS_CHA] = timedelta(minutes=DIS_CHA_TIME)
            # add an entry for the break time in dict!
            cat_time_dict[BREAK] = breaklength_day[j]

            scheduled_jobs, most_abundand, min_id, \
                pen_time_list, happiness, \
                min_score, \
                cat_time_dict_new = descition_matrix(cat_time_dict,
                                                     av_time,
                                                     int(tatami_day[j]),
                                                     breaktype,
                                                     bt_day[j],
                                                     breaklength_day[j])

            best_res = {k: v for k, v in sorted(most_abundand.items(),
                        key=lambda item: item[1], reverse=True)}

            pen_time = DIS_CHA_TIME//2  # chosen penalty time
            permut_num = int(list(best_res)[0])  # chosen permutation

            st.write("Permutation ", permut_num, " ",
                     permutations_list[permut_num],
                     "gives best result ",
                     best_res[permut_num], "times")

            fig, end_time_final[j], end_time_prelim[j] = plot_schedule_time(
                     scheduled_jobs[pen_time][permut_num],
                     cat_time_dict_new[pen_time][permut_num],
                     start_time_day[j].seconds,
                     date+timedelta(days=j), final_time)

            st.plotly_chart(fig)
            st.write("Start time day:",
                     str(start_time_day[j]),
                     "  \n Finals can start at: ",
                     end_time_prelim[j],
                     "  \n Day ends at: ",
                     str(end_time_final[j]))

            LABEL = "There are " + str(len(most_abundand)) + \
                    " possible results for day "\
                    + str(j+1)+". Open Details"

            with st.expander(LABEL):
                k = 1
                st.write("other options")
                while k < len(best_res):
                    permut_num = int(list(best_res)[k])  # chosen permutation
                    st.write("Permutation number",
                             permut_num, " ",
                             permutations_list[permut_num],
                             "gives best result ",
                             best_res[permut_num],
                             "times")

                    fig, end_time_final[j], end_time_prelim[j] = plot_schedule_time(
                             scheduled_jobs[pen_time][permut_num],
                             cat_time_dict_new[pen_time][permut_num],
                             start_time_day[j].seconds,
                             date+timedelta(days=j), final_time)

                    st.plotly_chart(fig)
                    st.write("Start time day:",
                             str(start_time_day[j]),
                             "  \n Final can start at: ",
                             end_time_prelim[j],
                             "  \n Day ends at: ",
                             str(end_time_final[j]))
                    k += 1

                st.write("Matrix with the results")
                fig1 = heatmap(min_id,
                               pen_time_list,
                               happiness,
                               "Best permutation")
                st.write(fig1)

            cat_par_day.clear()
            st.markdown("---")
            j += 1
