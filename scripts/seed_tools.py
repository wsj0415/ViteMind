import os
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initial Data (from AiToolsGallery.vue)
initial_tools = [
  # Coding
  { "category": 'Coding', "name": 'Cursor', "description": 'AI-first code editor.', "link": 'https://cursor.sh/', "tags": ['Editor', 'Free'] },
  { "category": 'Coding', "name": 'GitHub Copilot', "description": 'AI pair programmer.', "link": 'https://github.com/features/copilot', "tags": ['Extension', 'Paid'] },
  { "category": 'Coding', "name": 'Bolt.new', "description": 'Full-stack web app generator.', "link": 'https://bolt.new/', "tags": ['Web', 'Free'] },
  { "category": 'Coding', "name": 'Windsurf', "description": 'Context-aware AI IDE.', "link": 'https://codeium.com/windsurf', "tags": ['IDE', 'Free'] },
  { "category": 'Coding', "name": 'V0.dev', "description": 'UI generation by Vercel.', "link": 'https://v0.dev/', "tags": ['UI', 'Free'] },
  
  # Image
  { "category": 'Image', "name": 'Midjourney', "description": 'Hyper-realistic AI art.', "link": 'https://www.midjourney.com/', "tags": ['Discord', 'Paid'] },
  { "category": 'Image', "name": 'Flux', "description": 'SOTA open image model.', "link": 'https://blackforestlabs.ai/', "tags": ['Open Source', 'Free'] },
  { "category": 'Image', "name": 'Recraft', "description": 'Vector art & icons.', "link": 'https://www.recraft.ai/', "tags": ['Design', 'Free'] },
  { "category": 'Image', "name": 'Freepik', "description": 'AI resource generator.', "link": 'https://www.freepik.com/', "tags": ['Design', 'Freemium'] },

  # Video
  { "category": 'Video', "name": 'Sora', "description": 'OpenAI text-to-video.', "link": 'https://openai.com/sora', "tags": ['Waitlist'] },
  { "category": 'Video', "name": 'Kling', "description": 'High-quality video gen.', "link": 'https://kling.kuaishou.com/', "tags": ['Web', 'Free'] },
  { "category": 'Video', "name": 'Runway', "description": 'Gen-3 Alpha video tools.', "link": 'https://runwayml.com/', "tags": ['Web', 'Paid'] },
  { "category": 'Video', "name": 'Luma Dream Machine', "description": 'Fast video generation.', "link": 'https://lumalabs.ai/dream-machine', "tags": ['Web', 'Free'] },
  { "category": 'Video', "name": 'HeyGen', "description": 'AI avatar video gen.', "link": 'https://www.heygen.com/', "tags": ['Avatar', 'Paid'] },

  # Writing
  { "category": 'Writing', "name": 'ChatGPT', "description": 'The standard LLM.', "link": 'https://chat.openai.com/', "tags": ['Chat', 'Freemium'] },
  { "category": 'Writing', "name": 'Claude', "description": 'Natural, nuanced writing.', "link": 'https://claude.ai/', "tags": ['Chat', 'Freemium'] },
  { "category": 'Writing', "name": 'DeepSeek', "description": 'Powerful open model.', "link": 'https://www.deepseek.com/', "tags": ['Chat', 'Free'] },
  { "category": 'Writing', "name": 'Perplexity', "description": 'AI answer engine.', "link": 'https://www.perplexity.ai/', "tags": ['Search', 'Freemium'] },
  { "category": 'Writing', "name": 'NotebookLM', "description": 'AI research assistant.', "link": 'https://notebooklm.google.com/', "tags": ['Research', 'Free'] },

  # Audio
  { "category": 'Audio', "name": 'Suno', "description": 'Make music with AI.', "link": 'https://suno.com/', "tags": ['Music', 'Free'] },
  { "category": 'Audio', "name": 'Udio', "description": 'High-fidelity music gen.', "link": 'https://www.udio.com/', "tags": ['Music', 'Free'] },
  { "category": 'Audio', "name": 'ElevenLabs', "description": 'Realistic text-to-speech.', "link": 'https://elevenlabs.io/', "tags": ['Voice', 'Paid'] },

  # Productivity
  { "category": 'Productivity', "name": 'Gamma', "description": 'AI presentation maker.', "link": 'https://gamma.app/', "tags": ['Slides', 'Freemium'] },
  { "category": 'Productivity', "name": 'Notion AI', "description": 'Connected workspace.', "link": 'https://www.notion.so/', "tags": ['Docs', 'Paid'] },
]

def seed_data():
    print(f"Seeding {len(initial_tools)} tools to Supabase...")
    
    data_to_insert = []
    for tool in initial_tools:
        data_to_insert.append({
            "name": tool["name"],
            "description": tool["description"],
            "link": tool["link"],
            "category": tool["category"],
            "tags": tool["tags"],
            "approved": True
        })

    try:
        # Atomic Upsert (Requires UNIQUE constraint on 'link')
        response = supabase.table("ai_tools").upsert(data_to_insert, on_conflict="link").execute()
        print(f"Success! Upserted {len(data_to_insert)} tools.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        print("HINT: Did you add the UNIQUE constraint to the 'link' column?")

if __name__ == "__main__":
    seed_data()
