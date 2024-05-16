from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
   model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

openai_response = response.choices[0].message

print(openai_response)




