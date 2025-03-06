#!/usr/bin/env python3
"""
Script to process student grades and generate personalized study plans using AI.
"""

import csv
import os
import json
import time
from typing import Dict, Any, List
from ai_integration import AIIntegration
import config

def read_grades_csv(csv_file: str) -> Dict[str, Dict[str, Any]]:
    """
    Read student grades from a CSV file.
    
    Args:
        csv_file: Path to the CSV file containing student grades
        
    Returns:
        Dictionary mapping student IDs to their data
    """
    students = {}
    
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            student_id = row['User ID']
            
            # Initialize student data
            students[student_id] = {
                'user_id': student_id,
                'username': row['Username'],
                'fullname': row['Full Name'],
                'grades': {}
            }
            
            # Add all grade items
            for key, value in row.items():
                if key not in ['User ID', 'Username', 'Full Name']:
                    # Clean up HTML tags if present
                    if "<" in value:
                        # Extract just the numeric part if possible
                        parts = value.split('>')
                        if len(parts) > 1:
                            value = parts[-1].strip()
                    
                    students[student_id]['grades'][key] = value
    
    return students

def save_study_plan(student_id: str, student_name: str, study_plan: str, output_dir: str = "study_plans"):
    """
    Save a study plan to a file.
    
    Args:
        student_id: ID of the student
        student_name: Name of the student
        study_plan: The generated study plan
        output_dir: Directory to save the study plans
    """
    # Check if running in Lambda environment
    is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    # If running in Lambda, use /tmp directory
    if is_lambda:
        output_dir = os.path.join('/tmp', output_dir)
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a filename based on student ID and name
    safe_name = student_name.replace(" ", "_").lower()
    filename = f"{output_dir}/{student_id}_{safe_name}_study_plan.txt"
    
    # Save the study plan
    with open(filename, 'w') as file:
        file.write(study_plan)
    
    print(f"Study plan saved to {filename}")
    return filename  # Return the filename for easier access

def process_student_grades(student_grades_data=None, grades_file=None, output_dir="study_plans"):
    """
    Process student grades and generate personalized study plans.
    
    Args:
        student_grades_data: Dictionary of student grades (direct in-memory data)
        grades_file: Path to the CSV file containing student grades (alternative)
        output_dir: Directory to save the study plans
        
    Returns:
        Dictionary mapping student IDs to their study plan file paths
    """
    # Get student grades either from direct data or from CSV file
    if student_grades_data:
        students = student_grades_data
        print(f"Using provided student grades data for {len(students)} students")
    elif grades_file:
        students = read_grades_csv(grades_file)
        print(f"Read grades for {len(students)} students from {grades_file}")
    else:
        print("Error: No student grades data or file provided")
        return {}
    
    # Create AI integration using environment variables
    ai = AIIntegration()
    
    # Generate and save study plans for each student
    for i, (student_id, student_data) in enumerate(students.items()):
        print(f"Generating study plan for {student_data['fullname']} ({i+1}/{len(students)})...")
        
        try:
            # Generate study plan
            study_plan = ai.generate_study_plan(student_data)
            
            # Save the study plan
            save_study_plan(student_id, student_data['fullname'], study_plan, output_dir)
            
            # Add a delay between API calls to avoid overwhelming the API
            # Only add delay if not the last student
            if i < len(students) - 1:
                delay = 2  # 2 seconds delay between API calls
                print(f"Waiting {delay} seconds before next API call...")
                time.sleep(delay)
            
        except Exception as e:
            print(f"Error generating study plan for {student_data['fullname']}: {e}")
            # Continue with the next student even if one fails
            continue

# Example usage
if __name__ == "__main__":
    # Path to the grades CSV file
    grades_file = "student_grades_20250305_134040.csv"  # Update with your actual file
    
    # Process student grades and generate study plans
    process_student_grades(grades_file=grades_file)
