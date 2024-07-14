import json
from mistralai.client import MistralClient
from supabase import create_client, Client

# Initialize Mistral and Supabase clients
client = MistralClient("u2J9xMhy5qFjgpzMaCCT7YnoCIq1kjlH")
supabase_url = "https://ajmjjshqrkriiczbvanq.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqbWpqc2hxcmtyaWljemJ2YW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjA3OTQ0NDgsImV4cCI6MjAzNjM3MDQ0OH0.XbZQSI1rwm0G_wTWg9hyNFsNIGmbkLqpvJy_C0-Vu8E"
supabase: Client = create_client(supabase_url, supabase_key)

def extract_text_from_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            texts = []
            for section in ['introduction', 'key_concepts', 'tutorial_steps', 'examples_and_use_cases', 'metadata', 'code_snippets_python']:
                if section == 'key_concepts' or section == 'tutorial_steps':
                    for key, value in data[section].items():
                        texts.append({'section': section, 'key': key, 'content': value['content']})
                elif section == 'examples_and_use_cases':
                    for key, value in data[section].items():
                        texts.append({'section': section, 'key': key, 'content': value['content']})
                elif section == 'metadata':
                    for key, value in data[section].items():
                        texts.append({'section': section, 'key': key, 'content': ', '.join(value)})
                elif section == 'code_snippets_python':
                    for key, value in data[section].items():
                        texts.append({'section': section, 'key': key, 'content': value['description'] + ' ' + value['code']})
                else:
                    texts.append({'section': section, 'content': data[section]['content']})
            return texts
    except Exception as e:
        print(f"Error reading the file: {e}")
        return []

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    punctuation_to_remove = ",!.?"
    text = text.translate(str.maketrans('', '', punctuation_to_remove))
    return text

def preprocess_json_data(data):
    for item in data:
        item['content'] = preprocess_text(item['content'])
    return data

def create_embeddings(text_data):
    try:
        sentences = [item['content'] for item in text_data]
        response = client.embeddings(
            model='mistral-embed',
            input=sentences
        )
        embeddings = response.data
        data = [
            {'section': item['section'], 'key': item.get('key'), 'content': item['content'], 'embedding': embedding.embedding}
            for item, embedding in zip(text_data, embeddings)
        ]
        return data
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return []

def main():
    json_file = 'structured_data.json' 
    text_data = extract_text_from_json(json_file)
    if not text_data:
        print("No text extracted from JSON.")
        return

    # Preprocess the text data
    preprocessed_data = preprocess_json_data(text_data)
    
    embeddings = create_embeddings(preprocessed_data)
    if not embeddings:
        print("No embeddings created.")
        return

    try:
        response = supabase.table('gspipe').insert(embeddings).execute()
        print("Upload complete!")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

if __name__ == "__main__":
    main()