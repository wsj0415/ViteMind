<script setup>
// HomeBanner.vue
</script>

<template>
  <div class="home-banner">
    <div class="banner-container">
      <div class="banner-content">
        <div class="brand-row">
          <svg class="brand-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
            <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
          </svg>
          <span class="brand-text">ViteMind</span>
        </div>
        
        <h1 class="banner-title">
          UNCOVER THE<br>
          FUTURE OF AI.
        </h1>
        
        <p class="banner-subtitle">
          Curated Intelligence & News.
        </p>
      </div>

      <div class="banner-visual">
        <!-- Decorative Network Pattern (Simulated with SVG) -->
        <svg class="network-pattern" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
          <circle cx="50" cy="50" r="2" fill="#cbd5e1"/>
          <circle cx="150" cy="80" r="2" fill="#cbd5e1"/>
          <circle cx="250" cy="40" r="2" fill="#cbd5e1"/>
          <circle cx="350" cy="90" r="2" fill="#cbd5e1"/>
          <circle cx="80" cy="150" r="2" fill="#cbd5e1"/>
          <circle cx="200" cy="180" r="2" fill="#cbd5e1"/>
          <circle cx="320" cy="140" r="2" fill="#cbd5e1"/>
          <line x1="50" y1="50" x2="150" y2="80" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="150" y1="80" x2="250" y2="40" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="250" y1="40" x2="350" y2="90" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="50" y1="50" x2="80" y2="150" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="150" y1="80" x2="200" y2="180" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="80" y1="150" x2="200" y2="180" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="200" y1="180" x2="320" y2="140" stroke="#e2e8f0" stroke-width="1"/>
          <line x1="250" y1="40" x2="320" y2="140" stroke="#e2e8f0" stroke-width="1"/>
        </svg>
        
        <svg class="hero-brain-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
          <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-banner {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid var(--vp-c-divider);
  padding: 60px 0;
  overflow: hidden;
  position: relative;
}

.banner-container {
  max-width: 1152px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.banner-content {
  flex: 1;
  max-width: 600px;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.brand-icon {
  width: 32px;
  height: 32px;
  color: var(--vp-c-text-1);
}

.brand-text {
  font-family: "Inter", sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--vp-c-text-1);
  letter-spacing: -0.02em;
}

.banner-title {
  font-family: "Inter", sans-serif;
  font-size: 64px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--vp-c-text-1);
  margin: 0 0 16px 0;
  letter-spacing: -0.03em;
  text-transform: uppercase;
}

.banner-subtitle {
  font-family: "Inter", sans-serif;
  font-size: 24px;
  color: var(--vp-c-text-2);
  font-weight: 400;
  margin: 0;
}

.banner-visual {
  position: relative;
  width: 400px;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.network-pattern {
  position: absolute;
  top: 0;
  right: -50px;
  width: 100%;
  height: 100%;
  opacity: 0.5;
  transform: scale(1.5);
}

.hero-brain-icon {
  width: 120px;
  height: 120px;
  color: var(--vp-c-text-1);
  opacity: 0.1;
  position: absolute;
  bottom: 20px;
  right: 20px;
}

/* Dark mode adjustments */
:root.dark .home-banner {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

@media (max-width: 768px) {
  .banner-container {
    flex-direction: column;
    text-align: center;
  }
  
  .brand-row {
    justify-content: center;
  }
  
  .banner-title {
    font-size: 40px;
  }
  
  .banner-subtitle {
    font-size: 18px;
  }
  
  .banner-visual {
    display: none;
  }
}
</style>
