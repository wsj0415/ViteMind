const fs = require('fs');
const file = 'docs/.vitepress/theme/components/HomeBanner.vue';
let content = fs.readFileSync(file, 'utf8');

content = content.replace('<script setup>\n// HomeBanner.vue\n</script>', `<script setup>
import { useData, withBase } from 'vitepress'

const { theme } = useData()
</script>`);

content = content.replace('<span class="agency-logo">Logoisum</span>', '<span class="agency-logo">ViteMind</span>');

content = content.replace(/<div class="nav-center">[\s\S]*?<\/div>/, `<div class="nav-center">
        <a v-for="item in theme.nav" :key="item.link" :href="withBase(item.link)">{{ item.text }}</a>
      </div>`);

// Also, adjust CSS so that nav-center doesn't overflow horizontally.
content = content.replace('.nav-center {\n  display: flex;\n  gap: 32px;\n}', `.nav-center {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}`);

content = content.replace('.nav-center a {\n  font-family: \'Barlow\', sans-serif;\n  font-size: 14px;', `.nav-center a {
  font-family: 'Barlow', sans-serif;
  font-size: 13px;`);

fs.writeFileSync(file, content);
console.log('Done');
