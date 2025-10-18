# Qwen3 Dashboard 使用指南

## 📊 快速开始

### 生成Dashboard

```bash
python agents-toolchain/dashboard/generate_dashboard.py
```

### 查看Dashboard

在浏览器中打开：
```
benchmarks/models/qwen3_dashboard.html
```

---

## 🎯 功能特性

### 1. 多模态模型支持

Dashboard支持4种模型类型，点击顶部按钮切换：

- **LLM (Text)** - 纯文本语言模型
  - Qwen3-8B, Qwen3-30B-A3B, Qwen3-235B-A22B
  - 20个benchmark，涵盖知识、数学、编程、逻辑等
  
- **VLM (Vision)** - 视觉-语言模型
  - Qwen3-VL-8B, Qwen3-VL-30B-A3B, Qwen3-VL-235B-A22B
  - 45个benchmark，涵盖视觉理解、OCR、空间推理等
  
- **ALM (Audio)** - 音频-语言模型
  - Qwen-Audio
  - 13个benchmark，涵盖语音识别、音频理解等
  
- **Omni (Multimodal)** - 全模态模型
  - Qwen3-Omni-30B-A3B
  - 12个benchmark，涵盖语音对话、多模态理解等

### 2. 智能分类

每种模型类型的benchmarks都按能力自动分类：

**LLM分类**:
- Knowledge & Reasoning (知识与推理)
- Mathematics (数学)
- Coding (编程)
- Logic (逻辑)
- Instruction Following (指令跟随)
- Writing (写作)
- Function Calling (函数调用)
- Multilingual (多语言)

**VLM分类**:
- Visual Understanding (视觉理解)
- OCR & Documents (文档识别)
- Math & Science (数学与科学)
- Spatial Reasoning (空间推理)
- Video Understanding (视频理解)
- GUI & Coding (图形界面与编码)

### 3. 可视化图表

#### 能力雷达图
- 显示各能力维度的平均表现
- 直观对比优势领域

#### Top Benchmarks柱状图
- 展示得分最高的15项benchmark
- 渐变色柱状图，易于识别

### 4. 详细数据表格

- 完整benchmark列表
- 包含指标类型、分数、数据来源、描述
- 支持分类筛选

---

## 🔄 数据更新流程

Dashboard每次运行时自动读取最新数据：

1. **修改benchmark数据**
   ```
   benchmarks/models/qwen3_text.json
   benchmarks/models/qwen3_vl.json
   benchmarks/models/qwen3_audio.json
   benchmarks/models/qwen3_omni.json
   ```

2. **重新生成dashboard**
   ```bash
   python agents-toolchain/dashboard/generate_dashboard.py
   ```

3. **刷新浏览器** 查看更新

---

## 📁 项目结构

```
agents-toolchain/dashboard/
├── generate_dashboard.py    # 主生成脚本
├── test_dashboard.py         # 验证脚本
├── README.md                 # 英文文档
├── USAGE_CN.md              # 本文档（中文使用指南）
├── templates/                # 预留：Jinja2模板
└── static/                   # 预留：静态资源

benchmarks/models/
├── qwen3_text.json          # LLM数据源
├── qwen3_vl.json            # VLM数据源
├── qwen3_audio.json         # ALM数据源
├── qwen3_omni.json          # Omni数据源
└── qwen3_dashboard.html     # 生成的Dashboard
```

---

## 🛠️ 高级定制

### 添加新模型类型

1. 创建数据文件：`benchmarks/models/qwen3_xxx.json`

2. 修改 `generate_dashboard.py`：
   ```python
   def aggregate_xxx_data(self):
       filepath = BENCHMARKS_DIR / "qwen3_xxx.json"
       data = self.load_json_file(filepath)
       # ... 处理逻辑
   ```

3. 在 `generate()` 方法中调用：
   ```python
   self.aggregate_xxx_data()
   ```

4. 更新HTML模板添加按钮

### 修改分类规则

编辑 `_categorize_benchmarks()` 方法中的 `category_keywords` 字典：

```python
category_keywords = {
    "新分类名称": ["关键词1", "关键词2"],
    # ...
}
```

### 自定义样式

修改 `generate_html()` 方法中的 `<style>` 部分。

---

## 📊 统计信息

当前Dashboard包含：
- **90个benchmarks** (总计)
- **4种模型类型**
- **10+能力分类**
- **8个模型变体**

---

## 🔗 参考资料

- [Qwen3 技术报告](https://arxiv.org/abs/2505.09388)
- [Qwen3-VL Collection](https://huggingface.co/collections/Qwen/qwen3-vl-68d2a7c1b8a8afce4ebd2dbe)
- [Qwen-Audio Repository](https://github.com/QwenLM/Qwen-Audio)
- [Qwen3-Omni 技术报告](https://arxiv.org/abs/2509.17765)
- [AgentBench](https://github.com/THUDM/AgentBench)

---

## ⚠️ 注意事项

1. **浏览器兼容性**: 需要现代浏览器支持（Chrome 90+, Firefox 88+, Safari 14+）
2. **文件大小**: Dashboard约100KB，包含完整数据和样式
3. **离线可用**: 依赖CDN资源（Vue.js, ECharts），需要网络连接
4. **数据完整性**: 确保JSON文件格式正确，可用 `test_dashboard.py` 验证

---

## 🐛 故障排除

### Dashboard无法显示

1. 检查浏览器控制台错误
2. 验证JSON数据格式：
   ```bash
   python -m json.tool benchmarks/models/qwen3_text.json
   ```

### 图表不显示

1. 确认网络连接（CDN资源）
2. 检查浏览器JavaScript是否启用

### 数据未更新

1. 确认修改了正确的JSON文件
2. 重新运行生成脚本
3. 强制刷新浏览器（Ctrl+F5）

---

## 📝 许可证

遵循主仓库许可证 (Apache 2.0)
