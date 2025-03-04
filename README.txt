Author: Vu Quang Hoai Son
Creation Date: Mar 4 2025
Last Modified Date: Mar 4 2025

------------------------------------------------------------------------------------

*PURPOSE:
This project is to automate the following process:
1. Log in to Gmail
2. Use Gmail API to find the latest Students Weekly Report email
3. Save the attachment (report)
4. Send the report data to AI API such as Anthropic API or Open API to have them generate a personal study plan for each of the Students
5. Get the response from the AI API
6. Send the response to each student using their email addresses

*HOW TO RUN THIS PROJECT:
1. Install Required Dependencies
First, make sure you have all the necessary packages installed:
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib

2. Set Up Google Cloud Project and Enable Gmail API
Before running your script, you need to set up a Google Cloud project and enable the Gmail API:
- Go to the Google Cloud Console
- Create a new project (or select an existing one)
- In the sidebar, navigate to "APIs & Services" > "Library"
- Search for "Gmail API" and enable it
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" and select "OAuth client ID"
- Configure the OAuth consent screen if prompted
- For application type, choose "Desktop app"
- Name your OAuth client and click "Create"
- Download the JSON file (this is your credentials.json)

3. Place the Credentials File
Place the downloaded credentials.json file in the same directory as your Python script.

4. Run Your Script
Now you can run your script using Python:
python3 your_script_name.py

When you run the script for the first time:
A browser window will open asking you to log in to your Google account
Grant the requested permissions to your application
After authorization, the browser will show a success message and you can close it
The script will create a token.pickle file that stores your credentials for future runs

