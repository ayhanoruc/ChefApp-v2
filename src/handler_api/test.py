import requests

#URL of the FastAPI endpoint on the AWS EC2 instance
url = "localhost:8000/get-recipe" # test-url

preferences = {
    "metadata": {
        "cusine": "italian",
        "level": "beginner-friendly",
        "health_n_wellness": "low-carb"
    },
    "items": ["tomato", "potato", "milk"]
}

# Send the POST request with JSON data
response = requests.post(url, json=preferences)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("Response:", data["response"])
else:
    print("Error:", response.status_code, response.text)