<script setup>
import { ref, onMounted, computed } from 'vue'
import { createClient } from '@supabase/supabase-js'

const props = defineProps({
    tableName: {
        type: String,
        required: true
    },
    columns: {
        type: Array,
        required: true
    },
    defaultSort: {
        type: String,
        default: 'created_at'
    }
})

const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const data = ref([])
const loading = ref(true)
const searchQuery = ref('')
const editingId = ref(null)
const editForm = ref({})

// Fetch data
const fetchData = async () => {
    loading.value = true
    try {
        let query = supabase
            .from(props.tableName)
            .select('*')

        // Check if sort column exists in columns or is default
        // For simplicity, we just try to sort by defaultSort descending
        query = query.order(props.defaultSort, { ascending: false })

        const { data: result, error } = await query

        if (error) throw error
        data.value = result
    } catch (e) {
        console.error('Error fetching data:', e)
        alert('加载数据失败: ' + e.message)
    } finally {
        loading.value = false
    }
}

onMounted(fetchData)

// Filtered data
const filteredData = computed(() => {
    if (!searchQuery.value) return data.value

    const query = searchQuery.value.toLowerCase()
    return data.value.filter(item => {
        return Object.values(item).some(val =>
            String(val).toLowerCase().includes(query)
        )
    })
})

// Actions
const startEdit = (item) => {
    editingId.value = item.id
    editForm.value = { ...item }
}

const cancelEdit = () => {
    editingId.value = null
    editForm.value = {}
}

const saveEdit = async () => {
    try {
        const { error } = await supabase
            .from(props.tableName)
            .update(editForm.value)
            .eq('id', editingId.value)

        if (error) throw error

        // Update local data
        const index = data.value.findIndex(i => i.id === editingId.value)
        if (index !== -1) {
            data.value[index] = { ...editForm.value }
        }

        editingId.value = null
        // alert('保存成功')
    } catch (e) {
        console.error('Error saving:', e)
        alert('保存失败: ' + e.message)
    }
}

const deleteItem = async (id) => {
    if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) return

    try {
        const { error } = await supabase
            .from(props.tableName)
            .delete()
            .eq('id', id)

        if (error) throw error

        data.value = data.value.filter(i => i.id !== id)
    } catch (e) {
        console.error('Error deleting:', e)
        alert('删除失败: ' + e.message)
    }
}

const toggleBoolean = async (item, field) => {
    try {
        const newValue = !item[field]
        const { error } = await supabase
            .from(props.tableName)
            .update({ [field]: newValue })
            .eq('id', item.id)

        if (error) throw error

        item[field] = newValue
    } catch (e) {
        console.error('Error toggling:', e)
        alert('操作失败: ' + e.message)
    }
}
</script>

