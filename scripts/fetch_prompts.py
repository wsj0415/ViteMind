import requests
import json
import os
from datetime import datetime
import random
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    pass

# Configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"

CATEGORIES = ['Coding', 'Image', 'Writing', 'Marketing', 'SEO', 'Productivity']

def generate_prompts_with_ai():
    prompts = []
    
    # Generate 1-2 prompts for a random category each run
    category = random.choice(CATEGORIES)
    
    prompt_text = f"""
    Generate 2 high-quality, professional AI prompts for the category: "{category}".
    
    For "Image" category, generate Midjourney/DALL-E style prompts.
    For "Coding", generate complex programming tasks for ChatGPT/Claude.
    For others, generate useful productivity/writing prompts.

    Output a JSON array with objects containing:
    - title: (string) Short, descriptive title.
    - content: (string) The actual prompt text.
    - tags: (array of strings) 2-3 relevant tags.
    
    Do not include markdown formatting. Just the JSON array.
    """

    from openai import OpenAI
    
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://api-inference.modelscope.cn/v1"
    )

    try:
        print(f"Generating prompts for {category}...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt_text}]
        )
        content = response.choices[0].message.content
        
        # Clean markdown
        content = content.replace("```json", "").replace("```", "").strip()
        
        new_prompts = json.loads(content)
        
        # Add metadata
        for p in new_prompts:
            p['category'] = category
            p['approved'] = True # Auto-approve AI generated prompts
            p['created_at'] = datetime.now().isoformat()
            prompts.append(p)
            
        return prompts

    except Exception as e:
        print(f"AI Generation Error: {e}")
        return []

def save_to_supabase(prompts):
    try:
        from supabase import create_client, Client
    except ImportError:
        print("Supabase library not installed.")
        return

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("Supabase credentials not found.")
        return

    try:
        supabase: Client = create_client(url, key)
        
        data_to_upsert = []
        for p in prompts:
            data_to_upsert.append({
                "title": p.get("title"),
                "content": p.get("content"),
                "category": p.get("category"),
                "tags": p.get("tags"),
                "approved": p.get("approved", True),
                "created_at": p.get("created_at")
            })
            
        if not data_to_upsert:
            return

        # Execute Insert
        response = supabase.table("ai_prompts").insert(data_to_upsert).execute()
        print(f"Successfully uploaded {len(data_to_upsert)} prompts to Supabase.")
        
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found.")
        exit(1)

    print("Starting AI Prompt Generator...")
    generated_prompts = generate_prompts_with_ai()
    
    if generated_prompts:
        save_to_supabase(generated_prompts)
    
    print("Done.")
