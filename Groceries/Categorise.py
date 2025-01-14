import ollama
import os

model ="llama3.2"
categorisePrompt_filePath ="./Data/CoregorisePrompt.txt"
input_filePath ="./Data/groceries.txt"
output_filePath ="./Data/Categorise_groceries.txt"

if not os.path.exists(input_filePath):
    print(f"\nInput file '{input_filePath}' not found1")
    exit(1)

if not os.path.exists(categorisePrompt_filePath):
    print(f"\nInput file '{categorisePrompt_filePath}' not found1")
    exit(1)

with open(input_filePath,"r") as f:
    items = f.read().strip()

print(f"Input file '{items}'\n")

with open(categorisePrompt_filePath,"r") as f:
    categorisePrompt = f.read().strip()

print(categorisePrompt)
print("\n")

categorisePromptstr = categorisePrompt.format(items=items)
print(categorisePromptstr)

try:
    resp = ollama.generate(model=model, prompt=categorisePromptstr)
    generated_txt =resp.get("response","")
    print("\nCategorized list:")
    print(generated_txt)

    with open(output_filePath,"w") as f:
        f.write(generated_txt.strip())
    
    print(f"Categorized list has been saved to '{output_filePath}'")
except Exception as e:
    print("An error occurred". str(e))

