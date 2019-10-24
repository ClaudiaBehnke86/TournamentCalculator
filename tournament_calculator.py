""" This module should be used to create a tournament
But moslty it is used for me to have a hands on example for python
 """
import sys
import os
import math
import time
import numpy as np #pip3 install numpy
import pandas as pd #pip install pandas

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def main():
    """ The main function """
    print("-------------------------")
    print("- Tournament Calculator -")
    print("-------------------------")
    print("Part 1 - Create tournament")
    print("")
    name = input("Please enter a name for the tournament: ")
    print("")
    
    check_tour(name)
    catPar = read_in_file(name+".txt")

    print("")
    print("")
    print("----------------------------")
    print("-- Please check your input: -")
    print("----------------------------")
    print("")
    print("Catergories and Participants")
    
    for x, y in catPar.items():
        print(x, y)
    i = 0
    while i < 1:
        check = input("Please type in name of category you want to correct"\
                      "OK\" to continue to next step ")
        if check in catPar:
            print("Change catergory", check)
            parCount -= catPar[check]
            newVal = int(checkNum())
            catPar[check] = newVal
            parCount += newVal
            print("Updated\nTo show list again type \"SHOW ALL\" ")
        elif check == "SHOW ALL":
            for x, y in catPar.items():
                print(x, y)
        elif check == "OK":
            i = 1
        else:
            print("Catergory", check, "not known. Please try again")

    catCal = {} #number of fights
    catTim = {} #time of fights
    catFin = {} #tiem of finale block, if exists

    lowPat = {0:0, 1:0, 2:3, 3:3, 4:6, 5:10, 6:9, 7:12} #fights for low numbers of participants
    # 8:11 from 8 on its always +2
    timeIn = {"Fighting":timedelta(minutes=5, seconds=30),
              "Duo":timedelta(minutes=7),
              "Show":timedelta(minutes=2),
              "NeWaza":timedelta(minutes=7)}
    #timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    for i in catPar:
        addNum = int(catPar.get(i))
        fightnum = 0
        if final == True and addNum > 5:
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
    totFight += len(catFin)

    print("")
    print("----------------------------")
    print("--------- Summary ----------")
    print("----------------------------")
    print("")
    print("You have",
          parCount, "participants, which will fight ",
          totFight, "mathches in",
          len(catPar), "catergories with a total time fight time of (HH:MM:SS)",
          totTime+finTime)
    print("You have", len(catFin), "finals which will take", finTime)
    avTime = totTime/int(tatami)
    print("Average time per tatami will be", avTime, "with", tatami, "tatamis")

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
    starttime = timedelta(hours=8, minutes=30)
    print("startime tournament ", starttime)
    print("Change time?")
    chTime = checkYesNo()
    if chTime == True:
        print("Please give NEW startime\nHours: ")
        hNew = -1
        while(hNew > 24 or hNew < 0):
            hNew = checkNum()
            if(hNew > 24 or hNew < 0): print("Hours must between 0 and 24")
        print("Minutes:")
        mNew = -1
        while(mNew > 60 or mNew < 0):
            mNew = checkNum()
            if(mNew > 60 or mNew < 0): ("Minutes must between 0 and 60")
        starttime = timedelta(hours=hNew, minutes=mNew)

    #########################
    caToDis = catPar.copy()


    # Print the stuff
    frame = "-------------------------------"
    i = 0
    tname = ""
    ttime = ""

    tamiList = [1] * len(catPar)
    header = []
    while i < tatami:
        c = "Tatami" + str(i+1)
        header.append(c)
        header.append(starttime)
        i += 1

    df = pd.DataFrame(np.nan, tamiList, header)

    print(df)
    #print(tatamiArray)

    contr = False
    currTime = starttime
    testlist = header.copy()
    j = 0
    while contr == False:
        check = input("Please type in name of category you want to assing to tatami: ")
        if check in catPar:
            if check in caToDis:
                print("Move catergory: ", check)
                print("to tatami :")
                taNum = checkNum()-1 # to type tatami 1 and not 0
                if taNum >= tatami:
                    print("Tatami No :", taNum, "does not exists. Please try again")
                    continue
                else:
                    x = catTim[check] #get the Time from the dictionary
                    testlist[taNum] = check
                    testlist[taNum+1] = x
                    df.append(self, testlist)
                           #tatamiArray[j,taNum] = {check: x}
                    #tatamiArray += np.insert(tatamiArray, (taNum*2)+1, x )
                    del caToDis[check]
                    j += 1
                    print(df)
            else:
                print("Category ", check, " was already assinged to Tatami")
                print("Move catergory: ", check)
                print("to follwing Tatami :")
                taNum = checkNum()-1 # to type tatami 1 and not 0
                if taNum >= tatami:
                    print("Tatami No :", taNum, "does not exists. Please try again ")
                else:
                    print("On posititon Number")
                    posNum = checkNum()-1
                    x = catTim[check] #get the Time from the dictionary
                    currTime += x
                    tatamiList[taNum].insert(posNum, {check: x})
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
        elif check == "SHOW REST":
            print(caToDis)

        elif check == "OK":
            if len(caToDis) != 0:
                print("There are not distributed categories :", caToDis)
            else:
                contr = True
                continue
        else:
            print("Catergory", check, "not known. Please try again")

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

def checkYesNo():
    check = False
    inp1 = input("Please type Yes / No : ")
    while check == False:
        if inp1 == "Yes":
            inp1 = True
            check = True
        elif inp1 == "No":
            inp1 = False
            check = True
        else:
            inp1 = input("Invaid! Please enter YES or NO")
    return inp1

def checkNum():
    user_input = input("Please enter a number ")
    try:
        val = int(user_input)
    except ValueError:
        print("Please enter a valid number")
    return val

