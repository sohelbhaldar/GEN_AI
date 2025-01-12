import ollama   

response = ollama.list()

res = ollama.chat(
    model="llama3.2",
    messages=[
        {"role":"user","content":"why is the sky blue?"},
    ],
    stream=True,
)

# for chunk in res:
#     print(chunk["message"]["content"], end="", flush=True)

print("\n\n")

res = ollama.generate(
    model="llama3.2",
    prompt="why is the sky blue?"
)
print(res["response"])

# print(ollama.show("llama3.2"))

#CREATE A NEW MODEL
# ollama.create(model="modelName", modelfile=modelfile)

#DELETE A NEW MODEL
# ollama.delete("Model name")



# for chunk in res:
#     print(chunk["message"]["content"], end="", flush=True)

#response = requests.post(url, json=data, stream=True)
# print("Generated Text:"+response.text,end=" ", flush=True)
# if response.status_code == 200:
#     print("Generated Text:", end=" ", flush=True)
#     for line in response.iter_lines():
#         if line:
#             decoded_line = line.decode("utf-8")
#             result = json.loads(decoded_line)
#             generated_text = result.get("response","")
#             print(generated_text,end="",flush=True)
# else:
#     print("Error:", response.status_code, response.text)