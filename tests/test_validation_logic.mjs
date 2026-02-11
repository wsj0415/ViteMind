import { isValidUrl } from '../docs/.vitepress/theme/utils/validation.js'

console.log('Testing isValidUrl...')

const testCases = [
    { url: 'https://example.com', expected: true },
    { url: 'http://example.com', expected: true },
    { url: 'ftp://example.com', expected: false },
    { url: 'javascript:alert(1)', expected: false },
    { url: 'javascript:alert(1)//http://example.com', expected: false },
    { url: 'mailto:user@example.com', expected: false }, // default is http/https only
    { url: 'not-a-url', expected: false },
    { url: '', expected: false },
]

let passed = 0
let total = testCases.length

for (const tc of testCases) {
    const result = isValidUrl(tc.url)
    if (result === tc.expected) {
        passed++
    } else {
        console.error(`FAILED: "${tc.url}" -> expected ${tc.expected}, got ${result}`)
    }
}

// Test custom protocols
total++
if (isValidUrl('mailto:user@example.com', ['mailto:'])) {
    passed++
} else {
    console.error('FAILED: mailto custom protocol')
}

// Test multiple custom protocols
total++
if (isValidUrl('custom://abc', ['custom:', 'http:'])) {
    passed++
} else {
    console.error('FAILED: multiple custom protocols')
}

console.log(`Passed ${passed}/${total}`)

if (passed === total) {
    console.log('ALL TESTS PASSED')
    process.exit(0)
} else {
    process.exit(1)
}
