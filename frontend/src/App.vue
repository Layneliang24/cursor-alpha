<template>
  <div id="app">
    <!-- 登录注册页面的简洁布局 -->
    <div v-if="isAuthPage" class="auth-layout">
      <router-view />
    </div>
    
    <!-- 普通页面的完整布局 -->
    <div v-else>
      <!-- 顶部导航栏 -->
      <TopNavBar />
      
      <!-- 主体布局 -->
      <div class="d-flex">
        <!-- 侧边菜单栏 -->
        <SideMenu v-if="showSidebar" />
        
        <!-- 主内容区域 -->
        <main class="flex-grow-1 p-4" :class="{ 'container-fluid': showSidebar, 'container': !showSidebar }">
          <router-view />
        </main>
      </div>
      
      <!-- 底部 -->
      <FooterComponent />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TopNavBar from '@/components/TopNavBar.vue'
import SideMenu from '@/components/SideMenu.vue'
import FooterComponent from '@/components/FooterComponent.vue'

export default {
  name: 'App',
  components: {
    TopNavBar,
    SideMenu,
    FooterComponent
  },
  setup() {
    const route = useRoute()
    
    // 判断是否为认证页面
    const isAuthPage = computed(() => {
      return ['/login', '/register'].includes(route.path)
    })
    
    // 在登录和注册页面隐藏侧边栏
    const showSidebar = computed(() => {
      return !isAuthPage.value
    })
    
    return {
      isAuthPage,
      showSidebar
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

body {
  margin: 0;
  padding: 0;
  background-color: #f8f9fa;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>