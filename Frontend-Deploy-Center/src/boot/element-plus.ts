// src/boot/element-plus.ts
import { boot } from 'quasar/wrappers';
import ElementPlus from 'element-plus';
import 'element-plus/theme-chalk/index.css';

export default boot(({ app }) => {
  // 使用 Element Plus
  app.use(ElementPlus);
});
