import os
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initial Prompts Data
initial_prompts = [
    # Coding
    {
        "title": "Python Code Optimizer",
        "category": "Coding",
        "content": "Analyze the following Python code and optimize it for performance and readability. Explain the changes made.\n\n[Insert Code Here]",
        "tags": ["Python", "Optimization", "Refactoring"]
    },
    {
        "title": "React Component Generator",
        "category": "Coding",
        "content": "Create a reusable React component for a [Component Name] using Tailwind CSS. Include props for [Prop 1, Prop 2] and ensure accessibility compliance.",
        "tags": ["React", "Tailwind", "Frontend"]
    },
    {
        "title": "SQL Query Builder",
        "category": "Coding",
        "content": "Write a complex SQL query to retrieve [Data Requirement] from tables [Table A] and [Table B], handling edge cases like null values.",
        "tags": ["SQL", "Database", "Backend"]
    },

    # Writing
    {
        "title": "SEO Blog Post Generator",
        "category": "Writing",
        "content": "Write a 1500-word SEO-optimized blog post about \"[Topic]\". Include a catchy title, meta description, and use the following keywords: [Keyword 1, Keyword 2]. Use H2 and H3 headers.",
        "tags": ["SEO", "Content Marketing", "Blog"]
    },
    {
        "title": "Cold Email Template",
        "category": "Writing",
        "content": "Draft a cold email to a potential client offering [Service Name]. Keep it under 150 words, professional yet conversational, and include a clear call to action.",
        "tags": ["Sales", "Email", "Marketing"]
    },

    # Image
    {
        "title": "Cyberpunk Cityscape",
        "category": "Image",
        "content": "A futuristic cyberpunk city at night, neon lights reflecting on wet pavement, towering skyscrapers with holographic ads, cinematic lighting, photorealistic, 8k resolution --ar 16:9",
        "tags": ["Midjourney", "Sci-Fi", "Landscape"]
    },
    {
        "title": "Minimalist Logo Design",
        "category": "Image",
        "content": "A minimalist vector logo for a tech startup named \"[Name]\", using geometric shapes and a blue color palette. Flat design, clean lines, white background.",
        "tags": ["Logo", "Design", "Vector"]
    },

    # Marketing
    {
        "title": "Social Media Content Calendar",
        "category": "Marketing",
        "content": "Create a one-week social media content calendar for a [Brand Niche] brand. Include post ideas for Instagram, LinkedIn, and Twitter, with suggested captions and visual concepts.",
        "tags": ["Social Media", "Strategy", "Planning"]
    },
    
    # Productivity
    {
        "title": "Meeting Minutes Summarizer",
        "category": "Productivity",
        "content": "Summarize the following meeting transcript into key takeaways, action items (with assignees), and decisions made.\n\n[Insert Transcript]",
        "tags": ["Meeting", "Summary", "Business"]
    }
]

def seed_prompts():
    print(f"Seeding {len(initial_prompts)} prompts to Supabase...")
    
    count = 0
    for prompt in initial_prompts:
        # Check if exists by title to avoid duplicates
        existing = supabase.table("ai_prompts").select("id").eq("title", prompt["title"]).execute()
        
        if existing.data:
            print(f"Skipping '{prompt['title']}' (already exists)")
            continue

        data = {
            "title": prompt["title"],
            "content": prompt["content"],
            "category": prompt["category"],
            "tags": prompt["tags"],
            "approved": True,
            "version": 1,
            "is_deleted": False
        }
        
        try:
            supabase.table("ai_prompts").insert(data).execute()
            print(f"Inserted '{prompt['title']}'")
            count += 1
        except Exception as e:
            print(f"Error inserting '{prompt['title']}': {e}")

    print(f"Done. Inserted {count} new prompts.")

if __name__ == "__main__":
    seed_prompts()
