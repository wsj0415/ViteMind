
/**
 * Security: Validates if a string is a safe URL with allowed protocols.
 * @param {string} urlStr - The URL string to validate
 * @param {string[]} allowedProtocols - List of allowed protocols (default: http, https)
 * @returns {boolean} - True if valid and safe
 */
export const isValidUrl = (urlStr, allowedProtocols = ['http:', 'https:']) => {
    try {
        const url = new URL(urlStr)
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
            // Admin allows mailto, but public forms might typically stick to http/https
            if (!isValidUrl(value, ['http:', 'https:', 'mailto:'])) {
                errors[col.key] = '无效的 URL 或不允许的协议'
                isValid = false
            }
        }
    }
    return isValid
}
