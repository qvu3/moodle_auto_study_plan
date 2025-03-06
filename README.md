# Moodle Study Plan Generator

This project automatically retrieves student grades from Moodle, generates personalized study plans using AI, and sends them to students via email.

## Features

- Connects to Moodle API to retrieve student grades and information
- Processes grades to identify areas for improvement
- Generates personalized study plans using AI (Anthropic Claude or OpenAI)
- Sends study plans to students via email
- Can be run locally or deployed to AWS Lambda

## Prerequisites

- Python 3.8 or higher
- Moodle instance with API access enabled
- API key for Anthropic Claude or OpenAI
- SMTP server access for sending emails

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/moodle-study-plan-generator.git
   cd moodle-study-plan-generator
   ```

2. Create a virtual environment and install dependencies:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:

   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your actual credentials and settings.

## Configuration

The following environment variables need to be set in the `.env` file or in your environment:

### Moodle API Configuration

- `MOODLE_URL`: Your Moodle site URL
- `MOODLE_TOKEN`: Your Moodle API token
- `MOODLE_COURSE_ID`: The ID of the course to retrieve grades from

### AI API Configuration

- `AI_API_TYPE`: The AI API to use (`anthropic` or `openai`)
- `AI_API_KEY`: Your API key
- `AI_MAX_RETRIES`: Maximum number of retry attempts for API calls

### Email Configuration

- `SMTP_SERVER`: SMTP server address
- `SMTP_PORT`: SMTP server port
- `SENDER_EMAIL`: Sender's email address
- `SENDER_PASSWORD`: Sender's email password
- `EMAIL_SUBJECT_PREFIX`: Prefix for email subject
- `SENDER_NAME`: Name to display as the sender

## Usage

### Running Locally

To run the script locally:

```
python moodle_study_plans.py
```

### Scheduling with Cron

To run the script every Monday at 9 AM, add the following to your crontab:

```
0 9 * * 1 cd /path/to/moodle-study-plan-generator && /usr/bin/python3 moodle_study_plans.py >> cron.log 2>&1
```

### Deploying to AWS Lambda

1. Create a deployment package:

   ```
   pip install --target ./package -r requirements.txt
   cd package
   zip -r ../lambda_deployment_package.zip .
   cd ..
   zip -g lambda_deployment_package.zip *.py
   ```

2. Create a Lambda function in the AWS Console:

   - Runtime: Python 3.9+
   - Handler: `lambda_function.lambda_handler`
   - Timeout: At least 5 minutes
   - Memory: At least 512 MB

3. Upload the deployment package.

4. Set environment variables in the Lambda configuration.

5. Create an EventBridge rule to trigger the Lambda function every Monday at 9 AM:
   - Schedule expression: `cron(0 9 ? * MON *)`

## Project Structure

- `moodle_study_plans.py`: Main script that orchestrates the entire process
- `moodle_api.py`: Core API client for Moodle
- `moodle_grades.py`: Functions to retrieve and process grades
- `moodle_students.py`: Functions to retrieve student information and send emails
- `ai_integration.py`: Integration with AI APIs
- `grades_process.py`: Process grades and generate study plans
- `config.py`: Configuration module that loads environment variables
- `lambda_function.py`: AWS Lambda function handler

## Security Considerations

- The `.env` file contains sensitive information and should never be committed to version control
- For AWS Lambda, use environment variables instead of the `.env` file
- Consider using AWS Secrets Manager for storing sensitive credentials

## Troubleshooting

- If you encounter API rate limits or overloaded errors, the script will automatically retry with exponential backoff
- Check the logs for detailed error messages
- Ensure your Moodle API token has the necessary permissions
- For email issues, verify your SMTP settings and credentials

## License

This project is licensed under the MIT License - see the LICENSE file for details.