def newTour(name):
    f = open(name + ".txt", "w")
    print("How many tatmis will be there: ")
    tatami = checkNum()
    print("")
    print("Will there be a final block")
    final = checkYesNo()

    print("Tournament:", name, "will be created with ", tatami, " tatamis")

    f.write("Tournament: " + name + "\n")
    f.write("Tatamis: " + str(tatami) + "\n")

    if final == True:
        print("Tournament has a final block")
        f.write("Finalblock: YES \n")
    elif final == False:
        print("Tournament has NO final block")
        f.write("Finallblock: NO \n")
    else:
        print("You should never see this. Something is VERY wrong here!!!")

    time.sleep(2)
    print("------------------------")
    print("--- Age catergories ---")
    print("------------------------")
    print("Which age catergories will compete?")
    ageIn = ["U16", "U18", "U21", "Adults"]
    print("Possible catergories", ageIn)
    print()
    print("Type: \"ALL\" to add all categories")

    i = 0
    ageSel = []
    while i < len(ageIn):
        addCat = input("Please type in name of category or type \
        \"OK\" to continue to next step ")
        if addCat == "ALL":
            ageSel = ageIn.copy()
            print("All categories are added")
            break
        elif addCat in ageIn:
            ageSel.append(addCat)
            print(addCat, "added")
            i += 1
        elif addCat == "OK":
            if i == 0:
                print("You must add minimum ONE Age category")
            else:
                break
        else:
            print("Categorie ", addCat, "not known. Please try again")
    print("")
    print("The following age categories are added")
    print(ageSel)
    time.sleep(2)

    print("")
    print("------------------------")
    print("--- Disciplines -------")
    print("------------------------")
    print("Which disciplines will compete?")
    disIn = ["Fighting", "Duo", "Show", "Ne-Waza"]
    print("Possible categories:", disIn)
    print("Type: ""ALL"" to add all categories")

    i = 0
    disSel = []
    while i < len(disIn):
        addCat = input("Please type in name of diszipline or type \
                        \"OK\" to continue to next step ")
        if addCat == "ALL":
            disSel = disIn.copy()
            print("All disziplines are added")
            break
        elif addCat in disIn:
            disSel.append(addCat)
            print(addCat, "added")
            i += 1
        elif addCat == "OK":
            if i == 0:
                print("You must add minimum ONE discipline")
            else:
                break
        else:
            print("Diszipline ", addCat, "not known. Please try again")
    print("")
    print("The following disciplines are added:", disSel)
    #print(disSel)
    time.sleep(2)

    print("------------------------")
    print("calcualtion of weight categories")

    weightW = [45, 48, 52, 57, 63, 70, 71]
    weightW18 = [40, 44, 48, 52, 57, 63, 70, 71]
    weightW16 = [32, 36, 40, 44, 48, 52, 57, 63, 61]

    weightM = [56, 62, 69, 77, 85, 94, 95]
    weightM18 = [46, 50, 55, 60, 66, 73, 81, 82]
    weightM16 = [38, 42, 46, 50, 55, 60, 66, 73, 74]

    catTeam = {"Women", "Men", "Mixed"}

    catAll = []
    for i in ageSel: #Looping AgeCategories
        for j in disSel: #Looping Disziplines
            if(j == "Duo" or j == "Show"):
                for k in catTeam:
                    catAll.append(i +" "+ j + " " + k)
            elif i == "U16":
                for k in weightM16:
                    catAll.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weightW16:
                    catAll.append(i +" "+ j + " Women "+ str(k)+"kg")
            elif i == "U18":
                for k in weightM18:
                    catAll.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weightW18:
                    catAll.append(i +" "+ j + " Women "+ str(k)+"kg")
            else:
                for k in weightM:
                    catAll.append(i +" "+ j + " Men "+ str(k)+"kg")
                for k in weightW:
                    catAll.append(i +" "+ j + " Women "+ str(k)+"kg")
    time.sleep(2)
    print(" ")
    print("You have created the following categories")
    print(catAll)
    print("In total ", len(catAll), "catergories have been created for Tournament", name)
    print()
    time.sleep(2)

    print("----------------------------")
    print("- Part 2 - Add Competitors -")
    print("----------------------------")
    catPar = {}#number of particpants
    print("Please add the number of participants for each category: ")
    for i in catAll:
        fightnum = 0
        print("Number of competitors in", i)
        inp = checkNum()
        if inp <= 0:
            continue
        catPar[i] = int(inp)

    time.sleep(1)

    for x, y in catPar.items():
        f.write(str(x) +" "+ str(y) + "\n")

    f.close()
    
def check_tour(name):
    fname = name + ".txt"
    check = 0
    while check < 1:
        if os.path.isfile(fname):
            print("Tournament with name ", name, "already exist")
            print("What do you want to do?")
            print("1. Do you want to override? Type: \"OVERRIDE\"")
            print("!!! Overrinding will delete the exisiting file !!!")
            print("2. Do you want to use the datebase? Type \"USE\"")
            print("3. Do you want to use a different name? Type \"NEW\"")
            newf = input("Please type: \"OVERRIDE\" , \"USE\" or \"NEW\" : ")
            if newf == "OVERRIDE":
                print("New tournament will be created")
                check = 1
                newTour(name)
                continue
            elif newf == "NEW":
                name = input("Please type new name ")
                fname = name + ".txt"
            elif newf == "USE":
                #read_in_file(fname)
                check = 1
            else:
                newf = input("This is not valid. Please try again. ")
        else:
            print("New tournament will be created")
            check = 1
            newTour(name)

def read_in_file(fname):
    #------------
    # Read in file
    #-------------
    
    f = open(fname, "r")
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
        print("something is wrong with ", finIn)
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
    print(catPar)
    return catPar

main()
