import os
import requests
import concurrent.futures
import threading

api_url = "http://127.0.0.1:8000/add_big_text"

# Function to make API requests for a single file
def process_file(file_path):
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        document_content = file.read()
        print(len(document_content))

    payload = {
        "document": document_content,
        "metadata": {"source": f"{os.path.splitext(os.path.basename(file_path))[0]}"},
        "id": f"{os.path.splitext(os.path.basename(file_path))[0]}",
        "n_paragraph_sentences": 7
    }

    make_api_request(payload, file_path)
count = 1
def make_api_request(payload, file_path):
    global count
    response = requests.post(api_url, json=payload)
    print(f"File: {file_path}, Status Code: {response.status_code}, Response: {response.text}")
    print("File Number: ", count)
    count+=1

# Specify the folder containing the .txt files
folder_path = "/Users/shivam/Downloads/Gutenberg/txt"

# Use ThreadPoolExecutor with a semaphore to limit concurrent processing
max_concurrent_files = 10
semaphore = threading.Semaphore(max_concurrent_files)

with concurrent.futures.ThreadPoolExecutor(max_concurrent_files) as executor:
    # Iterate through each file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            # Acquire the semaphore before submitting the task
            with semaphore:
                executor.submit(process_file, file_path)
