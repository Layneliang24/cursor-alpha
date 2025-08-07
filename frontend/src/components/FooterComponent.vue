<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-left">
        <span class="brand">Alpha 技术平台</span>
        <span class="separator">|</span>
        <span class="slogan">分享技术，共同成长</span>
      </div>
      <div class="footer-right">
        <span class="copyright">&copy; 2024 All rights reserved</span>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'FooterComponent'
}
</script>

<style scoped>
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid #e4e7ed;
  padding: 8px 0;
  font-size: 12px;
  z-index: 100;
  height: 40px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.brand {
  font-weight: 600;
  color: #333;
}

.separator {
  color: #ccc;
}

.slogan {
  color: #888;
}

.footer-right {
  color: #999;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 4px;
    padding: 4px 20px;
  }
  
  .footer {
    height: 50px;
  }
  
  .footer-left {
    gap: 4px;
  }
}
</style> 