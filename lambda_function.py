"""
AWS Lambda function handler for Moodle study plan generation.
This module serves as the entry point for AWS Lambda.
"""

import json
import logging
from moodle_study_plans import main as process_study_plans
from generate_new_feature_plan import main as process_database_study_plans
import config
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda function handler.
    
    Args:
        event: The event dict that contains the parameters sent when the function is invoked
               Optional event parameters:
               - "feature": "original" (default), "database", or "both"
        context: Runtime information provided by AWS Lambda
        
    Returns:
        The response containing execution status and information
    """
    logger.info("Starting Moodle study plan generation Lambda function")
    
    try:
        # Get feature selection from environment variable first, then event, default to "original"
        feature = os.getenv('FEATURE', event.get('feature', 'original'))
        logger.info(f"Selected feature: {feature}")
        
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
        
        results = []
        
        # Run the original study plan generation
        if feature in ['original', 'both']:
            try:
                logger.info("Running original study plan generation...")
                process_study_plans()
                results.append("Original study plans generated successfully")
            except Exception as e:
                logger.error(f"Error in original study plan generation: {str(e)}")
                results.append(f"Original study plan generation failed: {str(e)}")
        
        # Run the database-based study plan generation
        if feature in ['database', 'both']:
            try:
                logger.info("Running database-based study plan generation...")
                process_database_study_plans()
                results.append("Database-based study plans generated successfully")
            except Exception as e:
                logger.error(f"Error in database-based study plan generation: {str(e)}")
                results.append(f"Database-based study plan generation failed: {str(e)}")
        
        # Check if any process was successful
        success_count = sum(1 for result in results if "successfully" in result)
        
        if success_count > 0:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Study plan generation completed',
                    'results': results
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'status': 'error',
                    'message': 'All study plan generation processes failed',
                    'results': results
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