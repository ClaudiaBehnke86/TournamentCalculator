********
Tutorial
********

After the GUI is started your standard browser should have opened. If not browser open you can open one and open the URL from your terminal:

.. code-block::

	You can now view your Streamlit app in your browser.

  	Local URL: http://localhost:8506
  	Network URL: http://192.168.178.46:8506

You will then see the GUI like in picture :numref:`start`

.. _start:
.. figure:: pictures/GUI_start.png

    First input fields of the GUI 

===============
Getting Started
===============

Create a new tournament 
#######################

You can change the vales by typing or using the +/- buttons

#. Enter a name in "Name of the tournament" - [string] 
#. Number of Tatamis - [int] 


Read in existing tournament 
###########################

If the name of the tournament was used before you have two options:

#. *Use*  Will read in all parameters stored in the text file
#. *Overwrite* Creates an empty event and overwrites the existing file

.. _start:
.. figure:: pictures/exist_tour.png

    Options for existing tournament 

Create "random" tournament
##########################

If you name the tournament random the number of athletes and the days for each category will be automatically filled with positive integers, based on:


.. code-block::

	np.random.normal(8, 5.32)

which is a normaldistribution_ with :math:`\mu = 8`, :math:`\sigma = 5.32`. 

This can be used for testing or if one does not exactly know how many participants to expect on a event.
Please note that the random generator will rerun every time a parameters is changed.  

Parameters
##########


Advanced settings
#################

Change settings for per day
###########################


.. _normaldistribution: https://en.wikipedia.org/wiki/Normal_distribution
