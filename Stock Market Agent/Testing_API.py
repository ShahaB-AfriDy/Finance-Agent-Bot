import requests
import json
import os


api_url = 'https://api.api-ninjas.com/v1/exchangerate?pair=GBP_AUD'
response = requests.get(api_url, headers={'X-Api-Key': os.getenv("NINJAS_API_KEY")})
if response.status_code == requests.codes.ok:
    print(json.dumps(response.json(),indent=2))
else:
    print("Error:", response.status_code, response.text)
