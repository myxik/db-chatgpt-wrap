import openai
openai.api_key = "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"

# list models
models = openai.Model.list()

# print the first model's id
print(models)

# create a chat completion
chat_completion = openai.ChatCompletion.create(model="text-davinci-002", messages=[{"role": "user", "content": "Hello world"}])

# print the chat completion
print(chat_completion.choices[0].message.content)
