from database import get_wrongly_answered_questions, get_correctly_answered_questions
from ai_integration import generate_study_plan_from_questions, AIIntegration
from moodle_students import get_student_info, send_study_plan_email
import config
import sys
import os

def main():
    """
    Main function to generate and send appropriate emails based on student performance.
    """
    print("Starting study plan generation for all students...")

    # Get all students
    students = get_student_info()
    if not students:
        print("No students found or could not retrieve student information.")
        return

    print(f"Found {len(students)} students. Processing each one.")

    for student_id, student_info in students.items():
        # We only want to process students, not teachers or other roles
        if 'student' not in student_info.get('roles', []):
            print(f"Skipping {student_info.get('fullname')} as they are not a student.")
            continue

        print(f"Processing user: {student_info.get('fullname')} (ID: {student_id})")

        # Get both wrongly and correctly answered questions
        wrong_questions_df = get_wrongly_answered_questions(student_id)
        correct_questions_df = get_correctly_answered_questions(student_id)
        
        # Check if we could retrieve the data
        if wrong_questions_df is None or correct_questions_df is None:
            print(f"Could not retrieve question data for student {student_id}. Skipping.")
            continue

        # Determine what kind of activity the student has
        has_wrong_answers = not wrong_questions_df.empty
        has_correct_answers = not correct_questions_df.empty

        if has_wrong_answers:
            # Case 1: Student has wrong answers (with or without correct answers)
            # Send study plan based on wrong answers
            print(f"Student has wrong answers. Generating study plan for {student_info.get('fullname')}...")
            study_plan = generate_study_plan_from_questions(wrong_questions_df)
            print("Study plan generated successfully.")

            # Send study plan email
            print(f"Sending study plan to {student_info.get('email')}...")
            study_plan_path = f"temp_{student_id}_study_plan.txt"
            with open(study_plan_path, "w", encoding='utf-8') as f:
                f.write(study_plan)
                
            send_study_plan_email(student_info, study_plan_path)
            os.remove(study_plan_path)
            print(f"Study plan sent successfully to {student_info.get('fullname')}.")

        elif has_correct_answers:
            # Case 2: Student only has correct answers (no wrong answers)
            # Send congratulatory email
            print(f"Student only has correct answers. Sending congratulatory email to {student_info.get('fullname')}...")
            
            congratulatory_message = f"""
Congratulations, {student_info.get('fullname')}!

From Black Belt Test Prep, we're thrilled to let you know that you haven't answered any questions incorrectly in the past 7 days. This is an outstanding achievement that demonstrates your dedication and understanding of the material!

Your consistent performance shows that you're:
- Mastering the concepts
- Staying focused during assessments  
- Applying your knowledge effectively

Keep up the excellent work! Here are some suggestions to maintain your momentum:

RECOMMENDATIONS TO STAY SHARP:
- Review previous topics to reinforce your knowledge
- Challenge yourself with advanced practice questions
- Help fellow students who might be struggling
- Take some time to celebrate your success!
- Follow us on TikTok @blackbelttestprep for more PANCE PRO tips!

Remember, consistency is key to long-term success. Your hard work is paying off, and we're proud of your progress.

Keep striving for excellence!

Best regards,
{config.SENDER_NAME}

---
"Success is not final, failure is not fatal: it is the courage to continue that counts." - Winston Churchill
            """.strip()
            
            study_plan_path = f"temp_{student_id}_congratulations.txt"
            with open(study_plan_path, "w", encoding='utf-8') as f:
                f.write(congratulatory_message)
                
            congratulatory_subject = f"🎉 Congratulations on Your Perfect Performance! - {student_info.get('fullname')}"
            send_study_plan_email(student_info, study_plan_path, custom_subject=congratulatory_subject)
            os.remove(study_plan_path)
            print(f"Congratulatory email sent successfully to {student_info.get('fullname')}.")

        else:
            # Case 3: Student has no activity (no wrong or correct answers)
            # Send reminder email to encourage practice
            print(f"Student has no recent activity. Sending reminder email to {student_info.get('fullname')}...")
            
            reminder_message = f"""
Hello {student_info.get('fullname')},

We hope you're doing well! We noticed that you haven't practiced on Black Belt Test Prep in the past 7 days, and we wanted to reach out to encourage you to get back on track.

From Black Belt Test Prep, we understand that life can get busy, but consistent practice is crucial for success on your upcoming exam. Even just a few questions a day can make a significant difference in your preparation.

WHAT YOU MISSED ON BLACK BELT TEST PREP:
- Timed quizzes that can pause and resume anytime
- Weekly personalized study plans based on your performance, delivered to your email automatically every week
- Track your progress with our new dashboard
- See other students' answers to questions you got wrong
and so much more!

HERE'S WHY REGULAR PRACTICE MATTERS:
- Keeps concepts fresh in your memory
- Builds confidence for exam day
- Identifies knowledge gaps early
- Develops test-taking stamina
- Reinforces learning through repetition

GETTING BACK ON TRACK:
- Start with just 10-15 questions per day
- Focus on your weaker subject areas
- Review explanations for both correct and incorrect answers
- Set a daily reminder to maintain consistency
- Follow us on TikTok @blackbelttestprep for daily motivation and tips!

Remember, every expert was once a beginner, and every professional was once an amateur. The key is to never stop practicing and improving.

We believe in your potential and are here to support your journey to success. Log back in today and take the first step toward achieving your goals!

Best regards,
{config.SENDER_NAME}

---
"The expert in anything was once a beginner who refused to give up."
            """.strip()
            
            study_plan_path = f"temp_{student_id}_reminder.txt"
            with open(study_plan_path, "w", encoding='utf-8') as f:
                f.write(reminder_message)
                
            reminder_subject = f"📚 We Miss You! Time to Get Back to Practice - {student_info.get('fullname')}"
            send_study_plan_email(student_info, study_plan_path, custom_subject=reminder_subject)
            os.remove(study_plan_path)
            print(f"Reminder email sent successfully to {student_info.get('fullname')}.")

if __name__ == "__main__":
    main() 