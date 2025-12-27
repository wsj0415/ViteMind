<script setup>
import { ref, computed } from 'vue'

const tools = [
  // Coding
  { category: 'Coding', name: 'Cursor', desc: 'AI-first code editor.', link: 'https://cursor.sh/', icon: '💻', tags: ['Editor', 'Free'] },
  { category: 'Coding', name: 'GitHub Copilot', desc: 'AI pair programmer.', link: 'https://github.com/features/copilot', icon: '🐙', tags: ['Extension', 'Paid'] },
  { category: 'Coding', name: 'Bolt.new', desc: 'Full-stack web app generator.', link: 'https://bolt.new/', icon: '⚡️', tags: ['Web', 'Free'] },
  { category: 'Coding', name: 'Windsurf', desc: 'Context-aware AI IDE.', link: 'https://codeium.com/windsurf', icon: '🏄', tags: ['IDE', 'Free'] },
  { category: 'Coding', name: 'V0.dev', desc: 'UI generation by Vercel.', link: 'https://v0.dev/', icon: '📐', tags: ['UI', 'Free'] },
  
  // Image
  { category: 'Image', name: 'Midjourney', desc: 'Hyper-realistic AI art.', link: 'https://www.midjourney.com/', icon: '🎨', tags: ['Discord', 'Paid'] },
  { category: 'Image', name: 'Flux', desc: 'SOTA open image model.', link: 'https://blackforestlabs.ai/', icon: '🌊', tags: ['Open Source', 'Free'] },
  { category: 'Image', name: 'Recraft', desc: 'Vector art & icons.', link: 'https://www.recraft.ai/', icon: '✏️', tags: ['Design', 'Free'] },
  { category: 'Image', name: 'Freepik', desc: 'AI resource generator.', link: 'https://www.freepik.com/', icon: '🖼️', tags: ['Design', 'Freemium'] },

  // Video
  { category: 'Video', name: 'Sora', desc: 'OpenAI text-to-video.', link: 'https://openai.com/sora', icon: '🎥', tags: ['Waitlist'] },
  { category: 'Video', name: 'Kling', desc: 'High-quality video gen.', link: 'https://kling.kuaishou.com/', icon: '🎬', tags: ['Web', 'Free'] },
  { category: 'Video', name: 'Runway', desc: 'Gen-3 Alpha video tools.', link: 'https://runwayml.com/', icon: '🎞️', tags: ['Web', 'Paid'] },
  { category: 'Video', name: 'Luma Dream Machine', desc: 'Fast video generation.', link: 'https://lumalabs.ai/dream-machine', icon: '☁️', tags: ['Web', 'Free'] },
  { category: 'Video', name: 'HeyGen', desc: 'AI avatar video gen.', link: 'https://www.heygen.com/', icon: '🗣️', tags: ['Avatar', 'Paid'] },

  // Writing
  { category: 'Writing', name: 'ChatGPT', desc: 'The standard LLM.', link: 'https://chat.openai.com/', icon: '🤖', tags: ['Chat', 'Freemium'] },
  { category: 'Writing', name: 'Claude', desc: 'Natural, nuanced writing.', link: 'https://claude.ai/', icon: '🧠', tags: ['Chat', 'Freemium'] },
  { category: 'Writing', name: 'DeepSeek', desc: 'Powerful open model.', link: 'https://www.deepseek.com/', icon: '🐳', tags: ['Chat', 'Free'] },
  { category: 'Writing', name: 'Perplexity', desc: 'AI answer engine.', link: 'https://www.perplexity.ai/', icon: '🔍', tags: ['Search', 'Freemium'] },
  { category: 'Writing', name: 'NotebookLM', desc: 'AI research assistant.', link: 'https://notebooklm.google.com/', icon: '📓', tags: ['Research', 'Free'] },

  // Audio
  { category: 'Audio', name: 'Suno', desc: 'Make music with AI.', link: 'https://suno.com/', icon: '🎵', tags: ['Music', 'Free'] },
  { category: 'Audio', name: 'Udio', desc: 'High-fidelity music gen.', link: 'https://www.udio.com/', icon: '🎧', tags: ['Music', 'Free'] },
  { category: 'Audio', name: 'ElevenLabs', desc: 'Realistic text-to-speech.', link: 'https://elevenlabs.io/', icon: '🎙️', tags: ['Voice', 'Paid'] },

  // Productivity
  { category: 'Productivity', name: 'Gamma', desc: 'AI presentation maker.', link: 'https://gamma.app/', icon: '📊', tags: ['Slides', 'Freemium'] },
  { category: 'Productivity', name: 'Notion AI', desc: 'Connected workspace.', link: 'https://www.notion.so/', icon: '📝', tags: ['Docs', 'Paid'] },
]

const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')

const filteredTools = computed(() => {
  return tools.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          t.desc.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})
</script>

<template>
  <div class="tools-gallery">
    <!-- Search & Filter Bar -->
    <div class="control-bar">
      <div class="search-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="SEARCH TOOLS..." 
          class="search-input"
        />
      </div>

      <div class="category-filter">
        <button 
          v-for="cat in categories" 
          :key="cat"
          class="cat-btn"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Grid -->
    <div class="tools-grid">
      <a 
        v-for="tool in filteredTools" 
        :key="tool.name" 
        :href="tool.link" 
        target="_blank"
        class="tool-card"
      >
        <div class="card-top">
          <div class="tool-icon">{{ tool.icon }}</div>
          <div class="tool-arrow">↗</div>
        </div>
        
        <div class="card-content">
          <h3 class="tool-name">{{ tool.name }}</h3>
          <p class="tool-desc">{{ tool.desc }}</p>
        </div>

        <div class="card-footer">
          <span class="tool-cat">{{ tool.category }}</span>
          <div class="tool-tags">
            <span v-for="tag in tool.tags" :key="tag" class="mini-tag">{{ tag }}</span>
          </div>
        </div>
      </a>
    </div>

    <div v-if="filteredTools.length === 0" class="no-results">
      NO TOOLS FOUND
    </div>
  </div>
</template>

<style scoped>
.tools-gallery {
  padding: 20px 0 60px;
  font-family: "Inter", sans-serif;
  color: var(--vp-c-text-1);
}

/* Controls */
.control-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  margin-bottom: 60px;
}

.search-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.search-input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  font-family: monospace;
  font-size: 14px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
  border-radius: 8px;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: var(--vp-c-brand);
  box-shadow: 0 0 0 2px var(--vp-c-brand-dimm);
  outline: none;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.cat-btn {
  background: transparent;
  border: 1px solid transparent;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 20px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  transition: all 0.2s;
  background: var(--vp-c-bg-alt);
}

.cat-btn:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-mute);
}

.cat-btn.active {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  font-weight: 600;
}

/* Grid */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.tool-card {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--vp-c-text-1) !important;
  transition: all 0.2s ease;
  height: 220px;
}

.tool-card:hover {
  transform: translateY(-4px);
  border-color: var(--vp-c-brand);
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.tool-icon {
  font-size: 36px;
  background: var(--vp-c-bg-alt);
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.tool-arrow {
  font-size: 14px;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.tool-card:hover .tool-arrow {
  opacity: 1;
  color: var(--vp-c-brand);
}

.card-content {
  flex: 1;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.tool-desc {
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.tool-cat {
  font-weight: 600;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
  letter-spacing: 0.5px;
}

.tool-tags {
  display: flex;
  gap: 6px;
}

.mini-tag {
  background: var(--vp-c-bg-alt);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

.no-results {
  text-align: center;
  padding: 60px;
  color: var(--vp-c-text-3);
  font-family: monospace;
}
</style>
