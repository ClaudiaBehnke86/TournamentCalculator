""" This module created the GUI

It can be run with

streamlit run theapp.py

more details see installation

"""
import os
from datetime import time, datetime, timedelta
import itertools  # for permutations of discipline order
from pathlib import Path
from pandas import json_normalize
import math
import random
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st
from fpdf import FPDF

import numpy as np

import tourcalc
from tourcalc.calculator import write_tour_file
from tourcalc.calculator import descition_matrix
from tourcalc.calculator import cal_cat
from tourcalc.calculator import read_in_file
from tourcalc.calculator import calculate_fight_time
from tourcalc.calculator import split_categories
from tourcalc.APIcall import getdata

import requests
from requests.auth import HTTPBasicAuth

AGE_INP = ["U12", "U14", "U16", "U18", "U21", "Adults", "Master"]  # the supported age divisions
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"]

AGE_SEL = []  # an empty list to select the age divisions
DIS_SEL = []  # an empty list to select the age categories

DIS_CHA = "Discipline change"  # indicator of a change of a discipline
DIS_CHA_TIME = 30  # add the changing time between disciplines in minutes

BREAK = "Break"


class PDF(FPDF):
    '''
    overwrites the pdf settings
    '''

    def __init__(self, orientation, tourname):
        # initialize attributes of parent class
        super().__init__(orientation)
        # initialize class attributes
        self.tourname = tourname

    def header(self):
        # Logo
        self.image('Logo_real.png', 8, 8, 30)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(70)
        # Title
        self.cell(30, 10, 'Daily Schedule for ' + self.tourname, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number & printing date
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cell(0, 10, 'Printed ' + str(now) + ' Page ' +
                  str(self.page_no()) + '/{nb}', 0, 0, 'C')


def plot_schedule_time(scheduled_jobs_i, cat_time_dict_i, start_time_i, date_i, final_time, final_start_time, bfinal_type, bfinal_time, final_tat, bfinal_tat):
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

    l_master = [pd.DataFrame([l, [i + 1] * len(l)]).T for i, l in enumerate(scheduled_jobs_i)]

    for df_tatami in l_master:
        df_tatami.columns = ['category', 'tatami']
        df_tatami['time'] = df_tatami['category'].replace(cat_time_dict_i)
        df_tatami['end_time'] = np.cumsum(df_tatami['time']).values.astype('datetime64[ns]')
        df_tatami['end_time'] += start_time_i
        df_tatami['start_time'] = df_tatami['end_time'].shift(periods=1).astype('datetime64[ns]')
        df_tatami['time'] = df_tatami['time'].values.astype('datetime64[ns]')

    df = pd.concat(l_master)

    str_start = str(date) + " " + str(start_time_i)
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
    end_time_prelim = datetime.strptime(df['end_time'].max(), "%Y-%m-%d %H:%M:%S")

    # datetime_local = datetime.now()
    # st.write("local time :", datetime_local)

    # tz_UTC = pytz.timezone('UTC')
    # datetime_utc = datetime.now(tz_UTC)
    # st.write("UTC time :", datetime_utc)

    # quick and dirty fix to make the app online working
    end_time_prelim = end_time_prelim - timedelta(hours=0)
    end_time_prelim = end_time_prelim.timestamp() * 1000

    end_time_prelim_time = df['end_time'].max()

    if final_start_time is not None and \
       datetime.strptime(df['end_time'].max(), "%Y-%m-%d %H:%M:%S").time() > final_start_time:
        st.error("You will be late! The Preliminaries will run to long.")
        st.warning("To fix this: Add a tatami or change the final time!\n \
                 The finals will NOT start at the planned fixed time")
        final_start_time = None

    if final_start_time is None:
        final_start_time = df['end_time'].max()
    else:
        final_start_time = str(date_i) + " "+str(final_start_time)

    if bfinal_type == 'Before the final':
        bfinal_start_time = final_start_time
        final_start_time = datetime.strptime(final_start_time, "%Y-%m-%d %H:%M:%S")  + bfinal_time
        final_start_time = str(final_start_time)
    else: 
        bfinal_start_time = final_start_time

    bfinal_end_time_c = datetime.strptime(bfinal_start_time, "%Y-%m-%d %H:%M:%S") + bfinal_time

    end_time_final_c = datetime.strptime(final_start_time, "%Y-%m-%d %H:%M:%S") + final_time

    df_list = []
    df_list.append(df)
    tat_dev = []
    for i in range(TATAMI):
        tat_dev.append(i+1)


    if bfinal_time.seconds > 0:   
        for x in range(int(bfinal_tat)):
            if bfinal_type == 'Before the final':
                y = int(x) + math.ceil(np.mean(tat_dev)-math.floor((np.std(tat_dev)/3*bfinal_tat)))     
            else:
                z = int(x) + math.ceil(np.mean(tat_dev)-math.floor((np.std(tat_dev)/3*bfinal_tat)))           
                if x < z:
                    y = x +1
                else:
                    y = TATAMI - (bfinal_tat+x)    
            df = pd.DataFrame({'category': "Bronze Final Block",
                               'tatami': y,
                               'end_time': str(bfinal_end_time_c),
                               'start_time': str(bfinal_start_time),
                              'cat_type': 'Final Block'}, index=[0])
            df_list.append(df)


    if final_time.seconds > 0:
        for x in range(int(final_tat)):
            y = int(x) + math.ceil(np.mean(tat_dev)-math.floor((np.std(tat_dev)/3*final_tat)))        
            df = pd.DataFrame({'category': "Final Block",
                              'tatami': y,
                               'end_time': str(end_time_final_c),
                               'start_time': str(final_start_time),
                               'cat_type':'Final Block'}, index=[0])
            df_list.append(df)
  
    df_print = pd.concat(df_list, ignore_index=True, axis=0)

    fig = px.timeline(
        df_print,
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
                  annotation_text=str(end_time_prelim_time)[-8:],
                  annotation_position="top right")

    return fig, end_time_final_c, end_time_prelim_time, final_start_time, bfinal_start_time, bfinal_end_time_c


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
            0, len(permutations_list))}
    _hover = []
    
    for i in range(0, len(row_labels)):
        _hover.append(
            [str(perm_map[int(data[i][j])]) for j in range(0, len(col_labels))])

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


