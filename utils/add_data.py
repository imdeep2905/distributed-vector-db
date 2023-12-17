import os
import requests
import json

api_url = "http://127.0.0.1:8000/add_big_text"

# Function to read file content and make API request
def process_file(file_path):
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        document_content = file.read()
        print(len(document_content))

    # Prepare the payload
    payload = {
        "document": document_content,
        "metadata": {"source": "file"},
        "id": os.path.splitext(os.path.basename(file_path))[0],  # Use file name as id
        "n_paragraph_sentences": 3
    }
    
    # print(payload)

    # Make the API request
    response = requests.post(api_url, json=payload)

    # Print the response (you can customize this based on your needs)
    print(f"File: {file_path}, Status Code: {response.status_code}, Response: {response.text}")

# Specify the folder containing the .txt files
folder_path = "/Users/jayminsuhagiya/Desktop/Gutenberg/txt"

# Iterate through each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        file_path = os.path.join(folder_path, file_name)
        process_file(file_path)
