def handler(request, response):
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    return {
        'message': 'Simple Python test endpoint',
        'working': True
    }