def make_input(cat_par_inp):
    '''
    Loops of the input files and returns the selected age divisions and
    disciplines in the GUI

    Parameters
    ----------
    cat_par_inp
        dictionary with categories and number of participants
        of each category [dict]
    '''

    for cat_name in cat_par_inp:  # loop over dictionary
        if ("U12" in cat_name) and ("U12" not in AGE_SEL):
            AGE_SEL.append("U12")
        if ("U14" in cat_name) and ("U14" not in AGE_SEL):
            AGE_SEL.append("U14")
        if ("U16" in cat_name) and ("U16" not in AGE_SEL):
            AGE_SEL.append("U16")
        if ("U18" in cat_name) and ("U18" not in AGE_SEL):
            AGE_SEL.append("U18")
        if ("U21" in cat_name) and ("U21" not in AGE_SEL):
            AGE_SEL.append("U21")
        if ("Adults" in cat_name) and ("Adults" not in AGE_SEL):
            AGE_SEL.append("Adults")
        if ("Master" in cat_name) and ("Master" not in AGE_SEL):
            AGE_SEL.append("Master")
        if len(AGE_SEL) == 0:
            st.write("No age divisions in input file")

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

    return AGE_SEL, DIS_SEL


def timing(start_time):
    ''' The sidebar elements for the timing

    Parameters
    ----------
    start_time
        start time of the event
    '''
    st.sidebar.image("https://i0.wp.com/jjeu.eu/wp-content/uploads/2018/08/jjif-logo-170.png?fit=222%2C160&ssl=1",
                     use_column_width='always')
    st.sidebar.header('Change settings for event')

    start_time_wid_day_inp = st.sidebar.time_input('Start time of the event',
                                                   value=start_time)
    breaktype_inp = st.sidebar.selectbox('What type of break do you want',
                                         ('Individual', 'One Block', 'No break'), key='breakt')
    if breaktype_inp != 'No break':
        breakl_wid_day_inp = st.sidebar.time_input('Length of the break',
                                                   help='[hh:mm]',
                                                   value=time(0, 30))
        btime_wid_day_inp = st.sidebar.time_input('Start time of the break', 
                                                  help='[hh:mm]',
                                                  value=time(12, 00))
    else:
        breakl_wid_day_inp = time(0, 30)
        btime_wid_day_inp = time(12, 0)
    split_inp = st.sidebar.checkbox('Split large categories',
                                    help='If a category is larger than the average end \
                                    time if is split on 2 tatamis, 1/3 and 2/3. \
                                    Only use this if you know how to schedule it that no matches overlap')
    return start_time_wid_day_inp, breaktype_inp, breakl_wid_day_inp, btime_wid_day_inp, split_inp

