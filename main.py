import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail-SMS'

def get_credentials():
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

    return messages

def GetMessage(service, msg_id):
    message = service.users().messages().get(userId="me", id=msg_id, format='metadata',metadataHeaders='Subject').execute()
    return message

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    for id in ListMessages(service):
        msg = GetMessage(service, id['id'])
        print(msg['payload']['headers'][0]['value'])

if __name__ == '__main__':
    main()
