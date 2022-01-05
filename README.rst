********
TourCalc
********
You can use this program in two ways:


Use deployed app
================

Go on:
`this page <https://share.streamlit.io/claudiabehnke86/tournamentcalculator/tourcalc/theapp.py>`_

use `the tutorial <https://tournamentcalculator.readthedocs.io/en/latest/introduction.html>`_
on to understand what it does

Installation own instance
=========================

Fork the repository and save it at a place where you like it.

The package consist of two files:

calculator.py and theapp.py.


To create the module type
.. code-block::

    pip install tourcalc

To run the gui you need to open the app using streamlit

.. code-block::
    
    streamlit run tourcalc/theapp.py


To create the documentation use:

.. code-block::

    ./docs/build_docs.sh


Needed software 
---------------
   
* numpy==1.21.2
* pandas==1.3.3
* plotly==5.3.1
* setuptools==57.4.0
* sphinx_rtd_theme==1.0.0
* streamlit==1.2.0