<template>
    <div class="data-manager">
        <!-- Toolbar -->
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input v-model="searchQuery" type="text" placeholder="搜索..." class="search-input" />
            </div>
            <button class="refresh-btn" @click="fetchData">🔄 刷新</button>
        </div>

        <!-- Table -->
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
                            {{ col.label }}
                        </th>
                        <th style="width: 120px">操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="loading">
                        <td :colspan="columns.length + 1" class="loading-cell">加载中...</td>
                    </tr>
                    <tr v-else-if="filteredData.length === 0">
                        <td :colspan="columns.length + 1" class="empty-cell">无数据</td>
                    </tr>
                    <tr v-for="item in filteredData" :key="item.id">
                        <template v-if="editingId === item.id">
                            <!-- Edit Mode -->
                            <td v-for="col in columns" :key="col.key">
                                <div v-if="!col.editable" class="readonly-text">
                                    {{ item[col.key] }}
                                </div>
                                <input v-else-if="col.type === 'text' || col.type === 'link'"
                                    v-model="editForm[col.key]" type="text" class="edit-input" />
                                <textarea v-else-if="col.type === 'textarea'" v-model="editForm[col.key]"
                                    class="edit-input" rows="2"></textarea>
                                <div v-else-if="col.type === 'boolean'">
                                    <input type="checkbox" v-model="editForm[col.key]" />
                                </div>
                            </td>
                            <td class="actions-cell">
                                <button class="save-btn" @click="saveEdit">保存</button>
                                <button class="cancel-btn" @click="cancelEdit">取消</button>
                            </td>
                        </template>

                        <template v-else>
                            <!-- View Mode -->
                            <td v-for="col in columns" :key="col.key">
                                <!-- Boolean Toggle -->
                                <div v-if="col.type === 'boolean'" class="bool-cell">
                                    <button class="toggle-switch" :class="{ active: item[col.key] }"
                                        @click="toggleBoolean(item, col.key)">
                                        {{ item[col.key] ? '已通过' : '待审核' }}
                                    </button>
                                </div>

                                <!-- Link -->
                                <a v-else-if="col.type === 'link'" :href="item[col.key]" target="_blank"
                                    class="link-text">
                                    {{ item[col.key] }}
                                </a>

                                <!-- Date -->
                                <span v-else-if="col.type === 'date'" class="date-text">
                                    {{ new Date(item[col.key]).toLocaleDateString() }}
                                </span>

                                <!-- Text -->
                                <div v-else class="text-cell" :title="item[col.key]">
                                    {{ item[col.key] }}
                                </div>
                            </td>
                            <td class="actions-cell">
                                <button class="edit-btn" @click="startEdit(item)">✏️</button>
                                <button class="delete-btn" @click="deleteItem(item.id)">🗑️</button>
                            </td>
                        </template>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.data-manager {
    background: var(--vp-c-bg);
    border-radius: 8px;
    border: 1px solid var(--vp-c-divider);
    overflow: hidden;
}

.toolbar {
    padding: 16px;
    border-bottom: 1px solid var(--vp-c-divider);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--vp-c-bg-alt);
}

.search-box {
    display: flex;
    align-items: center;
    background: var(--vp-c-bg);
    border: 1px solid var(--vp-c-divider);
    border-radius: 6px;
    padding: 6px 12px;
    width: 300px;
}

.search-input {
    border: none;
    background: transparent;
    margin-left: 8px;
    width: 100%;
    font-size: 14px;
    color: var(--vp-c-text-1);
}

.search-input:focus {
    outline: none;
}

.refresh-btn {
    padding: 6px 12px;
    background: var(--vp-c-bg);
    border: 1px solid var(--vp-c-divider);
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: var(--vp-c-text-2);
}

.refresh-btn:hover {
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
}

.table-container {
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.data-table th {
    text-align: left;
    padding: 12px 16px;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-2);
    font-weight: 600;
    border-bottom: 1px solid var(--vp-c-divider);
    white-space: nowrap;
}

.data-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--vp-c-divider);
    color: var(--vp-c-text-1);
    vertical-align: middle;
}

.text-cell {
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.link-text {
    color: var(--vp-c-brand);
    text-decoration: none;
    max-width: 200px;
    display: inline-block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.link-text:hover {
    text-decoration: underline;
}

.date-text {
    color: var(--vp-c-text-3);
    font-size: 13px;
}

.toggle-switch {
    padding: 4px 8px;
    border-radius: 12px;
    border: none;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-3);
    transition: all 0.2s;
}

.toggle-switch.active {
    background: #10b981;
    color: white;
}

.actions-cell {
    display: flex;
    gap: 8px;
}

.edit-btn,
.delete-btn {
    padding: 6px;
    border: none;
    background: transparent;
    cursor: pointer;
    border-radius: 4px;
    font-size: 16px;
}

.edit-btn:hover {
    background: var(--vp-c-brand-soft);
}

.delete-btn:hover {
    background: rgba(239, 68, 68, 0.1);
}

.edit-input {
    width: 100%;
    padding: 6px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 4px;
    background: var(--vp-c-bg);
    color: var(--vp-c-text-1);
    font-size: 13px;
}

.save-btn {
    padding: 4px 8px;
    background: var(--vp-c-brand);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
}

.cancel-btn {
    padding: 4px 8px;
    background: transparent;
    color: var(--vp-c-text-2);
    border: 1px solid var(--vp-c-divider);
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
}

.loading-cell,
.empty-cell {
    text-align: center;
    padding: 40px;
    color: var(--vp-c-text-3);
}
</style>
