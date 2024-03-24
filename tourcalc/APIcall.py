'''
In this module we make an API call to sportdata rest API to get athletes from an event
'''
import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd 
from pandas import json_normalize


def read_in_catkey():
    ''' Read in file
     - HELPER FUNCTION
     Reads in a csv  and convert catergory ids to catergoy names

    '''
    inp_file = pd.read_csv('https://raw.githubusercontent.com/ClaudiaBehnke86/JJIFsupportFiles/main/catID_name.csv', sep=';')

    print(inp_file)
    key_map_inp = inp_file[
        ['cat_id', 'name']
    ].set_index('cat_id').to_dict()['name']

    return key_map_inp


key_map = read_in_catkey()


def getdata(eventid, user, password):
    """
    give they key and get the dict
    """

    uri = 'https://www.sportdata.org/ju-jitsu/rest/event/categories/'+str(eventid)+'/'

    response = requests.get(uri, auth=HTTPBasicAuth(user, password),)
    d = response.json()

    if 'categories' in d:
        df_out = json_normalize(d['categories'])

        num_par = df_out[['id', 'number_of_participants']]
        newdict = num_par.set_index('id').to_dict()
        # number_of_participants
        num_par_dic = newdict['number_of_participants']
        num_par_dict_exp = {}

        for key, value in num_par_dic.items():
            if key in key_map.keys():
                num_par_dict_exp[key_map[key]] = value
            else:
                if key in key_map:
                    print("no mapping found for key ", key, " ", key_map[key])
                else:
                    print(key, "is not in input file")

    else:
        print('no valid categories in event')
        num_par_dict_exp = {}

    return num_par_dict_exp
