---
layout: page
title: " "
sidebar: false
---

<HomeBanner />

<NewsGallery />

<style>
/* Hide Search Bar on Homepage */
.VPNavBarSearch {
  display: none !important;
}

/* Hide default VitePress Nav to let the custom floating nav shine on the hero section */
.VPNav {
  display: none !important;
}

/* Ensure the page wrapper doesn't have top padding pushing down the hero */
.VPDoc {
  padding-top: 0 !important;
}

/* Fixes the extra space created by VitePress default layout when nav is hidden */
.VPContent {
  padding-top: 0 !important;
}
</style>
