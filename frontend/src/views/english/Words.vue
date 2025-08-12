<template>
  <div class="page-container">
    <div class="toolbar">
      <el-input v-model="localQuery.search" placeholder="搜索单词/释义" clearable style="max-width: 280px" @keyup.enter="handleSearch" />
      <el-select v-model="localQuery.difficulty" placeholder="难度" clearable style="width: 140px" class="ml8">
        <el-option label="全部" value="" />
        <el-option label="简单" value="easy" />
        <el-option label="一般" value="medium" />
        <el-option label="困难" value="hard" />
      </el-select>
      <el-button type="primary" class="ml8" @click="handleSearch">查询</el-button>
    </div>

    <el-table :data="englishStore.words" v-loading="englishStore.wordsLoading" stripe style="width: 100%">
      <el-table-column prop="word" label="单词" min-width="140" />
      <el-table-column prop="phonetic" label="音标" min-width="120" />
      <el-table-column prop="part_of_speech" label="词性" width="110" />
      <el-table-column prop="definition" label="释义" min-width="260" show-overflow-tooltip />
      <el-table-column prop="difficulty_level" label="难度" width="110" />
      <el-table-column prop="source_api" label="来源" width="140" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="goDetail(row)">详情</el-button>
          <el-button size="small" type="success" @click="startReview(row)">复习</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="total, prev, pager, next, jumper"
        :total="englishStore.wordsPagination.total"
        :page-size="englishStore.wordsPagination.pageSize"
        :current-page="englishStore.wordsPagination.page"
        @current-change="handlePageChange"
      />
    </div>
  </div>
  
  <el-dialog v-model="dialogVisible" title="待复习单词" width="640px">
    <el-table :data="dueList" v-loading="dueLoading" size="small">
      <el-table-column prop="word.word" label="单词" width="160" />
      <el-table-column prop="word.definition" label="释义" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button-group>
            <el-button size="small" @click="submitReview(row, 2)">困难</el-button>
            <el-button size="small" type="primary" @click="submitReview(row, 3)">一般</el-button>
            <el-button size="small" type="success" @click="submitReview(row, 5)">简单</el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-button @click="dialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
  
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEnglishStore } from '@/stores/english'
import { englishAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

const router = useRouter()
const englishStore = useEnglishStore()

const localQuery = reactive({
  search: '',
  difficulty: ''
})

const fetchList = async () => {
  await englishStore.fetchWords({
    search: localQuery.search,
    difficulty: localQuery.difficulty
  })
}

const handleSearch = () => {
  englishStore.wordsPagination.page = 1
  fetchList()
}

const handlePageChange = (page) => {
  englishStore.wordsPagination.page = page
  fetchList()
}

const goDetail = (row) => {
  router.push(`/english/words/${row.id}`)
}

onMounted(() => {
  fetchList()
})

// 复习逻辑
const dialogVisible = ref(false)
const dueList = ref([])
const dueLoading = ref(false)

const startReview = async () => {
  dialogVisible.value = true
  dueLoading.value = true
  try {
    const resp = await englishAPI.getDueReviews()
    dueList.value = resp?.results || resp?.data || []
  } finally {
    dueLoading.value = false
  }
}

const submitReview = async (progressRow, quality) => {
  try {
    await englishAPI.reviewProgress(progressRow.id, { quality })
    ElMessage.success('打卡成功')
    // 移除已复习项
    dueList.value = dueList.value.filter(i => i.id !== progressRow.id)
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.page-container { padding: 16px; }
.toolbar { margin-bottom: 12px; display: flex; align-items: center; }
.ml8 { margin-left: 8px; }
.pager { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>


