from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],
    input="Top 3 promising sectors or stocks to research this week, with a 1-line rationale for each. Entry and exit signals with example indicators."
)

print(response.output_text)