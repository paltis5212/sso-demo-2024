from authlib.integrations.flask_client import OAuth
oauth = OAuth()
oauth.register(
    name='sso',
    client_id='ikEN6LfzeTvi8CRgpJqGgAVZ',
    client_secret='sBRyhpuDwaDAFlxMhXCvGVGtZbecAlOB3YZMFjNBRxYMZiKo',
    request_token_url='https://www.svc.deltaww-energy.com:5001/oauth/token',
    request_token_params=None,
    access_token_url=None,
    access_token_params=None,
    authorize_url='https://www.svc.deltaww-energy.com:5001/oauth/authorize',
    authorize_params=None,
    api_base_url='https://www.svc.deltaww-energy.com:5001/',
    client_kwargs=None,
)

client = oauth.create_client('sso')