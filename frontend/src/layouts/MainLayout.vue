<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo" @click="$router.push('/')">
        <img src="/vite.svg" alt="logo" class="logo-img" />
        <span v-show="!isCollapse" class="logo-text">LifeHub</span>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="$route.path"
          router
          :collapse="isCollapse"
          background-color="#1d1e1f"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          class="sidebar-menu"
        >
          <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar || undefined">
                {{ userStore.user?.nickname?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.user?.nickname || userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const menuItems = [
  { path: '/dashboard', title: '仪表盘', icon: 'Odometer' },
  { path: '/finance', title: '财务管理', icon: 'Wallet' },
  { path: '/health', title: '健康管理', icon: 'FirstAidKit' },
  { path: '/exercise', title: '运动记录', icon: 'Trophy' },
  { path: '/diet', title: '饮食管理', icon: 'Coffee' },
  { path: '/todo', title: '待办事项', icon: 'Finished' },
  { path: '/notes', title: '笔记管理', icon: 'Notebook' },
  { path: '/habits', title: '习惯追踪', icon: 'AlarmClock' },
  { path: '/reading', title: '阅读管理', icon: 'Reading' },
  { path: '/experiences', title: '人生经历', icon: 'MapLocation' },
  { path: '/contacts', title: '联系人', icon: 'User' },
  { path: '/passwords', title: '密码管理', icon: 'Lock' },
  { path: '/goals', title: '目标管理', icon: 'Flag' },
]

function handleCommand(cmd) {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (cmd === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #1d1e1f;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);

  .logo-img {
    width: 32px;
    height: 32px;
  }

  .logo-text {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #409EFF, #67C23A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    white-space: nowrap;
  }
}

.sidebar-menu {
  border-right: none;

  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    margin: 2px 8px;
    border-radius: 8px;

    &.is-active {
      background: rgba(64, 158, 255, 0.15) !important;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.05) !important;
    }
  }
}

.header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 0 20px;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #606266;

    &:hover {
      color: #409EFF;
    }
  }
}

.header-right {
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;

    .username {
      font-size: 14px;
      color: #303133;
    }
  }
}

.main-content {
  background: #f0f2f5;
  overflow-y: auto;
}
</style>
