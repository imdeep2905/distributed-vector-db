import os
import requests
import concurrent.futures

api_url = "http://127.0.0.1:8000/add_big_text"

# Function to read file content, split into parts, and make API requests
def process_file(file_path):
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        document_content = file.read()
        print(len(document_content))

    # Split document content into 10 parts
    total_parts = 15
    part_size = len(document_content) // total_parts

    # Prepare and make API requests for each part
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(total_parts):
            start_idx = i * part_size
            end_idx = (i + 1) * part_size if i < total_parts - 1 else None
            part_content = document_content[start_idx:end_idx]

            payload = {
                "document": part_content,
                "metadata": {"source": "file"},
                "id": f"{os.path.splitext(os.path.basename(file_path))[0]}_part_{i + 1}",
                "n_paragraph_sentences": 7
            }

            # Submit each part's API request as a separate task
            futures.append(executor.submit(make_api_request, payload, file_path, i + 1))

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

def make_api_request(payload, file_path, part_number):
    response = requests.post(api_url, json=payload)
    print(f"File: {file_path}, Part {part_number}, Status Code: {response.status_code}, Response: {response.text}")

# Specify the folder containing the .txt files
folder_path = "/Users/shivam/Downloads/Gutenberg/txt"

# Iterate through each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        file_path = os.path.join(folder_path, file_name)
        process_file(file_path)
