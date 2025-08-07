<template>
  <div class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h4>Alpha 技术共享平台</h4>
        <p>分享技术，共同成长</p>
      </div>
      <div class="footer-section">
        <h4>快速链接</h4>
        <ul>
          <li><router-link to="/">首页</router-link></li>
          <li><router-link to="/articles">文章</router-link></li>
          <li><router-link to="/categories">分类</router-link></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4>联系我们</h4>
        <p>邮箱: contact@alpha.com</p>
        <p>GitHub: <a href="#" target="_blank">Alpha Platform</a></p>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2024 Alpha 技术共享平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FooterComponent'
}
</script>

<style scoped>
.footer {
  background-color: #f5f7fa;
  padding: 20px 0;
}

.footer-content {
  display: flex;
  justify-content: space-around;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-section {
  flex: 1;
  margin: 0 20px;
}

.footer-section h4 {
  color: #303133;
  margin-bottom: 10px;
}

.footer-section p {
  color: #606266;
  margin: 5px 0;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin: 5px 0;
}

.footer-section ul li a {
  color: #606266;
  text-decoration: none;
}

.footer-section ul li a:hover {
  color: #409eff;
}

.footer-bottom {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  color: #909399;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
  }
  
  .footer-section {
    margin: 10px 0;
  }
}
</style> 