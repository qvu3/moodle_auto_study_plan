Author: Vu Quang Hoai Son
Creation Date: Mar 4 2025
Last Modified Date: Mar 5 2025

------------------------------------------------------------------------------------

*PURPOSE:
This project is to automate the following process:
1. Retrieve student grades from Moodle using the Moodle API
2. Send the Moodle grades to AI API such as Anthropic API or Open API to have them generate a personal study plan for each of the Students
3. Get the response from the AI API
4. Send the response to each student using their email addresses

*HOW TO RUN THIS PROJECT:
1. Install Required Dependencies
First, make sure you have all the necessary packages installed:
pip3 install -r requirements.txt

2. Set Up Moodle API Access
To access your Moodle site's API, you need to:
- Log in to your Moodle site as an administrator
- Go to Site administration > Plugins > Web services > Overview
- Follow the steps to enable web services and create a token:
  a. Enable web services
  b. Enable REST protocol
  c. Create a specific user for web service access
  d. Create a new role with appropriate permissions
  e. Create a new service with the functions you need (at minimum: core_course_get_courses, core_enrol_get_enrolled_users, gradereport_user_get_grade_items)
  f. Add the user to the service
  g. Create a token for the user
- Copy the generated token to the moodle_config.py file
- Update the MOODLE_URL and COURSE_ID in moodle_config.py

3. Place the Credentials File
Place the downloaded credentials.json file in the same directory as your Python script.

4. Run Your Script
Now you can run your script using Python:
python3 moodle_study_plans.py

*MOODLE API FUNCTIONS USED:
- core_course_get_courses: Get a list of courses
- core_enrol_get_enrolled_users: Get users enrolled in a course
- gradereport_user_get_grade_items: Get grade items for users in a course
- core_grades_get_gradeitems: Get all grade items in a course

*FILES IN THIS PROJECT:
- studyplan_automate.py: Main script that orchestrates the entire process
- moodle_api.py: Module for interacting with the Moodle API
- moodle_config.py: Configuration file for Moodle API credentials and settings
- requirements.txt: List of Python dependencies
- credentials.json: Google API credentials file
- token.pickle: Stored Google API tokens (generated on first run)

