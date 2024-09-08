from openai import OpenAI

OPENAI_API_KEY = "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"


# client = OpenAI(api_key=OPENAI_API_KEY)


response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
)
print(response['choices'][0]['message']['content'])

