const MarkdownIt = require('markdown-it');

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true
});

// --- THE FIX LOGIC (Replica of NewsGallery.vue) ---
md.validateLink = (url) => {
  url = url.trim().toLowerCase()
  if (url.startsWith('/') || url.startsWith('#')) return true
  return url.startsWith('http:') || url.startsWith('https:')
}
// ---------------------

const inputs = [
  { text: '[Good HTTP](http://google.com)', shouldPass: true },
  { text: '[Good HTTPS](https://google.com)', shouldPass: true },
  { text: '[Good Relative](/foo)', shouldPass: true },
  { text: '[Good Anchor](#foo)', shouldPass: true },
  { text: '[Bad FTP](ftp://example.com)', shouldPass: false },
  { text: '[Bad Magnet](magnet:?)', shouldPass: false },
  { text: '[Bad Javascript](javascript:alert(1))', shouldPass: false },
  { text: '[Bad Unknown](unknown:foo)', shouldPass: false },
  { text: '[Bad File](file:///etc/passwd)', shouldPass: false }
];

let failed = false;

inputs.forEach(({ text, shouldPass }) => {
  const output = md.render(text).trim();
  const hasLink = output.includes('<a href="');

  // Note: markdown-it renders plain text for invalid links
  const passed = shouldPass ? hasLink : !hasLink;

  console.log(`Test: ${text}`);
  console.log(`Output: ${output}`);
  console.log(`Result: ${passed ? 'PASS' : 'FAIL'}`);
  console.log('---');

  if (!passed) failed = true;
});

if (failed) {
  console.error('Verification FAILED');
  process.exit(1);
} else {
  console.log('Verification PASSED');
}
