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

// State
const data = ref([])
const loading = ref(true)
const searchQuery = ref('')
const editingId = ref(null)
const editForm = ref({})
const showCreateModal = ref(false)
const createForm = ref({})

// Supabase client holder
let supabase = null

// Initialize Supabase and Fetch data
const initAndFetch = async () => {
    loading.value = true
    try {
        const supabaseUrl = import.meta.env.SUPABASE_URL
        const supabaseKey = import.meta.env.SUPABASE_KEY

        if (!supabaseUrl || !supabaseKey) {
            throw new Error('Supabase configuration missing')
        }

        supabase = createClient(supabaseUrl, supabaseKey)

        let query = supabase
            .from(props.tableName)
            .select('*')

        // Check if sort column exists in columns or is default
        query = query.order(props.defaultSort, { ascending: false })

        const { data: result, error } = await query

        if (error) throw error
        data.value = result
    } catch (e) {
        console.error('Error fetching data:', e)
        // Only alert if it's not a missing config error during SSG (though this runs onMounted)
        if (supabase) {
             alert('加载数据失败: ' + e.message)
        }
    } finally {
        loading.value = false
    }
}

onMounted(initAndFetch)

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
    if (!supabase) return
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
    } catch (e) {
        console.error('Error saving:', e)
        alert('保存失败: ' + e.message)
    }
}

const deleteItem = async (id) => {
    if (!supabase) return
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
    if (!supabase) return
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

// Create Actions
const startCreate = () => {
    createForm.value = {}
    // Initialize boolean fields to false or defaults if needed
    props.columns.forEach(col => {
        if (col.type === 'boolean') {
            createForm.value[col.key] = false
        }
    })
    showCreateModal.value = true
}

const cancelCreate = () => {
    showCreateModal.value = false
    createForm.value = {}
}

const saveCreate = async () => {
    if (!supabase) return
    try {
        const { data: newItem, error } = await supabase
            .from(props.tableName)
            .insert([createForm.value])
            .select()
            .single()

        if (error) throw error

        if (newItem) {
            data.value.unshift(newItem)
        }

        showCreateModal.value = false
        createForm.value = {}
    } catch (e) {
        console.error('Error creating:', e)
        alert('创建失败: ' + e.message)
    }
}
</script>

<template>
    <div class="data-manager">
        <!-- Toolbar -->
        <div class="toolbar">
            <div class="left-tools">
                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input v-model="searchQuery" type="text" placeholder="搜索..." class="search-input" />
                </div>
            </div>
            <div class="right-tools">
                <button class="create-btn" @click="startCreate">➕ 新增</button>
                <button class="refresh-btn" @click="initAndFetch">🔄 刷新</button>
            </div>
        </div>

        <!-- Create Modal -->
        <Teleport to="body">
            <div v-if="showCreateModal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>新增记录</h3>
                        <button class="close-btn" @click="cancelCreate">✕</button>
                    </div>
                    <div class="modal-body">
                        <div v-for="col in columns" :key="col.key" class="form-group">
                            <template v-if="col.editable">
                                <label>{{ col.label }}</label>
                                <input v-if="col.type === 'text' || col.type === 'link'"
                                    v-model="createForm[col.key]" type="text" class="form-input" />
                                <textarea v-else-if="col.type === 'textarea'"
                                    v-model="createForm[col.key]" class="form-input" rows="3"></textarea>
                                <div v-else-if="col.type === 'boolean'" class="checkbox-group">
                                    <input type="checkbox" v-model="createForm[col.key]" />
                                    <span>{{ createForm[col.key] ? '是' : '否' }}</span>
                                </div>
                                <!-- Date is typically auto-generated, so skipping unless editable -->
                                <input v-else-if="col.type === 'date'"
                                    v-model="createForm[col.key]" type="date" class="form-input" />
                            </template>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="cancel-btn" @click="cancelCreate">取消</button>
                        <button class="save-btn" @click="saveCreate">保存</button>
                    </div>
                </div>
            </div>
        </Teleport>

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

.left-tools, .right-tools {
    display: flex;
    align-items: center;
    gap: 12px;
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

.refresh-btn, .create-btn {
    padding: 6px 12px;
    background: var(--vp-c-bg);
    border: 1px solid var(--vp-c-divider);
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: var(--vp-c-text-2);
}

.create-btn {
    background: var(--vp-c-brand);
    color: white;
    border: none;
}

.create-btn:hover {
    background: var(--vp-c-brand-dark);
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

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: var(--vp-c-bg);
    border-radius: 8px;
    width: 500px;
    max-width: 90%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--vp-c-divider);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.close-btn {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--vp-c-text-2);
}

.modal-body {
    padding: 24px;
    overflow-y: auto;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: var(--vp-c-text-2);
}

.form-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 4px;
    background: var(--vp-c-bg-alt);
    color: var(--vp-c-text-1);
    font-size: 14px;
}

.form-input:focus {
    outline: none;
    border-color: var(--vp-c-brand);
}

.checkbox-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.modal-footer {
    padding: 16px 24px;
    border-top: 1px solid var(--vp-c-divider);
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.modal-footer .save-btn {
    padding: 8px 16px;
    font-size: 14px;
}

.modal-footer .cancel-btn {
    padding: 8px 16px;
    font-size: 14px;
}
</style>
