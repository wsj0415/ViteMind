<script setup>
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const feeds = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingFeed = ref(null)

// Form data
const form = ref({
    name: '',
    url: '',
    category: 'News',
    is_active: true,
    include_keywords: '',
    exclude_keywords: ''
})

const categories = ['News', 'Dev', 'New', 'Deal']

const fetchFeeds = async () => {
    try {
        loading.value = true
        const { data, error } = await supabase
            .from('rss_feeds')
            .select('*')
            .order('created_at', { ascending: false })

        if (error) throw error
        feeds.value = data
    } catch (e) {
        alert('Error fetching feeds: ' + e.message)
    } finally {
        loading.value = false
    }
}

const openModal = (feed = null) => {
    if (feed) {
        editingFeed.value = feed
        form.value = { ...feed }
    } else {
        editingFeed.value = null
        form.value = {
            name: '',
            url: '',
            category: 'News',
            is_active: true,
            include_keywords: '',
            exclude_keywords: ''
        }
    }
    showModal.value = true
}

const saveFeed = async () => {
    try {
        const dataToSave = { ...form.value }

        // Clean up empty strings to null if needed, or keep as empty string
        if (!dataToSave.include_keywords) dataToSave.include_keywords = null
        if (!dataToSave.exclude_keywords) dataToSave.exclude_keywords = null

        let error
        if (editingFeed.value) {
            const { error: updateError } = await supabase
                .from('rss_feeds')
                .update(dataToSave)
                .eq('id', editingFeed.value.id)
            error = updateError
        } else {
            const { error: insertError } = await supabase
                .from('rss_feeds')
                .insert([dataToSave])
            error = insertError
        }

        if (error) throw error

        showModal.value = false
        fetchFeeds()
    } catch (e) {
        alert('Error saving feed: ' + e.message)
    }
}

const deleteFeed = async (id) => {
    if (!confirm('Are you sure you want to delete this feed?')) return

    try {
        const { error } = await supabase
            .from('rss_feeds')
            .delete()
            .eq('id', id)

        if (error) throw error
        fetchFeeds()
    } catch (e) {
        alert('Error deleting feed: ' + e.message)
    }
}

const toggleStatus = async (feed) => {
    try {
        const { error } = await supabase
            .from('rss_feeds')
            .update({ is_active: !feed.is_active })
            .eq('id', feed.id)

        if (error) throw error
        feed.is_active = !feed.is_active
    } catch (e) {
        alert('Error updating status: ' + e.message)
    }
}

onMounted(() => {
    fetchFeeds()
})
</script>

<template>
    <div class="rss-manager">
        <div class="header-actions">
            <h2>RSS Feeds</h2>
            <button class="btn-primary" @click="openModal()">+ Add Feed</button>
        </div>

        <div v-if="loading" class="loading">Loading feeds...</div>

        <div v-else class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Health</th>
                        <th>Keywords (In/Ex)</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="feed in feeds" :key="feed.id" :class="{ inactive: !feed.is_active }">
                        <td>
                            <label class="switch">
                                <input type="checkbox" :checked="feed.is_active" @change="toggleStatus(feed)">
                                <span class="slider round"></span>
                            </label>
                        </td>
                        <td>
                            <div class="feed-name">{{ feed.name }}</div>
                            <div class="feed-url">{{ feed.url }}</div>
                        </td>
                        <td><span class="badge">{{ feed.category }}</span></td>
                        <td>
                            <div v-if="feed.error_message" class="status-error" :title="feed.error_message">
                                🔴 Error
                            </div>
                            <div v-else-if="feed.last_success_at" class="status-ok"
                                :title="'Last success: ' + new Date(feed.last_success_at).toLocaleString()">
                                🟢 OK
                            </div>
                            <div v-else class="status-unknown">
                                ⚪ Pending
                            </div>
                        </td>
                        <td class="keywords-cell">
                            <div v-if="feed.include_keywords" class="kw-in">IN: {{ feed.include_keywords }}</div>
                            <div v-if="feed.exclude_keywords" class="kw-ex">EX: {{ feed.exclude_keywords }}</div>
                        </td>
                        <td>
                            <button class="btn-text" @click="openModal(feed)">Edit</button>
                            <button class="btn-text danger" @click="deleteFeed(feed.id)">Delete</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Modal -->
        <div v-if="showModal" class="modal-overlay" @click="showModal = false">
            <div class="modal-content" @click.stop>
                <h3>{{ editingFeed ? 'Edit Feed' : 'Add New Feed' }}</h3>

                <div class="form-group">
                    <label>Name</label>
                    <input v-model="form.name" type="text" placeholder="e.g. Hacker News AI" required>
                </div>

                <div class="form-group">
                    <label>URL</label>
                    <input v-model="form.url" type="url" placeholder="https://..." required>
                </div>

                <div class="form-group">
                    <label>Category</label>
                    <select v-model="form.category">
                        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Include Keywords (Optional)</label>
                    <input v-model="form.include_keywords" type="text"
                        placeholder="e.g. AI, LLM, GPT (comma separated)">
                    <small>Only fetch articles containing these words.</small>
                </div>

                <div class="form-group">
                    <label>Exclude Keywords (Optional)</label>
                    <input v-model="form.exclude_keywords" type="text" placeholder="e.g. Crypto, NFT (comma separated)">
                    <small>Skip articles containing these words.</small>
                </div>

                <div class="modal-actions">
                    <button class="btn-text" @click="showModal = false">Cancel</button>
                    <button class="btn-primary" @click="saveFeed">Save</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.rss-manager {
    font-family: var(--vp-font-family-base);
}

.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.table-container {
    overflow-x: auto;
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th,
td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--vp-c-divider);
}

th {
    background: var(--vp-c-bg-soft);
    font-weight: 600;
}

.feed-url {
    font-size: 12px;
    color: var(--vp-c-text-2);
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.badge {
    background: var(--vp-c-brand-soft);
    color: var(--vp-c-brand);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
}

.status-ok {
    color: #10b981;
    font-weight: 500;
}

.status-error {
    color: #ef4444;
    font-weight: 500;
    cursor: help;
}

.status-unknown {
    color: var(--vp-c-text-2);
}

.keywords-cell {
    font-size: 12px;
    max-width: 200px;
}

.kw-in {
    color: #10b981;
}

.kw-ex {
    color: #ef4444;
}

.btn-primary {
    background: var(--vp-c-brand);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-text {
    background: none;
    border: none;
    color: var(--vp-c-text-1);
    cursor: pointer;
    margin-right: 8px;
}

.btn-text.danger {
    color: #ef4444;
}

/* Switch */
.switch {
    position: relative;
    display: inline-block;
    width: 34px;
    height: 20px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
}

.slider:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: .4s;
}

input:checked+.slider {
    background-color: var(--vp-c-brand);
}

input:checked+.slider:before {
    transform: translateX(14px);
}

.slider.round {
    border-radius: 34px;
}

.slider.round:before {
    border-radius: 50%;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
}

.modal-content {
    background: var(--vp-c-bg);
    padding: 24px;
    border-radius: 8px;
    width: 100%;
    max-width: 500px;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 8px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 4px;
    background: var(--vp-c-bg);
    color: var(--vp-c-text-1);
}

.form-group small {
    display: block;
    margin-top: 4px;
    color: var(--vp-c-text-2);
    font-size: 12px;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
}
</style>
