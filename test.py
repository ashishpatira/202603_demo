import requests
from bs4 import BeautifulSoup
import json

url = "https://www.ycombinator.com/companies/stripe"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
div = soup.find('div', attrs={'data-page': True})
if div:
    data = json.loads(div['data-page'])
    print("Has data-page!")
    company_data = data.get('props', {}).get('company', {})
    founders = company_data.get('founders', [])
    print("Founders:", [f.get('full_name') for f in founders])
else:
    print("No data-page div found")
