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
from tourcalc import cal_cat
from datetime import time, datetime, date, timedelta


input_mode = st.text_input("Name of the tournament")

left_column, right_column = st.columns(2)

with left_column:
    
    i_tatami = st.number_input("Number of tatamis",1)
    days = st.number_input("Number of days",1)

with right_column:    
    final = st.selectbox('Does the event have a final block',
    ('YES', 'NO'))
    breaktype = st.selectbox('What type of break do you want',
    ('Individual','One Block' ,'No break'))

with st.expander("Advanced settings"):
   st.write("with this settings you can finetune your event ")
   breaktime_wid = st.time_input('Legth of te break', time(0, 30))
   start_time_wid = st.time_input('Start time of the event', time(9, 00))

age_select = st.multiselect('Select the participating age categories', ['Adults', 'U21', 'U18', 'U16']) 
dis_select = st.multiselect('Select the participating disciplines', ['Jiu-Jitsu', 'Fighting', 'Duo', 'Show']) 
 
start_time = datetime.combine(date.min, start_time_wid) - datetime.min
breaktime = datetime.combine(date.min, breaktime_wid) - datetime.min

cat_all = cal_cat(age_select, dis_select) # calculate catergories
cat_par = {}#number of particpants

for i in cat_all:
    inp = st.number_input("Number of athletes " + i, min_value=0, key = i)
    cat_par[i] = int(inp)
    
if st.button('all info is correct'):
    
    st.write(main(cat_par,i_tatami,final,start_time,breaktype))        
    