#!/usr/bin/env python3
"""
Module for integrating with AI APIs to generate personalized study plans based on student grades.
"""

import requests
from typing import Dict, Any
import time
import random
import config
import google.generativeai as genai
import pandas as pd
from openai import OpenAI

class AIIntegration:
    def __init__(self, api_key: str = None, api_type: str = None, max_retries: int = None):
        """
        Initialize the AI integration.
        
        Args:
            api_key: The API key for the AI service. If None, uses the value from environment variables.
            api_type: The type of AI API to use ("anthropic", "openai", or "google_gemini"). If None, uses the value from environment variables.
            max_retries: Maximum number of retry attempts for API calls. If None, uses the value from environment variables.
        """
        self.api_key = api_key if api_key is not None else config.AI_API_KEY
        self.api_type = api_type if api_type is not None else config.AI_API_TYPE
        self.max_retries = max_retries if max_retries is not None else config.AI_MAX_RETRIES
        
        if not self.api_key:
            raise ValueError("AI API key is not set. Please set the AI_API_KEY environment variable.")
            
        self.api_type = self.api_type.lower()
        
        if self.api_type == "anthropic":
            self.api_url = "https://api.anthropic.com/v1/messages"
        elif self.api_type == "openai":
            # Initialize OpenAI client for v1.0+
            self.openai_client = OpenAI(api_key=self.api_key)
        elif self.api_type == "google_gemini":
            genai.configure(api_key=self.api_key)
            self.model_name = "gemini-2.5-flash-preview-05-20" # Using the specific model for preview
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}. Please use 'anthropic', 'openai' or 'google_gemini'.")
    
    def format_student_grades(self, student_data: Dict[str, Any]) -> str:
        """
        Format student grades for the AI prompt.
        
        Args:
            student_data: Dictionary containing student information and grades
            
        Returns:
            Formatted string of grades for the AI prompt
        """
        # Add debug logging
        print(f"Student data type: {type(student_data)}")
        print(f"Student data keys: {list(student_data.keys()) if isinstance(student_data, dict) else 'Not a dictionary'}")
        
        formatted_data = f"Student: {student_data.get('fullname', 'Unknown')}\n\n"
        formatted_data += "Grades:\n"
        
        # Add grades information - handle different data structures
        if 'grades' in student_data:
            grades = student_data['grades']
            
            # If grades is a dictionary
            if isinstance(grades, dict):
                for subject, grade in grades.items():
                    # Skip empty grades or grades with HTML
                    if grade != "- (-)" and grade != "" and "<" not in grade:
                        formatted_data += f"- {subject}: {grade}\n"
            # If grades is a list
            elif isinstance(grades, list):
                for grade_item in grades:
                    if isinstance(grade_item, dict):
                        item_name = grade_item.get('item_name', 'Unknown')
                        grade_value = grade_item.get('grade', '-')
                        percentage = grade_item.get('percentage', '-')
                        
                        # Skip empty grades or grades with HTML
                        if grade_value != "- (-)" and grade_value != "" and "<" not in str(grade_value):
                            formatted_data += f"- {item_name}: {grade_value} ({percentage})\n"
        
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
        3. Recommend study techniques and resources
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
        Call the OpenAI API to generate a study plan with retry logic using OpenAI 1.0+ client.
        
        Args:
            prompt: The prompt for the AI
            
        Returns:
            The generated study plan
        """
        # Implement retry with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert educational advisor specializing in personalized study plans."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                # Handle rate limiting and other errors
                wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                print(f"OpenAI API error: {e}. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                time.sleep(wait_time)
        
        # If we've exhausted all retries, raise an exception
        raise Exception(f"OpenAI API call failed after {self.max_retries} attempts.")
    
    def call_gemini_api(self, prompt: str) -> str:
        """
        Call the Google Gemini API to generate a study plan with retry logic.

        Args:
            prompt: The prompt for the AI

        Returns:
            The generated study plan
        """
        # Implement retry with exponential backoff
        for attempt in range(self.max_retries):
            try:
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                print(f"Gemini API error: {e}. Retrying in {wait_time:.2f} seconds (attempt {attempt+1}/{self.max_retries})...")
                time.sleep(wait_time)
        
        raise Exception(f"Gemini API call failed after {self.max_retries} attempts.")
    
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
        elif self.api_type == "google_gemini":
            return self.call_gemini_api(prompt)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")

def generate_study_plan_from_questions(questions_df):
    """
    Generate a personalized study plan based on incorrectly answered questions.
    """
    if questions_df.empty:
        return "No incorrectly answered questions found in the last week. Keep up the great work!"

    prompt = "Here are the questions a student answered incorrectly in the last 7 days:\n\n"
    for index, row in questions_df.iterrows():
        prompt += f"Question: {row['question_text']}\n"
        prompt += f"User's Answer: {row['user_answer']}\n"
        prompt += f"Correct Answer: {row['correct_answer']}\n\n"

    prompt += "Based on these incorrect answers, please generate a personalized study plan for the next week. The study plan should focus on the topics covered in these questions and provide resources or suggestions for improvement."

    # Create an AI integration instance
    ai_integration = AIIntegration()
    
    if ai_integration.api_type == "anthropic":
        return ai_integration.call_anthropic_api(prompt)
    elif ai_integration.api_type == "openai":
        return ai_integration.call_openai_api(prompt)
    elif ai_integration.api_type == "google_gemini":
        return ai_integration.call_gemini_api(prompt)
    else:
        raise ValueError(f"Invalid AI_API_TYPE: {ai_integration.api_type}")
