""" my gui"""
import streamlit as st
import numpy as np
import pandas as pd
import sys
import os
from tourcalc import create_input
from tourcalc import main
from tourcalc import new_tour
from tourcalc import cal_cat
from tourcalc import read_in_file
from tourcalc import calculate_fight_time
from datetime import time, datetime, date, timedelta
import matplotlib
import matplotlib.pyplot as plt
import random
import plotly.express as px
import plotly.graph_objects as go

AGE_INP = ["U16", "U18", "U21", "Adults"] #the supported age catergories
DIS_INP = ["Duo", "Show", "Jiu-Jitsu", "Fighting"] # order does not matter -> permutations

AGE_SEL = []
DIS_SEL = []

DIS_CHA = "Discipline change" # indicator of a change of a discipline
DIS_CHA_TIME = 30 #add the changeing time for the change betwenn disciplines in minutes

BREAK = "Break"
#BREAK_TIME = 14400 # 4hrs after start of tournamement
BREAK_LENGTH = 30 # 30 min

def plot_schedule(scheduled_jobs, cat_time_dict, start_time, loads, endtime):
#     '''plots a schedule'''
    
    df = pd.concat([pd.DataFrame([l, [i+1]*len(l)]).T for i, l in enumerate(scheduled_jobs)])
    df.columns = ['category', 'tatami']
    df['time'] = df['category'].replace(cat_time_dict)
    df['time'] = df['time'] + pd.to_datetime('1970/01/01') 

    
    df['category_type'] = df['category']

    df['category_type'].where(~(df['category_type'].str.contains("Jiu-Jitsu")), other="Jiu-Jitsu", inplace=True)
    df['category_type'].where(~(df['category_type'].str.contains("Fighting")), other="Fighting", inplace=True)
    df['category_type'].where(~(df['category_type'].str.contains("Duo")), other="Duo", inplace=True)
    df['category_type'].where(~(df['category_type'].str.contains("Show")), other="Show", inplace=True)
   
    df['gender'] = df['category']
    df['gender'].where(~(df['gender'].str.contains("Men")), other="Men", inplace=True)
    df['gender'].where(~(df['gender'].str.contains("Women")), other="Women", inplace=True)
    df['gender'].where(~(df['gender'].str.contains("Mixed")), other="Mixed", inplace=True)


    order_d = {str(i+1): j for i, j in enumerate(scheduled_jobs)}
    fig = px.bar(df, x='tatami', y='time', color='category_type',hover_name = 'category',text ='category', pattern_shape= 'gender',  category_orders= order_d)
    #fig = px.bar(df, x='tatami', y='time', category_orders= {str(i+1): j for i, j in enumerate(scheduled_jobs)})


    #st.write(order_d)
    #st.write(df)
    
    fig.update_layout(yaxis={'categoryorder':'array', 'categoryarray':df.index})
    #fig.update_layout(yaxis=dict(type='tatami'))
    #fig.update_yaxes(range=(start_time, endtime))
    return fig


def heatmap(data, row_labels, col_labels):
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
    """

    df1 = pd.DataFrame(data)
    df1.rows = row_labels 
    df1.columns = col_labels

    fig1 = go.Figure(data=go.Heatmap(
        z=data,
        x=col_labels,
        y=row_labels ,
        colorscale='Viridis'))
    return fig1


cat_par = {}#number of particpants
cat_dict_day = {}#day per catergory

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

                    for cat_name in cat_par_inp: #loop over dictionary
                        #par_num = int(cat_par_inp.get(cat_name)) #number of fights per catergory
                        #fight_num = 0 # reset counter
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

                    check = 1                
        else:
            check = 1
            

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
   breaklength_wid = st.time_input('Legth of the break', time(0, 30))
   breaktime_wid = st.time_input('Startime of the break', time(13, 00))
   start_time_wid = st.time_input('Start time of the event', time(9, 00))
   day = st.date_input('start date',)

age_select = st.multiselect('Select the participating age categories', AGE_INP, AGE_SEL) 
dis_select = st.multiselect('Select the participating disciplines', DIS_INP, DIS_SEL) 
 
start_time = datetime.combine(date.min, start_time_wid) - datetime.min
breaktime = datetime.combine(date.min, breaktime_wid) - datetime.min - start_time
breaklength = datetime.combine(date.min, breaklength_wid) - datetime.min

cat_all = cal_cat(age_select, dis_select) # calculate catergories


tot_par = 0
with st.expander("Hide categories"):

    left_column1, right_column2 = st.columns(2)   
    for i in cat_all:
        if tour_name == "random":
            _rtmp = round(np.random.normal(8, 5.32))
            while _rtmp < 0:
                _rtmp = round(np.random.normal(8, 5.32))
            with left_column1:
                inp = st.number_input("Number of athletes " + i, min_value= 0, value = _rtmp, key = i )
            day_rtmp = np.random.randint(1,days)
            with right_column2:
                day = st.number_input("Competition day " + i, min_value= 0, value = day_rtmp, key = i)
        else:    
            val = cat_par.get(i)
            if val == None:
                val =  0
            inp = st.number_input("Number of athletes " + i, min_value=0, key = i, value = val)
        tot_par +=  int(inp)
        cat_par[i] = int(inp)
        cat_dict_day[i] = int(day)
    
   
if st.button('all info is correct'):
    if tot_par == 0:
        st.write("Please add at least one athlete")
    elif tatami > len(cat_all):
        st.write("You have more tatamis than disciplines, please add disciplines or reduce tatamis")
    else:
        j = 1 
        st.write("Tournament: ", tour_name)    
        #st.write("There are",tot_par, "participants, which will fight", fight_num_total, " matches in ", \
        #len(cat_all), "categories with a total time fight time of (HH:MM:SS)", tot_time+final_time)
 
        while j <= days:
            cat_par_day = {} 
            for i in cat_par:
                if cat_dict_day[i] == j:
                    cat_par_day[i] = int(cat_par.get(i))
            
            st.write(cat_par_day) 
            scheduled_jobs,cat_time_dict,endtime,loads,pen_time, min_id, pen_time_list, happiness, min_score = main(cat_par_day,i_tatami,final,start_time,breaktype, breaktime, breaklength)  
            
            cat_fights_dict, cat_finals_dict, cat_time_dict_calc, \
                av_time, par_num_total, fight_num_total, tot_time, \
                final_time = calculate_fight_time(cat_par_day, final, i_tatami)
            st.write("Tournament: ", tour_name , " day: " , j )    
            st.write("There are",tot_par, "participants, which will fight", fight_num_total, " matches in ", \
            len(cat_all), "categories with a total time fight time of (HH:MM:SS)", tot_time+final_time)
            st.write("You have", len(cat_finals_dict), "finals which will take", final_time)
            st.write("Optimal solution time per tatami will be", av_time, "with", i_tatami, "tatamis")
            new_tour(tour_name,cat_par,i_tatami,final,start_time,breaktype)  

            st.write(plot_schedule(scheduled_jobs,
                cat_time_dict, start_time.seconds,
                loads,
                endtime/3600+start_time.seconds/3600))

            with st.expander("Details"):
                
                fig1 = heatmap(min_id, pen_time_list, happiness)
                st.write(fig1)
                fig2 = heatmap(min_score, pen_time_list, happiness)
                st.write(fig2)

            cat_par_day.clear() 
            j += 1  
                 
