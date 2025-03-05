#!/usr/bin/env python3
"""
Module for retrieving student information from Moodle and matching study plans to students.
"""

import os
import csv
from typing import Dict, Any, List, Optional
from moodle_api import MoodleAPI
import moodle_config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def get_student_info(course_id: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve student information from Moodle, including email addresses.
    
    Args:
        course_id: Optional course ID. If not provided, uses the one from moodle_config.
        
    Returns:
        A dictionary mapping student IDs to their information
    """
    try:
        # Create the Moodle API client
        moodle = MoodleAPI(moodle_config.MOODLE_URL, moodle_config.MOODLE_TOKEN)
        
        # Get the course ID from the config if not provided
        if course_id is None:
            course_id = moodle_config.COURSE_ID
        
        # Get all users in the course
        users = moodle.get_users_in_course(course_id)
        print(f"Found {len(users)} users in course {course_id}")
        
        # Process user information
        students = {}
        for user in users:
            # Skip users without an ID
            if 'id' not in user:
                continue
                
            user_id = str(user['id'])  # Convert to string to match CSV keys
            
            # Extract relevant information
            students[user_id] = {
                'id': user_id,
                'username': user.get('username', ''),
                'fullname': user.get('fullname', ''),
                'email': user.get('email', ''),
                'roles': [role.get('shortname', '') for role in user.get('roles', [])]
            }
        
        return students
    
    except Exception as e:
        print(f"Error retrieving student information: {e}")
        return {}

def match_study_plans_to_students(study_plans_dir: str, students: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Match study plans to students based on student IDs in filenames.
    
    Args:
        study_plans_dir: Directory containing study plan files
        students: Dictionary of student information
        
    Returns:
        Dictionary mapping student IDs to their study plan file paths
    """
    matched_plans = {}
    
    # Check if directory exists
    if not os.path.exists(study_plans_dir):
        print(f"Study plans directory {study_plans_dir} does not exist")
        return matched_plans
    
    # List all files in the directory
    for filename in os.listdir(study_plans_dir):
        # Skip non-text files
        if not filename.endswith('.txt'):
            continue
            
        # Extract student ID from filename (assuming format: student_id_name_study_plan.txt)
        parts = filename.split('_')
        if len(parts) < 2:
            continue
            
        student_id = parts[0]
        
        # Check if this student ID exists in our students dictionary
        if student_id in students:
            matched_plans[student_id] = os.path.join(study_plans_dir, filename)
    
    return matched_plans

def send_study_plan_email(student: Dict[str, Any], study_plan_path: str, 
                          smtp_server: str, smtp_port: int, 
                          sender_email: str, sender_password: str) -> bool:
    """
    Send a study plan to a student via email.
    
    Args:
        student: Dictionary containing student information
        study_plan_path: Path to the study plan file
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Sender's email address
        sender_password: Sender's email password
        
    Returns:
        True if the email was sent successfully, False otherwise
    """
    try:
        # Check if student has an email
        if not student.get('email'):
            print(f"No email address found for student {student.get('fullname', 'Unknown')}")
            return False
            
        # Read the study plan
        with open(study_plan_path, 'r') as file:
            study_plan_content = file.read()
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = student['email']
        msg['Subject'] = f"Your Personalized Study Plan - {student.get('fullname', 'Student')}"
        
        # Add HTML body
        html = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
              .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
              h1 {{ color: #2c3e50; }}
              h2 {{ color: #3498db; margin-top: 20px; }}
              .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #7f8c8d; }}
              pre {{ white-space: pre-wrap; background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
          </head>
          <body>
            <div class="container">
              <h1>Your Personalized Study Plan</h1>
              <p>Hello {student.get('fullname', 'Student')},</p>
              <p>Based on your recent performance, we've created a personalized study plan to help you improve and succeed in your studies.</p>
              
              <pre>{study_plan_content}</pre>
              
              <p>We hope this plan helps you achieve your goals. If you have any questions or need further assistance, please don't hesitate to reach out.</p>
              
              <p>Best regards,<br>Black Belt Test Prep Team</p>
              
              <div class="footer">
                <p>This is an automated email. Please do not reply directly to this message.</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Attach the study plan as a text file
        attachment = MIMEApplication(study_plan_content.encode('utf-8'))
        attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(study_plan_path)}"'
        msg.attach(attachment)
        
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Study plan sent to {student.get('fullname', 'Unknown')} ({student['email']})")
        return True
        
    except Exception as e:
        print(f"Error sending study plan to {student.get('fullname', 'Unknown')}: {e}")
        return False

def send_all_study_plans(students: Dict[str, Dict[str, Any]], 
                         matched_plans: Dict[str, str],
                         smtp_server: str, smtp_port: int,
                         sender_email: str, sender_password: str) -> Dict[str, bool]:
    """
    Send study plans to all matched students.
    
    Args:
        students: Dictionary of student information
        matched_plans: Dictionary mapping student IDs to study plan file paths
        smtp_server: SMTP server address
        smtp_port: SMTP server port
        sender_email: Sender's email address
        sender_password: Sender's email password
        
    Returns:
        Dictionary mapping student IDs to success status
    """
    results = {}
    
    for student_id, study_plan_path in matched_plans.items():
        if student_id in students:
            success = send_study_plan_email(
                students[student_id], 
                study_plan_path,
                smtp_server, 
                smtp_port,
                sender_email, 
                sender_password
            )
            results[student_id] = success
    
    return results

# Example usage
if __name__ == "__main__":
    # Get student information from Moodle
    students = get_student_info()
    
    if students:
        print(f"Retrieved information for {len(students)} students")
        
        # Example: Print student information
        for student_id, student in list(students.items())[:3]:  # Print first 3 students
            print(f"Student ID: {student_id}")
            print(f"  Name: {student.get('fullname', 'Unknown')}")
            print(f"  Email: {student.get('email', 'Unknown')}")
            print(f"  Roles: {', '.join(student.get('roles', []))}")
            print()
    else:
        print("Failed to retrieve student information from Moodle") 