import requests

question = 'Who are you?'
dictToSend = [{"role": "user", "content": question}]
res = requests.post('http://api.onlysq.ru/ai/v1', json=dictToSend)
response = res.json()
print(response['answer'])