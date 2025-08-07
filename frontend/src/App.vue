<template>
  <div id="app">
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
    
    // 在登录和注册页面隐藏侧边栏
    const showSidebar = computed(() => {
      return !['/login', '/register'].includes(route.path)
    })
    
    return {
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
</style>