"""
Ultra-simple Vercel function for testing.
"""

def handler(event, context):
    import json

    # Basic CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'message': 'Simple test endpoint working',
            'success': True
        })
    }