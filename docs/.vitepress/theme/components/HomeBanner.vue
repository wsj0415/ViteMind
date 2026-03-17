<script setup>
import { useData, withBase } from 'vitepress'

const { theme } = useData()
</script>

<template>
  <div class="home-hero">
    <video
      class="hero-video"
      src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260228_065522_522e2295-ba22-457e-8fdb-fbcd68109c73.mp4"
      autoplay
      loop
      muted
      playsinline
    ></video>

    <div class="hero-overlay"></div>

    <nav class="floating-nav">
      <div class="nav-left">
        <span class="agency-logo">ViteMind</span>
      </div>
      <div class="nav-center">
        <a v-for="item in theme.nav" :key="item.link" :href="withBase(item.link)">{{ item.text }}</a>
      </div>
      <div class="nav-right">
        <button class="primary-cta">
          Book A Free Meeting
          <span class="cta-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="7" y1="17" x2="17" y2="7"></line>
              <polyline points="7 7 17 7 17 17"></polyline>
            </svg>
          </span>
        </button>
      </div>
    </nav>

    <div class="hero-content">
      <h1 class="primary-headline">
        <span class="headline-line1">Agency that makes your</span><br>
        <span class="headline-line2">videos & reels viral</span>
      </h1>
      <p class="hero-subtext">
        Short-form video editing for Influencers, Creators and Brands
      </p>
      <button class="secondary-cta">
        <span class="play-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        </span>
        See Our Workreel
      </button>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&family=Instrument+Serif:ital@0;1&display=swap');

.home-hero {
  position: relative;
  width: 100vw;
  min-height: 90vh;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  background-color: #000;
}

.hero-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2); /* Slight darkening if needed, but requested no color overlays. I will leave it transparent or very subtle for text readability just in case. The prompt said "without any color overlays". I will remove it. */
  z-index: 1;
}

/* Let's remove the overlay as per "without any color overlays" */
.hero-overlay {
  display: none;
}

.floating-nav {
  position: absolute;
  top: 32px;
  width: calc(100% - 64px);
  max-width: 1200px;
  background-color: #ffffff;
  border-radius: 16px;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.nav-left .agency-logo {
  font-family: 'Barlow', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #222;
}

.nav-center {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.nav-center a {
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: #444;
  text-decoration: none;
  transition: color 0.3s ease;
}

.nav-center a:hover {
  color: #000;
}

.primary-cta {
  background-color: #222;
  color: #fff;
  font-family: 'Barlow', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 30px;
  padding: 8px 12px 8px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.primary-cta:hover {
  background-color: #000;
}

.cta-icon {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.cta-icon svg {
  width: 14px;
  height: 14px;
  color: #fff;
}

.hero-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  padding: 0 24px;
  margin-top: 80px; /* Space for the floating nav */
}

.primary-headline {
  margin: 0;
  color: #fff;
}

.headline-line1 {
  font-family: 'Barlow', sans-serif;
  font-weight: 600; /* bold/medium */
  font-size: 48px;
  letter-spacing: -4px;
  line-height: 1.1;
  display: block;
}

.headline-line2 {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 84px;
  font-weight: 400;
  line-height: 1.1;
  display: block;
  margin-top: 4px;
}

.hero-subtext {
  font-family: 'Barlow', sans-serif;
  font-weight: 500; /* Medium */
  font-size: 18px;
  color: #fff;
  margin: 24px 0 40px;
  max-width: 600px;
  opacity: 0.9;
}

.secondary-cta {
  background-color: #fff;
  color: #222;
  font-family: 'Barlow', sans-serif;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 40px;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.secondary-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.play-icon {
  display: flex;
  justify-content: center;
  align-items: center;
}

.play-icon svg {
  width: 16px;
  height: 16px;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .floating-nav {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
    border-radius: 24px;
  }
  
  .nav-center {
    display: none; /* Hide standard menu on mobile, or implement a hamburger */
  }
  
  .headline-line1 {
    font-size: 32px;
    letter-spacing: -2px;
  }
  
  .headline-line2 {
    font-size: 56px;
  }
  
  .hero-subtext {
    font-size: 16px;
  }
}
</style>
