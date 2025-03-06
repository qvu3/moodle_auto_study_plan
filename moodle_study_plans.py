#!/usr/bin/env python3
"""
Script to retrieve student grades from Moodle, generate personalized study plans,
and send them to students via email.
"""

from moodle_grades import get_moodle_student_grades, save_grades_to_csv
from grades_process import process_student_grades
from moodle_students import get_student_info, match_study_plans_to_students, send_all_study_plans
import config
import os
from datetime import datetime
import sys

def main():
    """
    Main function to retrieve grades, generate study plans, and send them to students.
    """
    print("Starting Moodle grades retrieval and study plan generation...")
    
    # Validate configuration
    missing_config = config.validate_config()
    if missing_config:
        print("Error: Missing or invalid configuration:")
        for key, message in missing_config.items():
            print(f"  - {key}: {message}")
        print("\nPlease check your .env file or environment variables.")
        return
    
    # Print configuration summary
    print(config.get_config_summary())
    
    # Get student grades from Moodle
    print("Retrieving student grades from Moodle...")
    student_grades = get_moodle_student_grades()
    
    if not student_grades:
        print("Failed to retrieve student grades from Moodle.")
        return
    
    print(f"Successfully retrieved grades for {len(student_grades)} students.")
    
    # Process grades and generate study plans
    print("Generating personalized study plans...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"study_plans_{timestamp}"
    
    # Check if running in Lambda environment
    is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or os.environ.get('BlackBelt_Studyplan_AI_Automation') is not None
    
    # Process grades and generate study plans
    if is_lambda:
        # Skip saving to CSV and pass student_grades directly
        full_output_dir = os.path.join('/tmp', output_dir)
        study_plans = process_student_grades(student_grades_data=student_grades, output_dir=output_dir)
    else:
        # For local development, still save to CSV for debugging/record keeping
        grades_file = save_grades_to_csv(student_grades, f"student_grades_{timestamp}.csv")
        print(f"Grades saved to {grades_file}")
        full_output_dir = output_dir
        study_plans = process_student_grades(grades_file=grades_file, output_dir=output_dir)
    
    print(f"Study plans generated and saved to {full_output_dir}/")
    
    # Ensure the directory exists before matching plans
    if is_lambda and not os.path.exists(full_output_dir):
        print(f"Creating output directory: {full_output_dir}")
        os.makedirs(full_output_dir, exist_ok=True)
    
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
    matched_plans = match_study_plans_to_students(full_output_dir, students)
    print(f"Matched {len(matched_plans)} study plans to students.")
    
    # Send study plans to students
    if matched_plans:
        print("Sending study plans to students...")
        results = send_all_study_plans(students, matched_plans)
        
        # Print results
        success_count = sum(1 for success in results.values() if success)
        print(f"Sent {success_count} out of {len(matched_plans)} study plans successfully.")
    else:
        print("No study plans matched to students. No emails were sent.")
    
    print("Process completed successfully.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
