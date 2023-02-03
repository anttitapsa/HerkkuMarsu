import csv
from os.path import exists
import pandas as pd
from datetime import datetime


def find_user(user_name):
    '''
    Check if user is found in credits.csv file.
    If user is not found, user is added into the file.

    If credits.csv is not found, file is created.
    '''
    if not exists("credits.csv"):
        f = open('credits.csv', 'w')
        writer = csv.writer(f)
        writer.writerow(["name","money","latest_change","latest_change_time"])
        f.close()
    df = pd.read_csv("credits.csv")
    if user_name in df["name"].values:
        return True
    else:
        return False

def add_user(user_name):
    '''
    Adds user into credits.csv file
    '''
    data = {"name": [user_name], "money": [0], "latest_change": ["add new user"], "latest_change_time": [datetime.now()]}
    df = pd.DataFrame(data)
    df.to_csv("credits.csv", mode='a', index=False, header=False)

def add_money(user_name, money):
    '''
    Adds money in money column of the user.

    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    current_money = float(df.loc[df['name']==user_name, "money"]) + float(money)
    df.loc[df["name"]==user_name, "money"] = round(current_money,2)
    df.loc[df["name"]==user_name, "latest_change"] = "add money"
    df.loc[df["name"]==user_name, "latest_change_time"] = datetime.now()
    df.to_csv("credits.csv", index=False)

    return round(current_money,2)

def use_money(user_name, money):
    '''
    Subtracts the money from the money column of the user.

    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    current_money = float(df.loc[df['name']==user_name, "money"]) - float(money)

    if current_money >= 0:
        df.loc[df["name"]==user_name, "money"] = round(current_money, 2)
        df.loc[df["name"]==user_name, "latest_change"] = "use money"
        df.loc[df["name"]==user_name, "latest_change_time"] = datetime.now()
        df.to_csv("credits.csv", index=False)

        return round(current_money,2)
    
    else:
        return round(current_money, 2)

def check_money(user_name):
    '''
    Returns the current amount of the money in user's money column 
    '''
    df = pd.read_csv("credits.csv")
    return float(df.loc[df['name']==user_name, "money"])