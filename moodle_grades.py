#!/usr/bin/env python3
"""
Module for retrieving and processing student grades from Moodle.
This module provides functions to interact with the Moodle API specifically for grade-related operations.
"""

import csv
from datetime import datetime
from typing import Dict, Any, Optional
from moodle_api import MoodleAPI
import config
import os

def get_moodle_student_grades(course_id: Optional[int] = None):
    """
    Retrieve student grades from Moodle using the Moodle API.
    
    Args:
        course_id: Optional course ID. If not provided, uses the one from environment variables.
        
    Returns:
        A dictionary mapping student IDs to their grade information
    """
    try:
        # Create the Moodle API client
        moodle = MoodleAPI()
        
        # Get the course ID from the config if not provided
        if course_id is None:
            course_id = config.MOODLE_COURSE_ID
        
        # Get all users in the course
        users = moodle.get_users_in_course(course_id)
        print(f"Found {len(users)} users in course {course_id}")
        
        # Get and process student grades
        student_grades = moodle.process_student_grades(course_id)
        print(f"Retrieved grades for {len(student_grades)} students")
        
        return student_grades
    
    except Exception as e:
        print(f"Error retrieving Moodle grades: {e}")
        return {}

def save_grades_to_csv(student_grades, filename=None):
    """
    Save student grades to a CSV file.
    
    Args:
        student_grades: Dictionary of student grades from Moodle API
        filename: Optional filename for the CSV file
        
    Returns:
        The path to the saved CSV file
    """
    # Check if running in Lambda environment
    is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    if filename is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"student_grades_{timestamp}.csv"
    
    # If running in Lambda, use /tmp directory
    if is_lambda:
        filename = os.path.join('/tmp', filename)
    
    with open(filename, 'w', newline='') as csvfile:
        # Determine all possible grade items
        all_grade_items = set()
        for student_id, student_data in student_grades.items():
            for grade in student_data['grades']:
                all_grade_items.add(grade['item_name'])
        
        # Create header row
        fieldnames = ['User ID', 'Username', 'Full Name'] + list(all_grade_items)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write student data
        for student_id, student_data in student_grades.items():
            row = {
                'User ID': student_data['user_id'],
                'Username': student_data['username'],
                'Full Name': student_data['fullname']
            }
            
            # Add grades to the row
            for grade in student_data['grades']:
                row[grade['item_name']] = grade['grade']
            
            writer.writerow(row)
    
    print(f"Saved student grades to {filename}")
    return filename

def get_module_grades(course_id: int, module_id: int, module_type: str):
    """
    Get grades for a specific module.
    
    Args:
        course_id: The ID of the course
        module_id: The ID of the module instance
        module_type: The type of module (e.g., 'assign', 'quiz')
        
    Returns:
        Grade information for the specified module
    """
    try:
        # Create the Moodle API client
        moodle = MoodleAPI()
        
        # Get module grades
        grades = moodle.get_module_grades(course_id, module_id, module_type)
        
        return grades
    
    except Exception as e:
        print(f"Error retrieving module grades: {e}")
        return {}

def combine_report_and_grades(report_file, grades_file):
    """
    Combine the weekly report and Moodle grades into a single dataset.
    This is a placeholder function - you'll need to implement the actual logic
    based on your report format and requirements.
    
    Args:
        report_file: Path to the weekly report file
        grades_file: Path to the grades CSV file
        
    Returns:
        Combined data for generating study plans
    """
    # This is a placeholder - implement based on your actual report format
    print(f"Combining data from {report_file} and {grades_file}")
    
    # Example implementation - you'll need to adjust this
    combined_data = {}
    
    # Read grades data
    with open(grades_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            student_id = row['User ID']
            combined_data[student_id] = {
                'user_id': student_id,
                'username': row['Username'],
                'fullname': row['Full Name'],
                'grades': {}
            }
            
            # Add all grade items
            for key, value in row.items():
                if key not in ['User ID', 'Username', 'Full Name']:
                    combined_data[student_id]['grades'][key] = value
    
    # TODO: Read and process the weekly report data
    # This will depend on the format of your report
    
    return combined_data

# Example usage
if __name__ == "__main__":
    # Get student grades from Moodle
    student_grades = get_moodle_student_grades()
    
    if student_grades:
        # Save grades to CSV
        grades_file = save_grades_to_csv(student_grades)
        print(f"Grades saved to {grades_file}")
        
        # Print the first student's grades as an example
        if student_grades:
            first_student_id = list(student_grades.keys())[0]
            student = student_grades[first_student_id]
            print(f"\nGrades for {student['fullname']}:")
            for grade in student['grades']:
                print(f"  {grade['item_name']}: {grade['grade']} ({grade['percentage']})")
    else:
        print("Failed to retrieve student grades from Moodle") 