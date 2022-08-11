import imaplib
import email
from email.header import decode_header
from time import sleep
import requests

mail_old = []
TOKEN = None
CHAT_ID = None
url = "https://api.telegram.org/bot"

username = None
password = None
# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:
imap_server = "mail.vnpt.vn"

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

def clean(text):
     # clean text for creating a folder
     return "".join(c if c.isalnum() else "_" for c in text)

def get_account():
    global username
    global password
    try:
        with open("config/user", 'r') as f:
            id = f.readline()
            id = id.replace("\n", "")
            username = id
    except Exception as ex:
        pass

    try:
        with open("config/pass", 'r') as f:
            id = f.readline()
            id = id.replace("\n", "")
            password = id
    except Exception as ex:
        pass


get_chat_id()
get_token()
get_mail_old()
get_account()

while 1:
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 10
    # total number of emails
    messages = int(messages[0])

    for i in range(messages, messages-N, -1):
        body_data = ""
        subject = None
        From = None
        mess_id = None
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                mess_id , encoding = decode_header(msg["Message-ID"])[0]
                if isinstance(mess_id, bytes):
                    if encoding == None:
                        encoding = 'utf-8'
                    # if it's a bytes, decode to str
                    mess_id = mess_id.decode(encoding)
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    if encoding == None:
                        encoding = 'utf-8'
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    if encoding == None:
                        encoding = 'utf-8'
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            body_data += body
                        elif "attachment" in content_disposition:
                            # download attachment
                            body_data += "have attachment in email"
                            # filename = part.get_filename()
                            # if filename:
                            #     folder_name = clean(subject)
                            #     if not os.path.isdir(folder_name):
                            #         # make a folder for this email (named after the subject)
                            #         os.mkdir(folder_name)
                            #     filepath = os.path.join(folder_name, filename)
                            #     # download attachment and save it
                            #     open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        body_data += body
                if content_type == "text/html":
                    body_data += "have text/html in email"
                #     # if it's HTML, create a new HTML file and open it in browser
                #     folder_name = clean(subject)
                #     if not os.path.isdir(folder_name):
                #         # make a folder for this email (named after the subject)
                #         os.mkdir(folder_name)
                #     filename = "index.html"
                #     filepath = os.path.join(folder_name, filename)
                #     # write the file
                #     open(filepath, "w").write(body)
                #     # open in the default browser
                #     webbrowser.open(filepath)
                print("="*100)
            if  mess_id in mail_old:
                continue
            else:
                alert_tele("sender: " + From + "\n" + "Subject: " + subject + "\nBody: " + body_data)
                mail_old.append(mess_id)
                add_mail(mess_id)    
    # close the connection and logout
    imap.close()
    imap.logout()
    sleep(60)

