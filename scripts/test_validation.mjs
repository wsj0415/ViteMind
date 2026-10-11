
import { isValidUrl } from '../docs/.vitepress/theme/utils/validation.js';

const testCases = [
    { input: 'https://example.com', expected: true, desc: 'HTTPS URL' },
    { input: 'http://example.com', expected: true, desc: 'HTTP URL' },
    { input: 'javascript:alert(1)', expected: false, desc: 'JavaScript URI (XSS)' },
    { input: 'data:text/html,<html>', expected: false, desc: 'Data URI' },
    { input: 'ftp://example.com', expected: false, desc: 'FTP URL (default)' },
    { input: 'mailto:user@example.com', expected: false, desc: 'Mailto URL (default)' },
    { input: 'not a url', expected: false, desc: 'Invalid String' },
    { input: '', expected: false, desc: 'Empty String' },
];

let errors = 0;

console.log("Running Validation Tests...");

testCases.forEach(tc => {
    const result = isValidUrl(tc.input);
    if (result !== tc.expected) {
        console.error(`[FAIL] ${tc.desc}: Input '${tc.input}' -> Expected ${tc.expected}, Got ${result}`);
        errors++;
    } else {
        console.log(`[PASS] ${tc.desc}`);
    }
});

// Test custom protocols
const mailtoResult = isValidUrl('mailto:test@test.com', ['mailto:']);
if (mailtoResult === true) {
     console.log(`[PASS] Custom Protocol (mailto)`);
} else {
     console.error(`[FAIL] Custom Protocol (mailto) -> Expected true, Got ${mailtoResult}`);
     errors++;
}

if (errors === 0) {
    console.log("\nAll tests passed!");
    process.exit(0);
} else {
    console.error(`\n${errors} tests failed.`);
    process.exit(1);
}
