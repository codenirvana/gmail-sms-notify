#!/usr/bin/python
import httplib2
import json
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from twilio.rest import TwilioRestClient

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail-SMS'

def GetCredentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)

    return credentials

def ListMessages(service):
    response = service.users().messages().list(userId="me", labelIds=["INBOX", "UNREAD"]).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    messages = [message['id'] for message in messages]
    return messages

def GetMessage(service, msg_id):
    message = service.users().messages().get(userId="me", id=msg_id, format='metadata',metadataHeaders='Subject').execute()
    return message

def WorkingDirectory():
    cwd = os.getcwd()
    if 'gmail-sms-notify' in cwd:
        cwd = ''
    else:
        cwd = os.path.expanduser('~') + '/gmail-sms-notify/'

    return cwd

def GetLogs():
    lines = open( WorkingDirectory() + 'logs','r' )
    logs = [line.rstrip('\n') for line in lines]
    lines.close()
    return logs

def UpdateLogs(messages):
    logs = open( WorkingDirectory() + 'logs','w' )
    logs.write('\n'.join(messages))
    logs.close()

def GetTwilio():
    f = open( WorkingDirectory() + 'twilio.json', 'r' )
    twilio = json.load(f)
    f.close()
    return twilio

def SendSMS(msgSubject):
    twilio = GetTwilio()

    client = TwilioRestClient( twilio['sid'], twilio['auth_token'] )

    message = client.messages.create(
        to = twilio["number_to"],
        from_ = twilio["number_from"],
        body = msgSubject
    )

def main():
    credentials = GetCredentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    msgList = ListMessages(service)
    prevMessages = GetLogs()

    for msg in msgList:
        if msg not in prevMessages:
            msg = GetMessage(service, msg)
            msgSubject = msg['payload']['headers'][0]['value']
            SendSMS(msgSubject)

    UpdateLogs(msgList)

if __name__ == '__main__':
    main()
