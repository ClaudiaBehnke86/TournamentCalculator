import os, sys
import math
import time
from checkInp import *

class newTour:
    def __init__(self ,name):
        self.name = name
    def createNew(self):
        f= open(self.name + ".txt","w")
        
        print("How many tatmis will be there: ")
        tatami = checkNum()
        print("")
        print("Will there be a final block")
        final =checkYesNo()

        print("Tournament:",self.name , "will be created with ",tatami, " tatamis")

        f.write("Tournament: " + self.name + "\n")
        f.write("Tatamis: " + str(tatami) + "\n")
        #f.write("Tournament: {0} will be created with {1} tatamis".format(name), .format{tatami})
        
        if final == True:
            print("Tournament has a final block")
            f.write("Finalblock: YES \n" )
        elif final == False:
            print("Tournament has NO final block")
            f.write("Finallblock: NO \n")
        else:
            print("You should never see this. Something is VERY wrong here!!!")

        time.sleep(2)

        print("------------------------")
        print ("--- Age catergories ---")
        print("------------------------")
        print("Which age catergories will compete?")
        ageIn = ["U16","U18","U21","Adults"]
        print("Possible catergories", ageIn)
        print()
        print("Type: \"ALL\" to add all categories")

        i = 0
        ageSel = []
        while i < len(ageIn):
            addCat = input("Please type in name of category or type \"OK\" to continue to next step ")
            if addCat == "ALL":
                ageSel =ageIn.copy()
                print("All categories are added")
                break
            elif addCat in ageIn:
                ageSel.append(addCat)
                print(addCat, "added")
                i+=1
            elif addCat == "OK":
                if i == 0:
                    print("You must add minimum ONE Age category")
                else:
                    break
            else:
                print("Categorie ", addCat , "not known. Please try again")
        print("")
        print("The following age categories are added")
        print(ageSel)

        time.sleep(2)

        print("")
        print("------------------------")
        print ("--- Disciplines -------")
        print("------------------------")
        print ("Which disciplines will compete?")
        disIn = ["Fighting","Duo","Show","Ne-Waza"]
        print("Possible categories:" , disIn)
        print()
        print("Type: ""ALL"" to add all categories")

        i = 0
        disSel = []
        while i < len(disIn):
            addCat = input("Please type in name of diszipline or type \"OK\" to continue to next step ")
            if addCat == "ALL":
                disSel =disIn.copy()
                print("All disziplines are added")
                break
            elif addCat in disIn:
                disSel.append(addCat)
                print(addCat, "added")
                i+=1
            elif addCat == "OK":
                if i == 0:
                    print("You must add minimum ONE discipline")
                else:
                    break
            else:
                print("Diszipline ", addCat , "not known. Please try again")
        print("")
        print("The following disciplines are added:", disSel)
        #print(disSel)
        time.sleep(2)

        print("------------------------")
        print("calcualtion of weight categories")

        weightW = [45,48,52,57,63,70,71]
        weightW18 = [40,44,48,52,57,63,70,71]
        weightW16 = [32,36,40,44,48,52,57,63,61]

        weightM = [56,62,69,77,85,94,95]
        weightM18 = [46,50,55,60,66,73,81,82]
        weightM16 = [38,42,46,50,55,60,66,73,74]

        catTeam = {"Women","Men","Mixed"}


        catAll = []
        for i in ageSel: #Looping AgeCategories
            for j in disSel: #Looping Disziplines
                if(j == "Duo" or j == "Show"):
                    for k in catTeam:
                        catAll.append(i +" "+ j + " " + k)
                elif(i == "U16"):
                     for k in weightM16:
                         catAll.append(i +" "+ j + " Men "+ str(k)+"kg")
                     for k in weightW16:
                         catAll.append(i +" "+ j + " Women "+ str(k)+"kg")
                elif(i == "U18"):
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
        print("In total" , len(catAll) , "catergories have been created for Tournament",self.name)
        print()
        time.sleep(2)

        print("----------------------------")
        print("- Part 2 - Add Competitors -")
        print("----------------------------")
        catPar = {} #number of particpants
       
        print("Please add the number of participants for each category: ")
        for i in catAll:
            fightnum = 0
            print("Number of competitors in", i)
            inp = checkNum()
            if inp <= 0:
                continue
            catPar[i] = int(inp)

        time.sleep(1)
       
        for x,y in catPar.items():
            f.write(str(x) +" "+ str(y) + "\n")
        
        f.close()
