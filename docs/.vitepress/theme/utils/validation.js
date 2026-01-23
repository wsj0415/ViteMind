
/**
 * Validates if a string is a safe URL.
 * @param {string} string - The URL string to validate
 * @param {Array<string>} [allowedProtocols=['http:', 'https:']] - List of allowed protocols
 * @returns {boolean} - True if valid and safe
 */
export const isValidUrl = (string, allowedProtocols = ['http:', 'https:']) => {
    try {
        const url = new URL(string)
        return allowedProtocols.includes(url.protocol)
    } catch (_) {
        return false
    }
}

/**
 * Validates a form based on column definitions.
 * Extracted from DataManager.vue for testability and reuse.
 *
 * @param {Object} form - The data object to validate
 * @param {Array} columns - The column definitions
 * @param {Object} errors - The errors object to populate (mutated)
 * @returns {boolean} - True if valid, false otherwise
 */
export const validateForm = (form, columns, errors) => {
    // Clear previous errors if needed, but here we expect caller to handle clearing or we just overwrite keys
    // In DataManager.vue: errors.value = {} is done before calling this.
    // But since we mutate errors object, we just add keys.

    let isValid = true

    for (const col of columns) {
        if (!col.editable) continue

        const value = form[col.key]

        // Check Required
        if (col.validation?.required) {
            const isEmpty = value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)
            if (isEmpty) {
                errors[col.key] = `${col.label} 是必填项`
                isValid = false
            }
        }

        // Check URL
        if (col.validation?.type === 'url' && value) {
            // Security: Prevent javascript: and other unsafe protocols
            const allowedProtocols = ['http:', 'https:', 'mailto:']

            if (!isValidUrl(value, allowedProtocols)) {
                // Determine error message based on failure type (invalid format vs protocol)
                // However, isValidUrl returns generic boolean. We stick to generic error or try to differentiate.
                // The original code had two error messages. Let's try to preserve that if possible.
                try {
                    const u = new URL(value) // Check if valid URL structure first
                    if (!allowedProtocols.includes(u.protocol)) {
                        errors[col.key] = '不允许的 URL 协议'
                    } else {
                        // Should not happen if isValidUrl returns true
                         errors[col.key] = '必须是有效的 URL'
                    }
                } catch {
                     errors[col.key] = '必须是有效的 URL'
                }
                isValid = false
            }
        }
    }
    return isValid
}
