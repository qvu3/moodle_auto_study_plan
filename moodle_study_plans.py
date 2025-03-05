#!/usr/bin/env python3
"""
Script to retrieve student grades from Moodle, generate personalized study plans,
and send them to students via email.
"""

from moodle_grades import get_moodle_student_grades, save_grades_to_csv
from grades_process import process_student_grades
from moodle_students import get_student_info, match_study_plans_to_students, send_all_study_plans
import email_config
import os
from datetime import datetime

def main():
    """
    Main function to retrieve grades, generate study plans, and send them to students.
    """
    print("Starting Moodle grades retrieval and study plan generation...")
    
    # Get student grades from Moodle
    print("Retrieving student grades from Moodle...")
    student_grades = get_moodle_student_grades()
    
    if not student_grades:
        print("Failed to retrieve student grades from Moodle.")
        return
    
    print(f"Successfully retrieved grades for {len(student_grades)} students.")
    
    # Save grades to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    grades_file = save_grades_to_csv(student_grades, f"student_grades_{timestamp}.csv")
    print(f"Grades saved to {grades_file}")
    
    # Process grades and generate study plans
    print("Generating personalized study plans...")
    output_dir = f"study_plans_{timestamp}"
    process_student_grades(grades_file, output_dir)
    print(f"Study plans generated and saved to {output_dir}/")
    
    # Get student information including email addresses
    print("Retrieving student information from Moodle...")
    students = get_student_info()
    
    if not students:
        print("Failed to retrieve student information from Moodle.")
        print("Study plans were generated but could not be sent to students.")
        return
    
    print(f"Retrieved information for {len(students)} students.")
    
    # Match study plans to students
    print("Matching study plans to students...")
    matched_plans = match_study_plans_to_students(output_dir, students)
    print(f"Matched {len(matched_plans)} study plans to students.")
    
    # Send study plans to students
    if matched_plans:
        print("Sending study plans to students...")
        results = send_all_study_plans(
            students,
            matched_plans,
            email_config.SMTP_SERVER,
            email_config.SMTP_PORT,
            email_config.SENDER_EMAIL,
            email_config.SENDER_PASSWORD
        )
        
        # Print results
        success_count = sum(1 for success in results.values() if success)
        print(f"Sent {success_count} out of {len(matched_plans)} study plans successfully.")
    else:
        print("No study plans matched to students. No emails were sent.")
    
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