def api_call(cat_par):
    ''' Overrides the number of participants with the number in sportdata
    Parameters
    ----------
    cat_par
        dictionary with categories and number of participants
        of each category [dict]
    '''
    apidata = st.sidebar.checkbox("Get registration from Sportdata API",
                                  help="Will overwrite athletes from .csv with registration")
    if apidata is True:
        # get upcoming events
        uri_upc = "https://www.sportdata.org/ju-jitsu/rest/events/upcoming/"
        response = requests.get(uri_upc,
                                auth=HTTPBasicAuth(st.secrets['user'],
                                                   st.secrets['password']),
                                                   timeout=5)
        d_upc = response.json()
        df_upc = json_normalize(d_upc)
        evts = df_upc['name'].tolist()
        evts.append('Other')
        option = st.sidebar.selectbox("Choose your event", evts,
                                      help='if the event is not listed choose Other')

        if option == 'Other':
            sd_key = st.sidebar.number_input("Enter the Sportdata event number",
                                             help='the number behind vernr= in the URL', value=0)
        else:
            sd_key = int(df_upc['id'][df_upc['name'] == option])

        if sd_key > 0:
            cat_par = getdata(str(sd_key), st.secrets['user'], st.secrets['password'])
            if len(cat_par) < 1:
                st.sidebar.warning("This event has no valid categories ", icon="🚨")

    return cat_par


def final_setting(final, TATAMI):
    ''' The sidebar elements for the final settings

    Parameters
    ----------
    FINAL
        bool to say if there is a final block planned
    '''
    st.sidebar.markdown("""---""")
    final = st.sidebar.checkbox('Final block',
                                help='If you check this box the event will have a separate final block',
                                value=final)

    if final is True:
        final_tat_inp = st.sidebar.number_input('Finals tatamis',
                                                help='On how many tatamis will the finals run',
                                                value=1, min_value = 1,max_value= TATAMI)
        final_show_inp = st.sidebar.checkbox('Final show & awards',
                                             help='Adds additional time for entrance and awards')

        if final_show_inp is True:
            show_extra_t_inp = st.sidebar.number_input('Add time for show in minutes',
                                                       value=7)
        else:
            show_extra_t_inp = 0

        final_fix_start_time = st.sidebar.checkbox('Fix start time of finals',
                                                   help='Select a fixed start time when the finales should begin') 
        if final_fix_start_time is True:
            final_start_time = st.sidebar.time_input('Start time of the finals',
                                                     help='[hh:mm]',
                                                     value=time(15, 00))
        else:
            final_start_time = None
        bronze_finals = st.sidebar.checkbox('Include the bronze fight',
                                            help='Add the bronze fights to the final block.')
        ms_mode = st.sidebar.checkbox('Add extra fight for bronze',
                                            help='Use this for TWG & CG.')
        if bronze_finals is True:
            bf_type = st.sidebar.selectbox('How should the bronze finals be held',
                                           ('Before the final', 'Parallel to the finals [BETA]'))
            bfinal_tat_max = TATAMI
            if bf_type == "Parallel to the finals":
                bfinal_tat_max = TATAMI - final_tat_inp
            bfinal_tat_inp = st.sidebar.number_input('Bronze finals tatamis',
                                                     help='On how many tatamis will the bronze finals run',
                                                     value=2, min_value = 1, max_value= bfinal_tat_max)

        else:
            bfinal_tat_inp = 1
            bf_type = None

    else:
        final_tat_inp = 1
        show_extra_t_inp = 0
        final_show_inp = False
        final_fix_start_time = False
        final_start_time = None
        bronze_finals = False
        bfinal_tat_inp = 1
        bf_type = None

    return final, final_tat_inp, final_show_inp, show_extra_t_inp, final_fix_start_time, final_start_time, bronze_finals, bfinal_tat_inp, bf_type, ms_mode


permutations_object = itertools.permutations(DIS_INP)
permutations_list = list(permutations_object)

cat_par = {}  # number of participants
cat_dict_day = {}  # day per category

st.header('Tournament Calculator')

