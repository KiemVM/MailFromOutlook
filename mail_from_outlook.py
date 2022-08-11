from time import sleep
from tokenize import Token
import telebot
import telegram
import win32com.client
#other libraries to be used in this script
import os
from datetime import datetime, timedelta
import requests

mail_old = []
TOKEN = None
CHAT_ID = None
url = "https://api.telegram.org/bot"

def alert_tele(text):
    params = {'chat_id':CHAT_ID, 'text': text}
    req = requests.post(url + TOKEN + '/sendMessage', data=params)
    res = req.json()

    return res['ok']

def get_token():
    global TOKEN
    try:
        with open("config/token", 'r') as f:
            id = f.readline()
            id = id.replace("\n", "")
            TOKEN = id
    except Exception as ex:
        pass

def get_chat_id():
    global CHAT_ID
    try:
        with open("config/chatid", 'r') as f:
            id = f.readline()
            id = id.replace("\n", "")
            CHAT_ID = id
    except Exception as ex:
        pass

def get_mail_old():
    global mail_old
    try:
        with open("config/mail_old_id", 'r') as f:
            while 1:
                id = f.readline()
                if len(id) <= 0:
                    break
                id = id.replace("\n", "")
                mail_old.append(id)
    except Exception as ex:
        pass

def add_mail(id):
    try: 
        with open("config/mail_old_id", 'a') as f:
            f.write(id + "\n")
    except Exception as ex:
        pass

get_chat_id()
get_token()
get_mail_old()
while 1:
    outlook = win32com.client.Dispatch('outlook.application')
    mapi = outlook.GetNamespace("MAPI")

    for account in mapi.Accounts:
        print(account.DeliveryStore.DisplayName)

    inbox = mapi.GetDefaultFolder(6)
    #inbox = mapi.GetDefaultFolder(6).Folders["your_sub_folder"]

    messages = inbox.Items

    received_dt = datetime.now() - timedelta(days=2)
    received_dt = received_dt.strftime('%m/%d/%Y %H:%M %p')
    messages = messages.Restrict("[ReceivedTime] >= '" + received_dt + "'")
    #messages = messages.Restrict("[SenderEmailAddress] = 'jira-noreply@vnpt.vn'")
    for a in messages:
        convID = a.ConversationID
        if convID in mail_old:
            continue
        else:
            alert_tele("sender: " + a.SenderName + "\n" + "Subject: " + a.Subject + "\nBody: " + a.Body)
            mail_old.append(convID)
            add_mail(convID)

    sleep(60)