import os, sys
import math
import time
import numpy as np #pip3 install numpy
import pandas as pd
from newTour import newTour
from checkInp import *
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


print("-------------------------")
print("- Tournament Calculator -")
print("-------------------------")
print("Part 1 - Create tournament")
print("")
name = input("Please enter a name for the tournament: ")
print("")
fname = name + ".txt"
check = 0
while check < 1:
    if os.path.isfile(fname):
        print("Tournament with name ", name ,"already exist" )
        print("What do you want to do?")
        print("1. Do you want to override? Type: \"OVERRIDE\"")
        print("!!! Overrinding will delete the exisiting file !!!")
        print("2. Do you want to use the datebase? Type \"USE\"")
        print("3. Do you want to use a different name? Type \"NEW\"")
        newf = input("Please type: \"OVERRIDE\" , \"USE\" or \"NEW\" : ")
        if newf == "OVERRIDE":
            print("New tournament will be created")
            check = 1
            tour = newTour(name)
            tour.createNew()
            continue
        elif newf == "NEW":
            name = input("Please type new name ")
            fname = name + ".txt"
        elif newf == "USE":
            check =1
        else:
            newf = input("This is not valid. Please try again. ")
    else:
        print("New tournament will be created")
        check = 1
        tour = newTour(name)
        tour.createNew()

#------------
# Read in file
#-------------
f= open(fname,"r")
header1 = f.readline() # Read and ignore header lines
tatamis = f.readline() # read in tatami line
tatamiInp = tatamis.split()
tatami = int(tatamiInp[1])
#---
finalT = f.readline()
finInp = finalT.split()
if finInp[1] == "YES":
    final = True
elif finInp[1] == "NO":
    final = False
else:
    print("something is wrong with ", fiIn)
#------
catPar = {} #number of particpants
parCount = 0
for line in f: # Loop over lines and extract variables of interest
    line = line.strip()
    columns = line.split()
    if(columns[1] == "Duo" or columns[1] == "Show"):
        catname = columns[0] + " "+ columns[1] + " " + columns[2]
        j = int(columns[3])
    else:
        catname = columns[0] + " "+ columns[1] + " " + columns[2] +" " + columns[3]
        j = int(columns[4])
    catPar[catname] = int(j)
    parCount += int(j)

time.sleep(1)
print("")
print("")
print("----------------------------")
print("-- Please check your input: -")
print("----------------------------")
print("")
print("Catergories and Participants")
for x,y in catPar.items():
    print(x, y)
i =0
while i < 1:
    check = input("Please type in name of category you want to correct \"OK\" to continue to next step ")
    if check in catPar:
        print("Change catergory", check )
        parCount -= catPar[check]
        newVal  = int(checkNum())
        catPar[check] = newVal
        parCount +=newVal
        print("Updated\nTo show list again type \"SHOW ALL\" ")
    elif check == "SHOW ALL" :
        for x,y in catPar.items():
            print(x, y)
    elif check == "OK":
        i = 1
    else:
        print("Catergory", check , "not known. Please try again")

catCal = {} #number of fights
catTim = {} #time of fights
catFin = {} #tiem of finale block, if exists

lowPat = {0:0, 1:0, 2:3, 3:3, 4: 6, 5:10, 6:9 ,7:12} #fights for low numbers of participants
# 8:11 from 8 on its always +2
timeIn = {"Fighting": timedelta(minutes=5, seconds = 30), "Duo" :timedelta(minutes=7), "Show" :timedelta(minutes=5), "NeWaza": timedelta (minutes=7)}
#timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

for i in catPar:
    addNum = int(catPar.get(i))
    fightnum = 0
    if final == True and addNum >5:
        fightnum = -1
        catFin[i] = {}
        for x in timeIn:
            if x in i: #if name of Discipline is in string of categoroy:
                catFin[i] = timeIn[x]
    if addNum < 8:
        fightnum += lowPat.get(addNum)
    else:
        fightnum += (addNum-8)*2 + 11
    for x in timeIn:
        if x in i: #if name of Discipline is in string of categoroy:
            catTim[i] = timeIn[x] * fightnum
            catCal[i] = fightnum


totTime = timedelta()
finTime = timedelta()
totFight = 0
for i in catTim:
    totTime += catTim.get(i)
    totFight += catCal.get(i)
for i in catFin:
    finTime += catFin.get(i)
totFight +=len(catFin)

print("")
print("----------------------------")
print("--------- Summary ----------")
print("----------------------------")
print("")
print("You have", parCount, "participants, which will fight", totFight , "mathches in",len(catPar),"catergories with a total time fight time of (HH:MM:SS)", totTime+finTime)
print("You have", len(catFin), "finals which will take",finTime)
avTime = totTime/int(tatami)
print("Average time per tatami will be", avTime, "with" , tatami , "tatamis")


print("")
print("----------------------------")
print("----------- Part 3 ---------")
print("---- distribute matches ----")
print("----------------------------")
print("")

