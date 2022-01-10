**********************
Installation and Usage
**********************
You can use this program in two ways:


Use deployed app
================

Go on `this page <https://share.streamlit.io/claudiabehnke86/tournamentcalculator/tourcalc/theapp.py>`_
and use `the tutorial <https://tournamentcalculator.readthedocs.io/en/latest/introduction.html>`_
on to understand what it does

Installation own instance
=========================

Fork the `repository <https://github.com/ClaudiaBehnke86/TournamentCalculator>`_ and save it at a place where you like it.

The package consist of two files:

.. code-block::

    calculator.py  
    theapp.py

To create the module type

.. code-block::

    pip install tourcalc

To run the gui you need to open the app using streamlit

.. code-block::
    
    streamlit run tourcalc/theapp.py


To create the documentation use:

.. code-block::

    ./docs/build_docs.sh


Needed software can be found in requirements.txt
   
