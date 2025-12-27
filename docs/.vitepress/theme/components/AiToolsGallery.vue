<script setup>
import { ref, computed } from 'vue'

const tools = [
  {
    category: 'Coding',
    name: 'Cursor',
    desc: 'The AI-first code editor.',
    link: 'https://cursor.sh/',
    icon: '💻'
  },
  {
    category: 'Coding',
    name: 'GitHub Copilot',
    desc: 'Your AI pair programmer.',
    link: 'https://github.com/features/copilot',
    icon: '🐙'
  },
  {
    category: 'Coding',
    name: 'Bolt.new',
    desc: 'Prompt to full-stack web app.',
    link: 'https://bolt.new/',
    icon: '⚡️'
  },
  {
    category: 'Coding',
    name: 'Windsurf',
    desc: 'Context-aware AI IDE.',
    link: 'https://codeium.com/windsurf',
    icon: '🏄'
  },
  {
    category: 'Image',
    name: 'Midjourney',
    desc: 'Hyper-realistic AI art generation.',
    link: 'https://www.midjourney.com/',
    icon: '🎨'
  },
  {
    category: 'Image',
    name: 'Flux',
    desc: 'Open state-of-the-art image model.',
    link: 'https://blackforestlabs.ai/',
    icon: '🌊'
  },
  {
    category: 'Image',
    name: 'Recraft',
    desc: 'Vector art and icon generation.',
    link: 'https://www.recraft.ai/',
    icon: '✏️'
  },
  {
    category: 'Video',
    name: 'Sora',
    desc: 'Text-to-video by OpenAI.',
    link: 'https://openai.com/sora',
    icon: '🎥'
  },
  {
    category: 'Video',
    name: 'Kling',
    desc: 'High-quality video generation.',
    link: 'https://kling.kuaishou.com/',
    icon: '🎬'
  },
  {
    category: 'Video',
    name: 'Runway',
    desc: 'Gen-3 Alpha video tools.',
    link: 'https://runwayml.com/',
    icon: '🎞️'
  },
  {
    category: 'Writing',
    name: 'ChatGPT',
    desc: 'The industry standard LLM.',
    link: 'https://chat.openai.com/',
    icon: '🤖'
  },
  {
    category: 'Writing',
    name: 'Claude',
    desc: 'Natural, nuanced writing.',
    link: 'https://claude.ai/',
    icon: '🧠'
  },
  {
    category: 'Writing',
    name: 'DeepSeek',
    desc: 'Powerful open-weight model.',
    link: 'https://www.deepseek.com/',
    icon: '🐳'
  },
  {
    category: 'Writing',
    name: 'Perplexity',
    desc: 'AI-powered answer engine.',
    link: 'https://www.perplexity.ai/',
    icon: '🔍'
  }
]

const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing']
const selectedCategory = ref('ALL')

const filteredTools = computed(() => {
  if (selectedCategory.value === 'ALL') return tools
  return tools.filter(t => t.category === selectedCategory.value)
})
</script>

<template>
  <div class="tools-gallery">
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

    <div class="tools-grid">
      <a 
        v-for="tool in filteredTools" 
        :key="tool.name" 
        :href="tool.link" 
        target="_blank"
        class="tool-card"
      >
        <div class="tool-icon">{{ tool.icon }}</div>
        <div class="tool-info">
          <div class="tool-header">
            <h3 class="tool-name">{{ tool.name }}</h3>
            <span class="tool-cat">{{ tool.category }}</span>
          </div>
          <p class="tool-desc">{{ tool.desc }}</p>
        </div>
        <div class="tool-arrow">↗</div>
      </a>
    </div>
  </div>
</template>

<style scoped>
.tools-gallery {
  padding: 40px 0;
  font-family: "Inter", sans-serif;
}

.category-filter {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 60px;
  flex-wrap: wrap;
}

.cat-btn {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  padding: 8px 24px;
  font-family: monospace;
  font-size: 14px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--vp-c-text-2);
}

.cat-btn:hover {
  border-color: var(--vp-c-text-1);
  color: var(--vp-c-text-1);
}

.cat-btn.active {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  border-color: var(--vp-c-text-1);
  font-weight: 700;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.tool-card {
  border: 1px solid var(--vp-c-divider);
  padding: 24px;
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--vp-c-text-1) !important;
  transition: all 0.2s;
  position: relative;
  background: var(--vp-c-bg);
  height: 200px;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 4px 4px 0 var(--vp-c-text-1);
  border-color: var(--vp-c-text-1);
}

.tool-icon {
  font-size: 32px;
  margin-bottom: 20px;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tool-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.tool-cat {
  font-size: 10px;
  font-family: monospace;
  text-transform: uppercase;
  border: 1px solid var(--vp-c-divider);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

.tool-desc {
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  margin: 0;
}

.tool-arrow {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tool-card:hover .tool-arrow {
  opacity: 1;
}
</style>
