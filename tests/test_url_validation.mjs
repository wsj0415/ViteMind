
import { isValidUrl } from '../docs/.vitepress/theme/utils/validation.js';

console.log('Running URL Validation Tests...');

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        console.log(`✅ PASS: ${message}`);
        passed++;
    } else {
        console.error(`❌ FAIL: ${message}`);
        failed++;
    }
}

// Test Cases
const tests = [
    { url: 'https://google.com', expected: true, desc: 'Valid HTTPS' },
    { url: 'http://example.com', expected: true, desc: 'Valid HTTP' },
    { url: 'javascript:alert(1)', expected: false, desc: 'Block Javascript Protocol' },
    { url: 'vbscript:msgbox', expected: false, desc: 'Block VBScript Protocol' },
    { url: 'data:text/html,bad', expected: false, desc: 'Block Data Protocol' },
    { url: 'ftp://example.com', expected: false, desc: 'Block FTP (default)' },
    { url: 'not-a-url', expected: false, desc: 'Invalid URL String' },
    { url: '', expected: false, desc: 'Empty String' },
    { url: 'mailto:user@example.com', expected: true, protocols: ['mailto:'], desc: 'Allow Mailto when specified' },
    { url: 'https://google.com', expected: false, protocols: ['http:'], desc: 'Strict Protocol (HTTP only)' },
];

tests.forEach(t => {
    const result = isValidUrl(t.url, t.protocols);
    assert(result === t.expected, `${t.desc} (${t.url}) -> ${result}`);
});

console.log(`\nResults: ${passed} Passed, ${failed} Failed`);

if (failed > 0) process.exit(1);
