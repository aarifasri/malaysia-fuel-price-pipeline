import requests
import pprint

url = "https://api.data.gov.my/data-catalogue?id=fuelprice&limit=5&sort=-date&filter=level@series_type"
response = requests.get(url)
data = response.json()
pprint.pprint(data)