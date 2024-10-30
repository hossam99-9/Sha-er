import requests

access_token = "eyJraWQiOiIyMDI0MTAwMjA4NDIiLCJhbGciOiJSUzI1NiJ9.eyJpYW1faWQiOiJJQk1pZC02OTEwMDBKRzRFIiwiaWQiOiJJQk1pZC02OTEwMDBKRzRFIiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiYjIxODZjZmQtYzNlMS00NGNmLTgxYWYtOGVlNGVhMDFjNmZjIiwiaWRlbnRpZmllciI6IjY5MTAwMEpHNEUiLCJnaXZlbl9uYW1lIjoiSXNsYW0iLCJmYW1pbHlfbmFtZSI6IkFobWVkIiwibmFtZSI6IklzbGFtIEFobWVkIiwiZW1haWwiOiJpc2xhbS5iYXNzdW5pLmV4dEBicmlnaHRza2llc2luYy5jb20iLCJzdWIiOiJpc2xhbS5iYXNzdW5pLmV4dEBicmlnaHRza2llc2luYy5jb20iLCJhdXRobiI6eyJzdWIiOiJpc2xhbS5iYXNzdW5pLmV4dEBicmlnaHRza2llc2luYy5jb20iLCJpYW1faWQiOiJJQk1pZC02OTEwMDBKRzRFIiwibmFtZSI6IklzbGFtIEFobWVkIiwiZ2l2ZW5fbmFtZSI6IklzbGFtIiwiZmFtaWx5X25hbWUiOiJBaG1lZCIsImVtYWlsIjoiaXNsYW0uYmFzc3VuaS5leHRAYnJpZ2h0c2tpZXNpbmMuY29tIn0sImFjY291bnQiOnsidmFsaWQiOnRydWUsImJzcyI6IjhkNWRiNWVjMTUwOTQ0ZjliMDdmOGJiNTI5YTQ2MjAwIiwiaW1zX3VzZXJfaWQiOiIxMjY3NzYyMSIsImZyb3plbiI6dHJ1ZSwiaW1zIjoiMjc0NjU3MCJ9LCJpYXQiOjE3Mjg1NjMxMDcsImV4cCI6MTcyODU2NjcwNywiaXNzIjoiaHR0cHM6Ly9pYW0uY2xvdWQuaWJtLmNvbS9pZGVudGl0eSIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImRlZmF1bHQiLCJhY3IiOjEsImFtciI6WyJwd2QiXX0.CGwLA7WNHejbTcJdRtub6peciaCpfVnptCokKTWs-nscEjB-aPm6FVYaqCfjA-ds2M1lqKZys2_bpVF3iOGGqZ0GyrrEJVZ6WWQNjCT0TzUIo3pq44IdmfKw_txdFYGXK3YN_Nw4laR2xMpydNnh9xUYNKtDuPZC3xWzZ0275y5F_JC26NNLPdG-fcEQc8AdrgzWG2ZSj1FPjGKa9yhSfrOKvU4NR3ebcBUdJb-3swkh7OOMMAK_cx-F6sPy5929pAyO8wfpCThwkpLiPX05DhwEpIHZK6kAsb1JA5Tt5vzmq3Ri-lXsRIUnPsG7CdmvRci1gBo3EyKccjghrTIFYQ"

url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

body = {
	"input": "<s> hi [INST]",
	"parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 900,
		"repetition_penalty": 1
	},
	"model_id": "sdaia/allam-1-13b-instruct",
	"project_id": "85b95f9c-2602-4bbe-85cf-abae5a6bb091"
}

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": f"Bearer {access_token}"
}

response = requests.post(
	url,
	headers=headers,
	json=body
)

if response.status_code != 200:
	raise Exception("Non-200 response: " + str(response.text))

data = response.json()
print(data)