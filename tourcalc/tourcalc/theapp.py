""" my gui"""
import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import sys
import os
from tourcalc import create_input
from tourcalc import main
from tourcalc import new_tour
from tourcalc import cal_cat
from tourcalc import plot_schedule
from tourcalc import read_in_file
from tourcalc import calculate_fight_time
from datetime import time, datetime, date, timedelta
import random

AGE_INP = ["U16", "U18", "U21", "Adults"] #the supported age catergories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"] # order does not matter -> permutations

cat_par = {}#number of particpants
tatami = 1
final = 'NO'

tour_name = st.text_input("Name of the tournament")

if len(tour_name) > 0: 
    #check_tour(tour_name)
    fname = tour_name + ".txt"
    check = 0
    while check < 1:
        if os.path.isfile(fname):
            if tour_name == "random":
                check = 1
                continue
            else:
                st.write("Tournament with name ", tour_name, "already exist")
                newf = st.selectbox('What do you want to do?', ['OVERRIDE', 'USE']) 
                if newf == "OVERRIDE":
                    check = 1
                    continue
                elif newf == "USE":
                    cat_par_inp, final, tatami, starttime, break_t  = read_in_file(tour_name+".txt")
                    cat_par = cat_par_inp
                    st.write(cat_par_inp, final, tatami, starttime, break_t )
 
                    check = 1                
        else:
            check = 1
            continue
st.write(cat_par)

left_column, right_column = st.columns(2)

with left_column:
    
    i_tatami = st.number_input("Number of tatamis",tatami)
    days = st.number_input("Number of days",1)

with right_column:    
    final = st.selectbox('Does the event have a final block',
    ('YES', 'NO'))
    breaktype = st.selectbox('What type of break do you want',
    ('Individual','One Block' ,'No break'))

if final == 'YES': 
    final = True
else: final = False

with st.expander("Advanced settings"):
   st.write("with this settings you can finetune your event ")
   breaktime_wid = st.time_input('Legth of te break', time(0, 30))
   start_time_wid = st.time_input('Start time of the event', time(9, 00))

age_select = st.multiselect('Select the participating age categories', AGE_INP,) 
dis_select = st.multiselect('Select the participating disciplines', DIS_INP) 
 
start_time = datetime.combine(date.min, start_time_wid) - datetime.min
breaktime = datetime.combine(date.min, breaktime_wid) - datetime.min

cat_all = cal_cat(age_select, dis_select) # calculate catergories


tot_par = 0
with st.expander("Hide categories"):
    for i in cat_all:
        if tour_name == "random":
            _rtmp = round(np.random.normal(8, 5.32))
            while _rtmp < 0:
                _rtmp = round(np.random.normal(8, 5.32))
            inp = st.number_input("Number of athletes " + i, min_value= 0, value = _rtmp, key = i )
        else:    
            inp = st.number_input("Number of athletes " + i, min_value=0, key = i)
        tot_par +=  int(inp)
        cat_par[i] = int(inp)
    
if st.button('all info is correct'):
    if tot_par == 0:
        st.write("Please add at least one athlete")
    else:
        scheduled_jobs,cat_time_dict,endtime,loads = main(cat_par,i_tatami,final,start_time,breaktype)  
        
        cat_fights_dict, cat_finals_dict, cat_time_dict, \
            av_time, par_num_total, fight_num_total, tot_time, \
            final_time = calculate_fight_time(cat_par, final, i_tatami)

        st.write("There are",tot_par, "participants, which will fight", fight_num_total, " matches in ", \
        len(cat_all), "categories with a total time fight time of (HH:MM:SS)", tot_time+final_time)
        st.write("You have", len(cat_finals_dict), "finals which will take", final_time)
        st.write("Optimal solution time per tatami will be", av_time, "with", i_tatami, "tatamis")
        new_tour(tour_name,cat_par,i_tatami,final,start_time,breaktype)  
    

        st.write(plot_schedule(scheduled_jobs,
            cat_time_dict, start_time.seconds,
            loads,
            endtime/3600+start_time.seconds/3600))
