
import { isValidUrl } from '../docs/.vitepress/theme/utils/validation.js'

console.log("Running validation tests...")

const cases = [
    { input: "https://google.com", expected: true },
    { input: "http://insecure.com", expected: true },
    { input: "javascript:alert(1)", expected: false },
    { input: "JAVAscript:alert(1)", expected: false }, // Case insensitive check implicitly handled by URL API? URL protocol is lowercased.
    { input: "ftp://files.com", expected: false },
    { input: "mailto:someone@example.com", expected: false }, // Default protocols don't include mailto
    { input: "not-a-url", expected: false },
    { input: "", expected: false }
]

let passed = 0
let failed = 0

cases.forEach(({ input, expected }) => {
    const result = isValidUrl(input)
    if (result === expected) {
        passed++
    } else {
        console.error(`✗ [${input}] -> ${result} (Expected: ${expected})`)
        failed++
    }
})

// Test with custom protocols
const resultMailto = isValidUrl("mailto:test@test.com", ["mailto:", "http:", "https:"])
if (resultMailto === true) {
    passed++
} else {
    console.error(`✗ [mailto:test@test.com] -> ${resultMailto} (Expected: true with custom protocol)`)
    failed++
}

console.log(`\nTests Completed. Passed: ${passed}, Failed: ${failed}`)

if (failed > 0) process.exit(1)
