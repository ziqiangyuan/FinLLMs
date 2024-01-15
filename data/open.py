import openai

import os
#from openai.types import Model, ModelDeleted
openai.proxy = {'http': "http://127.0.0.1:7890",'https': "http://127.0.0.1:7890"}
###上面两行是为了在中国用，VPN相关
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )
openai.api_key = "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"
temp_text="hello"
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user",
        "content": temp_text}
    ]
)
print(completion.choices[0].message)
#print(client.models.list())