LINK = '[Click here for tutorial](https://tournamentcalculator.readthedocs.io/en/latest/tutorial.html)'
st.markdown(LINK, unsafe_allow_html=True)

left_column_2, right_column_2 = st.columns(2)
with left_column_2:
    st.subheader("New Tournament")
    tour_name = st.text_input("Name of the tournament", key='tour_name_key_inp'+str(random.randint(0, 100)), value="")
    fname = tour_name + ".csv"
with right_column_2:
    st.subheader("Read in file")
    uploaded_file = st.file_uploader("Choose a file",
                                     help="Make sure to have a CSV with the right input")

if uploaded_file is not None:
    cat_par_inp, cat_dict_day, FINAL, TATAMI, days, \
        start_time, breaktype, date_inp = read_in_file(uploaded_file)
    tour_name = str(uploaded_file.name)[:-4]
    fname = tour_name + ".csv"
    st.write("Make the planning for", tour_name)

    try:
        date_time_obj = datetime.strptime(date_inp[0:10], '%Y-%m-%d')
    except ValueError:
        try:
            date_time_obj = datetime.strptime(date_inp[0:10], '%d/%m/%Y')
        except ValueError:
            st.exception("Oops! That was no date. We will use today")
            date_time_obj = datetime.today()
    try:
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    except ValueError:
        st.exception("Oops! That was no time. We will use 9:00")
        start_time = time(9, 0)
    AGE_SEL, DIS_SEL = make_input(cat_par_inp)
    cat_par = cat_par_inp

elif len(tour_name) > 0 and os.path.isfile(check_file):
    st.write("Tournament with name ", tour_name, "already exist")
    newf = st.selectbox('What do you want to do?', ['USE', 'OVERRIDE'])
    if newf == 'USE':
        cat_par_inp, cat_dict_day, FINAL, TATAMI, days, \
            start_time, breaktype, date_inp = read_in_file(check_file)
        print("date ", date_inp)
        try:
            date_time_obj = datetime.strptime(date_inp[0:10], '%d/%m/%Y')
        except ValueError:
            st.exception("Oops! That was no date. We will use today")
            date_time_obj = datetime.today()
        try:
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        except ValueError:
            st.exception("Oops! That was no time. We will use 9:00")
            start_time = time(9, 0)

        AGE_SEL, DIS_SEL = make_input(cat_par_inp)
        cat_par = cat_par_inp

    else:
        TATAMI = 3
        days = 1
        FINAL = True
        date_time_obj = datetime.today()
        start_time = time(9, 0)
else:
    TATAMI = 3
    days = 1
    FINAL = True
    date_time_obj = datetime.today()
    start_time = time(9, 0)

# all on the sidebar:
start_time_wid_day, breaktype, breakl_wid_day, btime_wid_day, SPLIT = timing(start_time)

# overrides the data from the input csv
cat_par = api_call(cat_par)

FINAL, final_tat, final_show, show_extra_t, f_fix_start_time, f_start_time, \
    bfinals, bfinal_tat_inp, bfinal_type, ms_mode = final_setting(FINAL, TATAMI)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    TATAMI = st.number_input("Number of tatamis", value=TATAMI, key='tatami')
with middle_column:
    days = st.number_input("Number of days", value=days, key='days')
with right_column:
    date = st.date_input('First day of the event', value=date_time_obj, key='date')

left_column, right_column = st.columns(2)
with left_column:
    age_select = st.multiselect('Select the participating age divisions',
                                AGE_INP,
                                AGE_SEL)
with right_column:
    dis_select = st.multiselect('Select the participating disciplines',
                                DIS_INP,
                                DIS_SEL)

cat_all = cal_cat(age_select, dis_select)  # calculate categories

