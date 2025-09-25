import requests


headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NTQxNzk4NCwianRpIjoiZWJjMmZlMGEtMWE5Yy00MjgxLWI2OTctYzJlYjUyNDk0Zjg4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImVqQXRHZmpnemNiZG94OGlUWFFCOUoiLCJuYmYiOjE3NDU0MTc5ODQsImNzcmYiOiIzMTQyMTZhYS03M2NkLTRmYTctOTdiYS0yMmU1Yjc5MjQ5NzciLCJleHAiOjE3NDU0MTg4ODR9.O-5RQDWD-4O58_u48wPc8kx2Zb8Dk5x1-Xguc5oT5tM",
    "Content-Type": "application/json"
}

resp=requests.get("http://127.0.0.1:8200/cmsapi",headers=headers)
print(resp.text)