
/**
 * Validates if a string is a valid URL with allowed protocols.
 * @param {string} string - The string to validate
 * @param {Array<string>} protocols - Allowed protocols (default: http, https)
 * @returns {boolean} - True if valid, false otherwise
 */
export const isValidUrl = (string, protocols = ['http:', 'https:']) => {
    try {
        const url = new URL(string)
        return protocols.includes(url.protocol)
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
            if (!isValidUrl(value, ['http:', 'https:', 'mailto:'])) {
                try {
                    new URL(value)
                    errors[col.key] = '不允许的 URL 协议'
                } catch {
                    errors[col.key] = '必须是有效的 URL'
                }
                isValid = false
            }
        }
    }
    return isValid
}