random_inp = st.checkbox('Random participants')
tot_par = 0
input_df = pd.DataFrame()
with st.expander("Hide categories"):

    st.info("If you make changes here, don't forget to Download the data again",icon="🚨")
    left_column1, right_column2 = st.columns(2)
    for i in cat_all:

        if random_inp is True:
            val = round(np.random.normal(8, 5.32))
            while val < 0:
                val = round(np.random.normal(8, 5.32))
        elif len(cat_par) > 0:
            val = cat_par.get(i, 0)
        else:
            val = 0

        if random_inp is True:
            val1 = np.random.randint(1, days+1)
        elif len(cat_dict_day) > 0:
            val1 = cat_dict_day.get(i, 1)
        else:
            val1 = 1

        input_df = input_df.append({'Category Name': str(i),
                                    'Number of athletes': int(val),
                                    'Competition day': int(val1)}, ignore_index=True)
        tot_par += int(val)

    edited_df = st.experimental_data_editor(input_df)
    edited_df['Number of athletes'] = ['Number of athletes'].astype(int)
    edited_df['Competition day'] = ['Competition day'].astype(int)

    if (len(cat_all) > 0) and (len(edited_df[~edited_df['Competition day'].between(1, days)]))>0:
        mis_cat = edited_df['Category Name'].values[~edited_df['Competition day'].between(1, days)]
        st.warning("These categories are not correctly scheduled " + str(mis_cat),icon="⚠️")

    if (len(cat_all) > 0) and len(edited_df[edited_df['Number of athletes'] < 0]) > 0:
        wrong_cat = edited_df['Category Name'].values[edited_df['Number of athletes'] < 0]
        st.error("These categories have negative athletes and will be ignored " + str(wrong_cat),icon="🚨")
        edited_df['Number of athletes'][edited_df['Number of athletes'] < 0] = 0

for key in cat_par.copy().keys():
    if key not in cat_all:
        st.write("You have not chosen the age division/disciple of ", key, "as input")
        cat_par.pop(key, None)

# lists with default values
tatami_day = [int(TATAMI)] * int(days)
start_time_day = [start_time] * int(days)
btime_day = [time(00, 00)] * int(days)
btype_day = [breaktype] * int(days)
bt_index = ['Individual', 'One Block', 'No break'].index(breaktype)
breaklength_day = [time(0, 00)] * int(days)
end_time_final = [time(00, 00)] * int(days)
end_time_prelim = [time(00, 00)] * int(days)
final_day = [FINAL] * int(days)
final_tat_day = [1] * int(days)
bfinal_day = [bfinals] * int(days)
bfinal_tat_day = [1] * int(days)

f_fix_start_time_day = [f_fix_start_time] * int(days)
f_start_time_day = [time(15, 00)] * int(days)

cols = st.columns(days)


for j in range(days):
    col = cols[j%5]
    with col:
        with st.expander("Change settings for day "
                         + str(j + 1) + " : " + str(date + timedelta(days=j))):
            st.write("with this settings you can fine tune your event ")

            tatami_day[j] = int(st.number_input("Number of tatamis",
                                                value=int(TATAMI), key=j))
            start_time_wid_days = st.time_input('Start time of the event',
                                                value=start_time_wid_day, key="start_time_" + str(j))
            btype_day[j] = st.selectbox('What type of break do you want',
                                       ('Individual', 'One Block', 'No break'), index=bt_index, key="break_type_" + str(j))
            if btype_day[j] != 'No break':
                btime_wid_day = st.time_input('Start time of the break',
                                              value=btime_wid_day, key="start_time_break" + str(j))
                breakl_wid_day = st.time_input('Length of the break',
                                              value=breakl_wid_day, key="length_break" + str(j))
            final_day[j] = st.checkbox('Final block', value=FINAL, key= "final_"+ str(j))
            if final_day[j] is True:
                f_fix_start_time_day[j] = st.checkbox('Fix start time of finals',
                                             help='Select a fixed start time when the finales should begin',
                                             value = f_fix_start_time_day[j],  key= "fix_start_time_day"+str(j))
            if f_fix_start_time_day[j] is True:
                f_start_time_day[j] = st.time_input('Start time of the finals', help='[hh:mm]',
                                                  value=f_start_time,  key="start_time_day_finals" + str(j))
            else:
                f_start_time_day[j] = None

            if final_day[j] is True:
                final_tat_day[j] = st.number_input('Finals tatamis',
                                                   value=final_tat, key="final_tat" + str(j))
                bfinal_day[j] = st.checkbox('Include Bronzefinals', value=bfinals, key="bfinals" +str(j))
                if bfinal_day[j] is True:
                    bfinal_tat_day[j] = st.number_input('Bronzefinals tatamis',
                                                        help='On how many tatamis will the bronze finals run',
                                                        value=bfinal_tat_inp, key= "bfinals_tat" +str(j))
            # convert time to datetime object
            start_time_day[j] = (datetime.combine(date.min,
                                 start_time_wid_days) - datetime.min)
            # convert break time to hours after start
            btime_day[j] = datetime.combine(date.min, btime_wid_day) - datetime.combine(date.min, start_time_wid_days)
            breaklength_day[j] = (datetime.combine(date.min,
                                  breakl_wid_day) - datetime.min)

