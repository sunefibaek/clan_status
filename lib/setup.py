import requests

def get_public_ip():
    response = requests.get('https://api.ipify.org')
    ip_address = response.text
    return ip_address

print(get_public_ip())