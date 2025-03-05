import requests
import json
import os
from typing import Dict, List, Any, Optional

class MoodleAPI:
    def __init__(self, base_url: str, token: str):
        """
        Initialize the Moodle API client.
        
        Args:
            base_url: The base URL of your Moodle site (e.g., 'https://moodle.example.com')
            token: Your Moodle API token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.web_service_url = f"{self.base_url}/webservice/rest/server.php"
    
    def call_api(self, function: str, params: Dict[str, Any] = None) -> Dict:
        """
        Make a call to the Moodle API.
        
        Args:
            function: The Moodle API function to call
            params: Additional parameters for the API call
            
        Returns:
            The JSON response from the API
        """
        if params is None:
            params = {}
            
        params.update({
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        })
        
        response = requests.get(self.web_service_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
        
        result = response.json()
        
        # Check if the response contains an error
        if isinstance(result, dict) and 'exception' in result:
            raise Exception(f"Moodle API error: {result.get('message', 'Unknown error')}")
            
        return result
    
    def get_courses(self) -> List[Dict]:
        """
        Get a list of courses the user has access to.
        
        Returns:
            A list of course objects
        """
        return self.call_api('core_course_get_courses')
    
    def get_course_by_id(self, course_id: int) -> Dict:
        """
        Get details for a specific course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            Course details
        """
        courses = self.call_api('core_course_get_courses', {'options[ids][]': course_id})
        if not courses:
            raise Exception(f"Course with ID {course_id} not found")
        return courses[0]
    
    def get_course_modules(self, course_id: int) -> List[Dict]:
        """
        Get all modules in a course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            A list of course modules
        """
        return self.call_api('core_course_get_contents', {'courseid': course_id})
    
    def get_users_in_course(self, course_id: int) -> List[Dict]:
        """
        Get all users enrolled in a course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            A list of user objects
        """
        return self.call_api('core_enrol_get_enrolled_users', {'courseid': course_id})
    
    def get_user_grades(self, course_id: int, user_id: Optional[int] = None) -> Dict:
        """
        Get grades for users in a course.
        
        Args:
            course_id: The ID of the course
            user_id: Optional user ID to get grades for a specific user
            
        Returns:
            Grade information for the specified course and user(s)
        """
        params = {'courseid': course_id}
        if user_id:
            params['userid'] = user_id
            
        return self.call_api('gradereport_user_get_grade_items', params)
    
    def get_grade_items(self, course_id: int) -> List[Dict]:
        """
        Get all grade items in a course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            A list of grade items
        """
        return self.call_api('core_grades_get_gradeitems', {'courseid': course_id})
    
    def get_module_grades(self, course_id: int, module_id: int, module_type: str) -> Dict:
        """
        Get grades for a specific module.
        
        This is a wrapper around the grade_get_grades function mentioned in your example.
        
        Args:
            course_id: The ID of the course
            module_id: The ID of the module instance
            module_type: The type of module (e.g., 'assign', 'quiz')
            
        Returns:
            Grade information for the specified module
        """
        # Note: This is a custom implementation as the direct grade_get_grades function
        # might not be directly accessible via the web service API
        # You may need to adjust this based on your Moodle version and configuration
        
        params = {
            'courseid': course_id,
            'component': f'mod_{module_type}',
            'cmid': module_id
        }
        
        return self.call_api('gradereport_user_get_grade_items', params)
    
    def process_student_grades(self, course_id: int, module_id: int = None, module_type: str = None) -> Dict[str, Any]:
        """
        Process and format student grades for a course or specific module.
        
        Args:
            course_id: The ID of the course
            module_id: Optional ID of the module instance
            module_type: Optional type of module (required if module_id is provided)
            
        Returns:
            A dictionary mapping student IDs to their grade information
        """
        # Get all users in the course
        users = self.get_users_in_course(course_id)
        
        # Get grades for all users
        if module_id and module_type:
            grades_data = self.get_module_grades(course_id, module_id, module_type)
        else:
            grades_data = self.get_user_grades(course_id)
        
        # Process the grades data
        # The exact structure will depend on your Moodle version and configuration
        # You may need to adjust this based on the actual response format
        
        student_grades = {}
        
        # Example processing - adjust based on actual response structure
        if 'usergrades' in grades_data:
            for user_grade in grades_data['usergrades']:
                user_id = user_grade.get('userid')
                if user_id:
                    student_grades[user_id] = {
                        'user_id': user_id,
                        'username': user_grade.get('username', ''),
                        'fullname': user_grade.get('fullname', ''),
                        'grades': []
                    }
                    
                    for grade_item in user_grade.get('gradeitems', []):
                        if module_id is None or (grade_item.get('cmid') == module_id):
                            student_grades[user_id]['grades'].append({
                                'item_name': grade_item.get('itemname', ''),
                                'grade': grade_item.get('gradeformatted', ''),
                                'percentage': grade_item.get('percentageformatted', ''),
                                'feedback': grade_item.get('feedback', '')
                            })
        
        return student_grades


# Example usage
if __name__ == "__main__":
    # Replace with your actual Moodle site URL and token
    MOODLE_URL = "https://blackbeltprep.com/moodle"
    MOODLE_TOKEN = "19e2e83b7624d96704ec3030ab6ea73b"
    
    # Create the Moodle API client
    moodle = MoodleAPI(MOODLE_URL, MOODLE_TOKEN)
    
    # Example: Get all courses
    try:
        courses = moodle.get_courses()
        print(f"Found {len(courses)} courses")
        
        if courses:
            # Get the first course
            course_id = courses[0]['id']
            print(f"Getting details for course ID {course_id}")
            
            # Get users in the course
            users = moodle.get_users_in_course(course_id)
            print(f"Found {len(users)} users in the course")
            
            # Get grades for all users in the course
            grades = moodle.get_user_grades(course_id)
            print("Retrieved grades for the course")
            
            # Process and display student grades
            student_grades = moodle.process_student_grades(course_id)
            print(f"Processed grades for {len(student_grades)} students")
            
            # Print the first student's grades as an example
            if student_grades:
                first_student_id = list(student_grades.keys())[0]
                student = student_grades[first_student_id]
                print(f"\nGrades for {student['fullname']}:")
                for grade in student['grades']:
                    print(f"  {grade['item_name']}: {grade['grade']} ({grade['percentage']})")
    
    except Exception as e:
        print(f"Error: {e}") 