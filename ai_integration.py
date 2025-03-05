#!/usr/bin/env python3
"""
Module for integrating with AI APIs to generate personalized study plans based on student grades.
"""

import requests
from typing import Dict, Any
import time
import random

class AIIntegration:
    def __init__(self, api_key: str, api_type: str = "anthropic", max_retries: int = 5):
        """
        Initialize the AI integration.
        
        Args:
            api_key: The API key for the AI service
            api_type: The type of AI API to use ("anthropic" or "openai")
            max_retries: Maximum number of retry attempts for API calls
        """
        self.api_key = api_key
        self.api_type = api_type.lower()
        self.max_retries = max_retries
        
        if self.api_type == "anthropic":
            self.api_url = "https://api.anthropic.com/v1/messages"
        elif self.api_type == "openai":
            self.api_url = "https://api.openai.com/v1/chat/completions"
        else:
            raise ValueError(f"Unsupported API type: {api_type}")
    
    def format_student_grades(self, student_data: Dict[str, Any]) -> str:
        """
        Format student grades for the AI prompt.
        
        Args:
            student_data: Dictionary containing student information and grades
            
        Returns:
            Formatted string of grades for the AI prompt
        """
        formatted_data = f"Student: {student_data.get('fullname', 'Unknown')}\n\n"
        formatted_data += "Grades:\n"
        
        # Add grades information
        if 'grades' in student_data:
            for subject, grade in student_data['grades'].items():
                # Skip empty grades or grades with HTML
                if grade != "- (-)" and grade != "" and "<" not in grade:
                    formatted_data += f"- {subject}: {grade}\n"
        
        return formatted_data
    
    def generate_prompt(self, student_data: Dict[str, Any]) -> str:
        """
        Generate a prompt for the AI based on student grades.
        
        Args:
            student_data: Dictionary containing student information and grades
            
        Returns:
            Complete prompt for the AI
        """
        formatted_data = self.format_student_grades(student_data)
        
        prompt = f"""
        You are an expert educational advisor specializing in personalized study plans. 
        Based on the following student grades, create a detailed, personalized study plan for the next week.
        
        {formatted_data}
        
        The study plan should:
        1. Identify weak areas that need improvement based on the grades
        2. Suggest specific topics to focus on
        3. Recommend study techniques and resources (prioritize resources from Black Belt Test Prep such as quizzes, flashcards, and practice tests)
        4. Provide a daily schedule for the week
        5. Include motivational elements and encouragement
        
        Format the study plan in a clear, organized manner with headings and bullet points.
        """
        
        return prompt
    
    def call_anthropic_api(self, prompt: str) -> str:
        """
        Call the Anthropic API to generate a study plan with retry logic.
        
        Args:
            prompt: The prompt for the AI
            
        Returns:
            The generated study plan
        """
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        # Implement retry with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=data)
                
                # If successful, return the result
                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"]
                
                # If overloaded (status code 529), retry with backoff
                if response.status_code == 529:
                    wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                    print(f"API overloaded. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                    time.sleep(wait_time)
                    continue
                
                # For other errors, raise an exception
                response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                # For network errors, retry with backoff
                wait_time = (2 ** attempt) + random.random()
                print(f"Request error: {e}. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                time.sleep(wait_time)
        
        # If we've exhausted all retries, raise an exception
        raise Exception(f"API call failed after {self.max_retries} attempts. Last status code: {response.status_code}, response: {response.text}")
    
    def call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API to generate a study plan with retry logic.
        
        Args:
            prompt: The prompt for the AI
            
        Returns:
            The generated study plan
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert educational advisor specializing in personalized study plans."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000
        }
        
        # Implement retry with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=data)
                
                # If successful, return the result
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                
                # If rate limited, retry with backoff
                if response.status_code == 429:
                    wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                    print(f"API rate limited. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                    time.sleep(wait_time)
                    continue
                
                # For other errors, raise an exception
                response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                # For network errors, retry with backoff
                wait_time = (2 ** attempt) + random.random()
                print(f"Request error: {e}. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                time.sleep(wait_time)
        
        # If we've exhausted all retries, raise an exception
        raise Exception(f"API call failed after {self.max_retries} attempts. Last status code: {response.status_code}, response: {response.text}")
    
    def generate_study_plan(self, student_data: Dict[str, Any]) -> str:
        """
        Generate a personalized study plan for a student based on their grades.
        
        Args:
            student_data: Dictionary containing student information and grades
            
        Returns:
            The generated study plan
        """
        prompt = self.generate_prompt(student_data)
        
        if self.api_type == "anthropic":
            return self.call_anthropic_api(prompt)
        elif self.api_type == "openai":
            return self.call_openai_api(prompt)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")
