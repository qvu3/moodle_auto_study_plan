"""
AWS Lambda function handler for Moodle study plan generation.
This module serves as the entry point for AWS Lambda.
"""

import json
import logging
from moodle_study_plans import main as process_study_plans
import config

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda function handler.
    
    Args:
        event: The event dict that contains the parameters sent when the function is invoked
        context: Runtime information provided by AWS Lambda
        
    Returns:
        The response containing execution status and information
    """
    logger.info("Starting Moodle study plan generation Lambda function")
    
    try:
        # Validate configuration
        missing_config = config.validate_config()
        if missing_config:
            error_message = "Missing or invalid configuration: " + ", ".join(missing_config.keys())
            logger.error(error_message)
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'status': 'error',
                    'message': error_message
                })
            }
        
        # Log configuration summary (with sensitive data masked)
        logger.info(config.get_config_summary())
        
        # Run the main process
        process_study_plans()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Study plans generated and sent successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error in Lambda function: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        } 