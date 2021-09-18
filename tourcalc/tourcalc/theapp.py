""" my gui"""
import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

from tourcalc import create_input
from tourcalc import main

def analysis(input_mode):
    a,b,c,d,e = create_input(input_mode)
    return main(a,b,c,d,e)


input_mode = st.text_input("Name of tournament")
i_tatami = st.text_input("Number of tatamis")
i_breaktime = st.text_input("breaktime")
if st.button('all info is correct'):
    st.write(analysis(input_mode))
#if len(input_mode) > 1:
#    st.write(analysis(input_mode))
