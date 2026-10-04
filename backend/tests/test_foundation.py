def test_health_and_openapi(env):
    c,_,_=env
    assert c.get('/health').status_code==200
    assert c.get('/openapi.json').status_code==200

def test_missing_token(env):
    c,_,_=env
    assert c.get('/api/v1/me').status_code==401
