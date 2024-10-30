import requests

url = "http://10.100.20.148:8002/analysis/"

# Input data to send (the bait string for analysis)
data = {
    "bait": "أنا الذي نظر الأعمي إالي أدبي و أسمعت كلماتي من به صمم"
}

# Send the POST request to the server
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Print the analysis result
    result = response.json()
    print("Analysis Result:")
    print(f"Qafya (Rhyme): {result['qafya']}")
    print(f"Meter: {result['meter']}")
    print(f"Critic: {result['critic']}")
    print(f"Rhetorical Devices: {result['rhetorical']}")
else:
    # Print error if the request failed
    print(f"Request failed with status code {response.status_code}")
    print(f"Error message: {response.text}")
