#!/usr/bin/env python3
"""
Test script for Moodle API integration.
This script tests the connection to the Moodle API and retrieves basic information.
"""

import sys
from moodle_api import MoodleAPI
import config
from moodle_grades import get_moodle_student_grades, save_grades_to_csv

def test_moodle_connection():
    """Test the connection to the Moodle API."""
    print("Testing Moodle API connection...")
    
    try:
        # Create the Moodle API client
        moodle = MoodleAPI(config.MOODLE_URL, config.MOODLE_TOKEN)
        
        # Test getting courses
        print("\nTesting get_courses()...")
        courses = moodle.get_courses()
        print(f"Found {len(courses)} courses")
        
        if courses:
            # Print the first few courses
            print("\nFirst few courses:")
            for i, course in enumerate(courses[:3]):
                print(f"  {i+1}. {course.get('fullname', 'Unknown')} (ID: {course.get('id', 'Unknown')})")
        
        # Test getting course by ID
        course_id = config.MOODLE_COURSE_ID
        print(f"\nTesting get_course_by_id({course_id})...")
        try:
            course = moodle.get_course_by_id(course_id)
            print(f"Course name: {course.get('fullname', 'Unknown')}")
        except Exception as e:
            print(f"Error getting course: {e}")
        
        # Test getting users in course
        print(f"\nTesting get_users_in_course({course_id})...")
        try:
            users = moodle.get_users_in_course(course_id)
            print(f"Found {len(users)} users in the course")
            
            if users:
                # Print the first few users
                print("\nFirst few users:")
                for i, user in enumerate(users[:3]):
                    print(f"  {i+1}. {user.get('fullname', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
        except Exception as e:
            print(f"Error getting users: {e}")
        
        # Test getting grades using the new module
        print(f"\nTesting get_moodle_student_grades()...")
        try:
            student_grades = get_moodle_student_grades(course_id)
            print(f"Retrieved grades for {len(student_grades)} students")
            
            if student_grades:
                # Save grades to CSV
                grades_file = save_grades_to_csv(student_grades)
                print(f"Saved grades to {grades_file}")
                
                # Print the first student's grades as an example
                first_student_id = list(student_grades.keys())[0]
                student = student_grades[first_student_id]
                print(f"\nGrades for {student['fullname']}:")
                for grade in student['grades']:
                    print(f"  {grade['item_name']}: {grade['grade']} ({grade['percentage']})")
        except Exception as e:
            print(f"Error getting grades: {e}")
        
        print("\nMoodle API test completed successfully!")
        return True
    
    except Exception as e:
        print(f"\nError testing Moodle API: {e}")
        return False

if __name__ == "__main__":
    success = test_moodle_connection()
    sys.exit(0 if success else 1) 