fname = tour_name + ".csv"
if st.button('all info is correct'):
    if len(edited_df) == 0:
        st.write("Please add at least one athlete")
    elif len(fname) < 1:
        st.write("Please give the event a name")
    elif TATAMI > len(cat_all):
        st.write("You have more tatamis than disciplines, \
                 please add disciplines or reduce tatamis")
    else:
        tour_file = write_tour_file(tour_name,
                                    edited_df,
                                    TATAMI,
                                    days,
                                    FINAL,
                                    start_time,
                                    date,
                                    breaktype)
        with open(fname, "r") as file:
            btn = st.download_button(
                label="Download data from event",
                data=file,
                file_name=fname,
                mime="csv")

        # new pdf in landscape
        pdf = PDF('L', tour_name)
        pdf.add_page()
        pdf.alias_nb_pages()
        pdf.set_font("Arial", size=20)
        pdf.cell(200, 20, txt="Proposed planning ", ln=1, align='C')
        pdf.set_font("Arial", size=12)

        cat_fights_dict, cat_finals_dict, cat_time_dict, \
            par_num_total, fight_num_total, \
            tot_time, final_time, cat_bfinals_dict, bfinal_time = calculate_fight_time(cat_par, FINAL, bfinals, ms_mode)

        st.write("There are", tot_par, "participants, which will fight",
                 fight_num_total, " matches in ", len(cat_all),
                 "categories with a total time fight time of (HH:MM:SS)",
                 tot_time + final_time)
        st.markdown("---")

        data = []
        for j in range(0, days):
            cat_par_day = edited_df[edited_df['Competition day'] == j+1]
            cat_par_day = cat_par_day.set_index('Category Name')[['Number of athletes']].to_dict()
            cat_par_day = json_normalize(cat_par_day['Number of athletes'])

            pdf.cell(200, 10, txt="Categories on Day " + str(date + timedelta(days=j)), ln=1, align='L')
            blu = edited_df['Category Name'][edited_df['Competition day']==j+1].tolist()
            pdf.multi_cell(250, 5, txt=str(blu), align='L')
            cat_fights_dict, cat_finals_dict, cat_time_dict, \
                par_num_total, fight_num_total, \
                tot_time, \
                final_time, cat_bfinals_dict, \
                bfinal_time = calculate_fight_time(cat_par_day,
                                                   final_day[j], bfinal_day[j], ms_mode)

            av_time = tot_time / int(tatami_day[j])

            final_time = final_time / int(final_tat_day[j])
            bfinal_time = bfinal_time / int(bfinal_tat_day[j])
            if final_show is True:
                final_time += len(cat_finals_dict)*timedelta(minutes= show_extra_t)
            stringheader = "Day: " + str(date + timedelta(days=j))
            st.header(stringheader)
            st.write("There are", par_num_total,
                     "participants, which will fight", fight_num_total,
                     " matches in ", len(cat_time_dict),
                     "categories with a total time fight time of (HH:MM:SS)",
                     tot_time + final_time)
            with st.expander("Show categories"):
                st.write(str(blu))
            if par_num_total > 1:
                if final_day[j]:
                    st.write("You have ", len(cat_finals_dict),
                             "finals, which will take", final_time,
                             "on ",  int(final_tat_day[j]), "tatamis")
                if bfinal_day[j]:
                    st.write("You have 2x ", len(cat_bfinals_dict), " = ",
                             len(cat_bfinals_dict)*2,
                             "bronze finals, which will take", bfinal_time,
                             "on ",  int(bfinal_tat_day[j]), "tatamis")
                st.write("Optimal solution time per tatami will be",
                         av_time, "with", tatami_day[j],
                         "tatamis.")

                if SPLIT == True:
                    cat_time_dict = split_categories(cat_time_dict, av_time)

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
                                                         btype_day[j],
                                                         btime_day[j],
                                                         breaklength_day[j])

                best_res = {k: v for k, v in sorted(most_abundand.items(),
                            key=lambda item: item[1], reverse=True)}

                pen_time = DIS_CHA_TIME//2  # chosen penalty time
                permut_num = int(list(best_res)[0])  # chosen permutation

                st.write("Permutation ", permut_num, " ",
                         permutations_list[permut_num],
                         "gives best result ",
                         best_res[permut_num], "times")

                fig, end_time_final[j], end_time_prelim[j], start_time_final, bfinal_start_time, bfinal_end_time_c = plot_schedule_time(
                         scheduled_jobs[pen_time][permut_num],
                         cat_time_dict_new[pen_time][permut_num],
                         start_time_day[j],
                         date+timedelta(days=j), final_time, f_start_time_day[j],
                         bfinal_type, bfinal_time, final_tat_day[j], bfinal_tat_day[j])

                st.plotly_chart(fig)
                st.write("Start time day:",
                         str(start_time_day[j]),
                         "  \n Finals can start at: ",
                         str(start_time_final)[-8:],
                         "  \n Day ends at: ",
                         str(end_time_final[j])[-8:])

                # workaround to the get right format
                start_day_dt = datetime.combine(date, time(0, 0))

                # add lists for overview

                st.write(start_time_final)
                data.append(["Preliminaries",
                            start_day_dt + start_time_day[j],
                            datetime.strptime(end_time_prelim[j], "%Y-%m-%d %H:%M:%S") - timedelta(days=j),
                            str(date + timedelta(days=j))])
                data.append(["Final",
                            datetime.strptime(start_time_final, "%Y-%m-%d %H:%M:%S") - timedelta(days=j),
                            end_time_final[j] - timedelta(days=j),
                            str(date + timedelta(days=j))])
                data.append(["Bronzefinals",
                            datetime.strptime(bfinal_start_time, "%Y-%m-%d %H:%M:%S") - timedelta(days=j),
                            bfinal_end_time_c - timedelta(days=j),
                            str(date + timedelta(days=j))])

                LABEL = "There are " + str(len(most_abundand)) + \
                        " possible results for day "\
                        + str(j + 1) + ". Open Details"

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

                        fig, end_time_final[j], end_time_prelim[j], start_time_final, bfinal_start_time, bfinal_end_time_c \
                            = plot_schedule_time(scheduled_jobs[pen_time][permut_num],
                                                 cat_time_dict_new[pen_time][permut_num],
                                                 start_time_day[j],
                                                 date+timedelta(days=j), final_time,
                                                 f_start_time_day[j], bfinal_type,
                                                 bfinal_time, final_tat_day[j], bfinal_tat_day[j])

                        st.plotly_chart(fig)
                        st.write("Start time day:",
                                 str(start_time_day[j])[-8:],
                                 "  \n Final can start at: ",
                                 str(start_time_final)[-8:],
                                 "  \n Day ends at: ",
                                 str(end_time_final[j])[-8:])
                        k += 1

                    st.write("Matrix with the results")
                    fig1 = heatmap(min_id,
                                   pen_time_list,
                                   happiness,
                                   "Best permutation")
                    st.write(fig1)
            else:
                st.info('Nothing happens at this day', icon="ℹ️")
                data.append(["Preliminaries",
                            start_day_dt + start_time_day[j],
                            start_day_dt + start_time_day[j],
                            str(date + timedelta(days=j))])
                data.append(["Final",
                            start_day_dt + start_time_day[j],
                            start_day_dt + start_time_day[j],
                            str(date + timedelta(days=j))])
                data.append(["Bronzefinals",
                            start_day_dt + start_time_day[j],
                            start_day_dt + start_time_day[j],
                            str(date + timedelta(days=j))])

            st.markdown("---")
            j += 1

        pdf.output("dummy2.pdf")
        with open("dummy2.pdf", "rb") as pdf_file:
            PDFbyte2 = pdf_file.read()

        st.download_button(label="Download Planning",
                           data=PDFbyte2,
                           file_name=tour_name+'.pdf')
        os.remove("dummy2.pdf")

        st.header("Overview for all days")
        df = pd.DataFrame(data, columns=['Type', 'Begin', 'End', 'day'])
        fig = px.timeline(df, x_start='Begin', x_end='End', color='Type', text='day')
        st.write(fig)


st.sidebar.markdown('<a href="mailto:sportdirector@jjif.org">Contact for problems</a>', unsafe_allow_html=True)

LINK = '[Click here for the source code](https://github.com/ClaudiaBehnke86/TournamentCalculator)'
st.markdown(LINK, unsafe_allow_html=True)
