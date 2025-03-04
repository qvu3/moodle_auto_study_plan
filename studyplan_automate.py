import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def authenticate_gmail():
    credentials = None
    # Stores the user's access and refresh tokens in the token.pickle file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # Need to enable the Gmail API and download the credentials.json file
            # from the Google API Console
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                ['https://www.googleapis.com/auth/gmail.readonly']
            )
            credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=credentials)
    return service

# Example usage
if __name__ == '__main__':
    service = authenticate_gmail()
    
    # Get messages from the inbox
    results = service.users().messages().list(userId='me', maxResults=30).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found')
    else:
        print(f'Found {len(messages)} messages')
        for message in messages:
            # Get the full message details
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # Extract headers from the payload
            headers = msg['payload']['headers']

            # Find the subject and sender
            target_subject = "Students Weekly Report"
            target_sender = "info@blackbelttestprep.com"
            subject = ""
            sender = ""
            date = ""
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value']
                if header['name'] == 'Date':
                    date = header['value']
            
                if target_sender in sender and target_subject in subject:
                    print(f'From: {sender}')
                    print(f'Subject: {subject}')
                    print(f'Date: {date}')
                    print('-'*20)
                    break
                else:
                    pass
            
            