#fname = name + "_Tatami.txt"
#check = 0
#while check < 1:
#    if os.path.isfile(fname):
#       print("Tatami Setup with name ", name ,"already exist" )
#       print("What do you want to do?")
#       print("1. Do you want to override? Type: \"OVERRIDE\"")
#       print("!!! Overrinding will delete the exisiting file !!!")
#       print("2. Do you want to use the datebase? Type \"USE\"")
#       print("3. Do you want to use a different name? Type \"NEW\"")
#       newf = input("Please type: \"OVERRIDE\" , \"USE\" or \"NEW\" : ")
#       if newf == "OVERRIDE":
#           print("New tournament will be created")
#           check = 1
#           f1= open(fname + "i.txt","w")
#           continue
#       elif newf == "NEW":
#           name = input("Please type new name ")
#           fname = name + "_Tatami.txt"
#       elif newf == "USE":
#           check =1
#       else:
#           newf = input("This is not valid. Please try again. ")
#   else:
#       print("New tatami setup will be created")
#        check = 1
#        f1= open(fname ,"w")



# Startime
starttime = timedelta(hours = 8, minutes= 30)
print("startime tournament ", starttime)
print("Change time?")
chTime = checkYesNo()
if chTime == True:
    print("Please give NEW startime\nHours: ")
    hNew = -1
    while(hNew > 24 or hNew <0):
        hNew = checkNum()
        if(hNew > 24 or hNew <0): print("Hours must between 0 and 24")
    print("Minutes:")
    mNew = -1
    while(mNew > 60 or mNew <0):
        mNew = checkNum()
        if(mNew > 60 or mNew <0): ("Minutes must between 0 and 60")
    starttime = timedelta(hours = hNew, minutes= mNew)

#########################
caToDis = catPar.copy()


# Print the stuff
frame = "-------------------------------"
i = 0
tname =""
ttime =""

                       
tamiList = [1] * len(catPar)
header = []
while i < tatami:
   
    c = "Tatami" + str(i+1)
    header.append(c)
    header.append(starttime)
    i+=1


df = pd.DataFrame(np.nan, tamiList ,header)



print(df)
#print(tatamiArray)


contr = False
currTime = starttime
testlist = header.copy()
j =0
while contr == False:
    check = input("Please type in name of category you want to assing to tatami: ")
    if check in catPar:
        if check in caToDis:
            print("Move catergory: ", check )
            print("to tatami :")
            taNum = checkNum()-1 # to type tatami 1 and not 0
            if taNum >= tatami:
                print("Tatami No :", taNum, "does not exists. Please try again ")
                continue
            else:
                x = catTim[check] #get the Time from the dictionary
                testlist[taNum] = check
                testlist[taNum+1] = x
                
                df.append(self, testlist)
                       #tatamiArray[j,taNum] = {check: x}
                #tatamiArray += np.insert(tatamiArray, (taNum*2)+1, x )
                del caToDis[check]
                j +=1
                print(df)
        else:
            print("Category ", check , " was already assinged to Tatami ")
            print("Move catergory: ", check )
            print("to follwing Tatami :")
            taNum = checkNum()-1 # to type tatami 1 and not 0
            if taNum >= tatami:
                print("Tatami No :", taNum, "does not exists. Please try again ")
            else:
                print("On posititon Number")
                posNum = checkNum()-1
                x = catTim[check] #get the Time from the dictionary
                currTime += x
                tatamiList[taNum].insert(posNum , {check: x})

               
        print("Updated Type \nTo show tatamis again type \"SHOW TATAMI\" ")
        print("To show open catergories type \"SHOW REST\" ")
        print("To continue type \"OK\" ")

    elif check == "SHOW TATAMI":
        print("smart stuff")
            #print(tatamiArray)
            #print(frame*tatami)
            #print(tname  + "  |")
            #print(frame*tatami)
            #endTime = []
            #prEndTime = " "
            #showCat = ""
            #for j in range(0,len(tatamiList)):
            #   print("j ", j)
            #endTime.append(starttime)
            #for k in range (1, len(tatamiList[j])):
            #for x, y in tatamiList[j][k].items():
                    #currTime += y
                    #print("What is j ", j , "and k", k ," ?" )
                        #showCat += str(x) +"    " + str(y) + "      | "
                        #newTime = endTime[j] + y
                #newTime = newy
                #endTime[j] = newTime
                #prEndTime += "|   " + str(endTime[j]) + "      "
                #print("| " +showCat +"\n")
                #print(frame*tatami)
            #print(prEndTime)
    elif check == "SHOW REST" :
        print(caToDis)

    elif check == "OK":
        if(len(caToDis)!=0):
            print("There are not distributed categories :", caToDis)
        else:
            contr = True
            continue
    else:
        print("Catergory", check , "not known. Please try again")

#for j in range(0,len(tatamiList)):
#   for k in range (0, len(tatamiList[j])):
#       for x, y in tatamiList[j][k].items():
            #currTime = starttime + y
#tatamiList[j][k].items()




#print(tatamiArray)

sys.exit()
#In [37]: for tats in range(0, len(a)):
#    ...:     total_time = timedelta(0)
#    ...:     for i in range(0, len(a[tats])):
#    ...:         for x, y in a[tats][i].items():
#    ...:             total_time+=y
#    ...:             print(total_time)
#    ...:             print(y)
#    ...:     a[tats].append({'total':total_time})


#f1.write
#f1.close()

print(tatamiList)
