# Deploy Center 贡献指南

感谢你对 `Deploy Center` 项目的关注与支持！

以下是代码提交与协作的规范，欢迎提交 PR，请遵循以下格式进行协作。

---

##  提交信息规范（Commit Message）

请使用约定式提交（Conventional Commits）风格，格式如下：

```
<类型>: <简要描述>
```

### 常用类型说明：

| 类型     | 说明                     |
|----------|--------------------------|
| feat     | 新功能、新模块           |
| fix      | 修复 Bug                 |
| refactor | 重构（不影响功能）       |
| docs     | 文档变更                 |
| style    | 代码格式（如空格、缩进）调整 |
| chore    | 构建/脚手架/依赖更新     |
| test     | 添加或修改测试           |
| perf     | 性能优化                 |

### 示例：

```bash
feat: 实现定时部署功能
fix: 修复 xxx 的问题
docs: 新增 xxx 文档
```

---

##  合作流程建议

1. Fork 本项目并创建新分支：

```bash
git checkout -b feat/your-feature-name
```

2. 遵循 commit message 规范提交代码

3. 提交 PR 时：

- 填写清晰的标题与描述
- 可附带截图 / 说明链接 / 复现方式
- 如有相关 issue，请关联

---

##  建议关注的内容

- 代码整洁与命名一致性
- 避免大体量混合提交（建议小步提交）
- 中文文档同步（如文档调整）

---

如有任何问题或建议，欢迎提 Issue 或 Discussions！
