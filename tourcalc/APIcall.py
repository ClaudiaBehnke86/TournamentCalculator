'''
In this module we make an API call to sportdata rest API to get athletes from an event
'''
import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd 
from pandas import json_normalize

key_map = {"4333":"U16 Duo Women",
	"4332":"U16 Duo Men",
	"4334":"U16 Duo Mixed",
	"4296":"U16 Fighting Men -38 kg",
	"4297":"U16 Fighting Men -42 kg",
	"4298":"U16 Fighting Men -46 kg",
	"4299":"U16 Fighting Men -50 kg",
	"4300":"U16 Fighting Men -55 kg",
	"4301":"U16 Fighting Men -60 kg",
	"4302":"U16 Fighting Men -66 kg",
	"4303":"U16 Fighting Men -73 kg",
	"4304":"U16 Fighting Men +73 kg",
	"4336":"U16 Show Women",
	"4335":"U16 Show Men",
	"4337":"U16 Show Mixed",
	"1816":"U18 Jiu-Jitsu Women -40 kg",
	"1817":"U18 Jiu-Jitsu Women -44 kg",
	"1818":"U18 Jiu-Jitsu Women -48 kg",
	"1819":"U18 Jiu-Jitsu Women -52 kg",
	"1820":"U18 Jiu-Jitsu Women -57 kg",
	"1821":"U18 Jiu-Jitsu Women -63 kg",
	"1822":"U18 Jiu-Jitsu Women -70 kg",
	"1815":"U18 Jiu-Jitsu Women +70 kg",
	"1823":"U18 Jiu-Jitsu Men -46 kg",
	"1824":"U18 Jiu-Jitsu Men -50 kg",
	"1825":"U18 Jiu-Jitsu Men -55 kg",
	"1826":"U18 Jiu-Jitsu Men -60 kg",
	"1827":"U18 Jiu-Jitsu Men -66 kg",
	"1828":"U18 Jiu-Jitsu Men -73 kg",
	"1829":"U18 Jiu-Jitsu Men -81 kg",
	"1830":"U18 Jiu-Jitsu Men +81 kg",
	"1889":"U18 Duo Men",
	"1890":"U18 Duo Mixed",
	"1891":"U18 Duo Women",
	"1806":"U18 Fighting Women -40 kg",
	"1807":"U18 Fighting Women -44 kg",
	"1808":"U18 Fighting Women -48 kg",
	"1809":"U18 Fighting Women -52 kg",
	"1810":"U18 Fighting Women -57 kg",
	"1811":"U18 Fighting Women -63 kg",
	"1812":"U18 Fighting Women -70 kg",
	"1814":"U18 Fighting Women +70 kg",
	"1760":"U18 Fighting Men -46 kg",
	"1761":"U18 Fighting Men -50 kg",
	"1762":"U18 Fighting Men -55 kg",
	"1763":"U18 Fighting Men -60 kg",
	"1764":"U18 Fighting Men -66 kg",
	"1765":"U18 Fighting Men -73 kg",
	"1766":"U18 Fighting Men -81 kg",
	"1767":"U18 Fighting Men +81 kg",
	"1892":"U18 Show Men",
	"1893":"U18 Show Mixed",
	"1894":"U18 Show Women",
	"1466":"U21 Jiu-Jitsu Women -45 kg",
	"1467":"U21 Jiu-Jitsu Women -48 kg",
	"1468":"U21 Jiu-Jitsu Women -52 kg",
	"1469":"U21 Jiu-Jitsu Women -57 kg",
	"1470":"U21 Jiu-Jitsu Women -63 kg",
	"1471":"U21 Jiu-Jitsu Women -70 kg",
	"1472":"U21 Jiu-Jitsu Women +70 kg",
	"1459":"U21 Jiu-Jitsu Men -56 kg",
	"1460":"U21 Jiu-Jitsu Men -62 kg",
	"1461":"U21 Jiu-Jitsu Men -69 kg",
	"1462":"U21 Jiu-Jitsu Men -77 kg",
	"1463":"U21 Jiu-Jitsu Men -85 kg",
	"1464":"U21 Jiu-Jitsu Men -94 kg",
	"1465":"U21 Jiu-Jitsu Men +94 kg",
	"1488":"U21 Duo Men",
	"1487":"U21 Duo Mixed",
	"1489":"U21 Duo Women",
	"1436":"U21 Fighting Women -45 kg",
	"1437":"U21 Fighting Women -48 kg",
	"1438":"U21 Fighting Women -52 kg",
	"1439":"U21 Fighting Women -57 kg",
	"1441":"U21 Fighting Women -63 kg",
	"1442":"U21 Fighting Women -70 kg",
	"1443":"U21 Fighting Women +70 kg",
	"1429":"U21 Fighting Men -56 kg",
	"1430":"U21 Fighting Men -62 kg",
	"1431":"U21 Fighting Men -69 kg",
	"1432":"U21 Fighting Men -77 kg",
	"1433":"U21 Fighting Men -85 kg",
	"1434":"U21 Fighting Men -94 kg",
	"1435":"U21 Fighting Men +94 kg",
	"1497":"U21 Show Men",
	"1498":"U21 Show Mixed",
	"1496":"U21 Show Women",
	"1491":"Adults Duo Men",
	"1492":"Adults Duo Mixed",
	"1490":"Adults Duo Women",
	"1444":"Adults Fighting Men -56 kg",
	"1451":"Adults Fighting Men -62 kg",
	"1446":"Adults Fighting Men -69 kg",
	"1447":"Adults Fighting Men -77 kg",
	"1448":"Adults Fighting Men -85 kg",
	"1449":"Adults Fighting Men -94 kg",
	"1450":"Adults Fighting Men +94 kg",
	"1452":"Adults Fighting Women -45 kg",
	"1453":"Adults Fighting Women -48 kg",
	"1454":"Adults Fighting Women -52 kg",
	"1455":"Adults Fighting Women -57 kg",
	"1456":"Adults Fighting Women -63 kg",
	"1457":"Adults Fighting Women -70 kg",
	"1458":"Adults Fighting Women +70 kg",
	"1473":"Adults Jiu-Jitsu Men -56 kg",
	"1474":"Adults Jiu-Jitsu Men -62 kg",
	"1475":"Adults Jiu-Jitsu Men -69 kg",
	"1476":"Adults Jiu-Jitsu Men -77 kg",
	"1477":"Adults Jiu-Jitsu Men -85 kg",
	"1478":"Adults Jiu-Jitsu Men -94 kg",
	"1479":"Adults Jiu-Jitsu Men +94 kg",
	"1480":"Adults Jiu-Jitsu Women -45 kg",
	"1481":"Adults Jiu-Jitsu Women -48 kg",
	"1482":"Adults Jiu-Jitsu Women -52 kg",
	"1483":"Adults Jiu-Jitsu Women -57 kg",
	"1484":"Adults Jiu-Jitsu Women -63 kg",
	"1485":"Adults Jiu-Jitsu Women -70 kg",
	"1486":"Adults Jiu-Jitsu Women +70 kg",
	"1494":"Adults Show Men",
	"1495":"Adults Show Mixed",
	"1493":"Adults Show Women",
	"4323":"U16 Jiu-Jitsu Women -32 kg",
	"4324":"U16 Jiu-Jitsu Women -36 kg",
	"4325":"U16 Jiu-Jitsu Women -40 kg",
	"4326":"U16 Jiu-Jitsu Women -44 kg",
	"4327":"U16 Jiu-Jitsu Women -48 kg",
	"4328":"U16 Jiu-Jitsu Women -52 kg",
	"4329":"U16 Jiu-Jitsu Women -57 kg",
	"4330":"U16 Jiu-Jitsu Women -63 kg",
	"4331":"U16 Jiu-Jitsu Women +63 kg",
	"4314":"U16 Jiu-Jitsu Men -38 kg",
	"4315":"U16 Jiu-Jitsu Men -42 kg",
	"4316":"U16 Jiu-Jitsu Men -46 kg",
	"4317":"U16 Jiu-Jitsu Men -50 kg",
	"4318":"U16 Jiu-Jitsu Men -55 kg",
	"4319":"U16 Jiu-Jitsu Men -60 kg",
	"4320":"U16 Jiu-Jitsu Men -66 kg",
	"4321":"U16 Jiu-Jitsu Men -73 kg",
	"4322":"U16 Jiu-Jitsu Men +73 kg",
	"4305":"U16 Fighting Women -32 kg",
	"4306":"U16 Fighting Women -36 kg",
	"4307":"U16 Fighting Women -40 kg",
	"4308":"U16 Fighting Women -44 kg",
	"4309":"U16 Fighting Women -48 kg",
	"4310":"U16 Fighting Women -52 kg",
	"4311":"U16 Fighting Women -57 kg",
	"4312":"U16 Fighting Women -63 kg",
	"4313":"U16 Fighting Women +63 kg"}


def getdata(eventid, user, password):
	"""
	give they key and get the dict
	"""
	uri = 'https://www.sportdata.org/ju-jitsu/rest/event/categories/'+str(eventid)+'/'

	response = requests.get(uri, auth=HTTPBasicAuth(user,password))
	d = response.json()
	df_out = json_normalize(d['categories'])

	num_par = df_out[['id', 'number_of_participants']]
	newdict = num_par.set_index('id').to_dict()

	# number_of_participants
	num_par_dic = newdict['number_of_participants']
	num_par_dict_exp = {}

	for key, value in num_par_dic.items():
		if str(key) in key_map.keys():
			num_par_dict_exp[key_map[str(key)]] = value
		else: 
			print("no mapping found for key ", key)

	return num_par_dict_exp
