import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from datetime import datetime
# Import the functions from the new moodle_grades module
from moodle_grades import get_moodle_student_grades, save_grades_to_csv, combine_report_and_grades

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

def get_student_weekly_report(service):
    """
    Find and download the latest Students Weekly Report from Gmail.
    
    Args:
        service: The Gmail API service
        
    Returns:
        The path to the saved report file, or None if not found
    """
    # Get messages from the inbox
    results = service.users().messages().list(userId='me', maxResults=30).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found')
        return None
    
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
        
        # Extract headers
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
            
            # Check if the email has an attachment
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']

                for part in parts:
                    if part.get('filename') and part.get('filename') != '':
                        # This part contains an attachment
                        attachment_id = part['body']['attachmentId']
                        filename = part['filename']

                        if attachment_id:
                            # Get the attachment
                            attachment = service.users().messages().attachments().get(
                                userId='me',
                                messageId=msg['id'],
                                id=attachment_id
                            ).execute()

                            # Decode the attachment date
                            file_data = base64.urlsafe_b64decode(attachment['data'])

                            # Save the attachment
                            with open(filename, 'wb') as f:
                                f.write(file_data)

                            print(f'Saved attachment: {filename}')
                            return filename
            
            print('-'*20)
            break
    
    return None

# Example usage
if __name__ == '__main__':
    # Authenticate with Gmail
    service = authenticate_gmail()
    
    # Get the latest weekly report
    report_file = get_student_weekly_report(service)
    
    if report_file:
        print(f"Successfully retrieved weekly report: {report_file}")
        
        # Get student grades from Moodle using the imported function
        student_grades = get_moodle_student_grades()
        
        if student_grades:
            # Save grades to CSV using the imported function
            grades_file = save_grades_to_csv(student_grades)
            
            # Combine report and grades data using the imported function
            # combined_data = combine_report_and_grades(report_file, grades_file)
            
            # TODO: Send the combined data to AI API for generating study plans
            # TODO: Send the study plans to students via email
            
            print("Process completed successfully")
        else:
            print("Failed to retrieve student grades from Moodle")
    else:
        print("Failed to retrieve weekly report from Gmail")
            
            