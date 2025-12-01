"""
Vercel Python serverless function for authentication.
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import jwt
import datetime

# Demo credentials
DEMO_USERS = {
    "admin@entrepedia.ai": "admin123",
    "admin": "admin123",
    "testuser": "test123",
    "test@example.com": "test123"
}

def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload.update({"exp": expire})

    secret = "fallback-secret-key-for-demo"
    return jwt.encode(payload, secret, algorithm="HS256")

def handler(request):
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }

    # Handle preflight requests
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    path = request.url.path if hasattr(request.url, 'path') else getattr(request, 'path', '/')
    method = getattr(request, 'method', 'GET')

    try:
        # Health endpoint
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'mode': 'vercel-python'
                })
            }

        # Root endpoint
        if path == '/' or path == '':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Entrepedia AI Platform API',
                    'version': '1.0.0',
                    'mode': 'vercel-python'
                })
            }

        # Login endpoint
        if path == '/auth/login' and method == 'POST':
            # Parse form data
            body = getattr(request, 'body', '')
            if isinstance(body, bytes):
                body = body.decode('utf-8')

            form_data = parse_qs(body)
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]

            if username in DEMO_USERS and DEMO_USERS[username] == password:
                token = create_access_token({
                    'sub': username,
                    'user_id': 1
                })

                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'access_token': token,
                        'token_type': 'bearer'
                    })
                }
            else:
                return {
                    'statusCode': 401,
                    'headers': headers,
                    'body': json.dumps({
                        'detail': 'Incorrect username or password'
                    })
                }

        # Logout endpoint
        if path == '/auth/logout':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'Logged out successfully'
                })
            }

        # Verify token endpoint
        if path == '/auth/verify-token':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'Token valid',
                    'user': 'demo'
                })
            }

        # Not found
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Not found'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'detail': str(e)
            })
        }
