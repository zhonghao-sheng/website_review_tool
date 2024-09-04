import requests



okta_domain = 'dev-53645540.okta.com'

url = f'https://{okta_domain}/.well-known/openid-configuration'

print(f'Attempting to access: {url}')



response = requests.get(url)

print(response.status_code)

print(response.text)
