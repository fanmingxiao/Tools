# SVW Copilot Word 插件

这是一个 Microsoft Word 侧边栏插件，将 SVW Copilot AI 助手集成到 Word 中。

## 功能特性

- 🎯 **自定义选项卡**: 在 Word Ribbon 中添加名为 "AI助手" 的独立选项卡
- 🖱️ **一键启动**: 点击 "SVW Copilot" 按钮即可打开侧边栏
- 🌐 **网页集成**: 加载 `https://copilot.csvw.com/embedded/page/word/src/taskpane/taskpane.html` 网页
- 📐 **侧边栏模式**: 以任务窗格（Taskpane）形式展示，方便与文档并排使用

## 安装方法

### 方法1: 通过 Office 商店（如果已发布）
1. 打开 Word
2. 点击 "插入" > "获取加载项"
3. 搜索 "SVW Copilot"
4. 点击 "添加"

### 方法2: 旁加载（Sideload）- 开发测试

#### Windows 桌面版 Word:
1. 将 `manifest.xml` 文件复制到一个共享文件夹或本地目录
2. 打开 Word，点击 "文件" > "选项" > "信任中心" > "信任中心设置"
3. 选择 "受信任的加载项目录"
4. 点击 "添加新目录"，输入 manifest.xml 所在文件夹的路径
5. 勾选 "添加到目录中的加载项"
6. 点击 "确定" 保存设置
7. 重启 Word

#### Word Online:
1. 打开 [Word Online](https://word.new)
2. 点击 "插入" > "Office 加载项" > "管理我的加载项"
3. 点击 "上传我的加载项"
4. 选择 `manifest.xml` 文件上传

#### Mac 版 Word:
1. 打开终端，执行：
   ```bash
   cp -r SVW-Copilot-Word-Addin ~/Library/Containers/com.microsoft.Word/Data/Documents/wef/
   ```
2. 重启 Word

## 使用方法

1. 安装插件后，在 Word Ribbon 中会出现 **"AI助手"** 选项卡
2. 切换到 "AI助手" 选项卡
3. 点击 **"SVW Copilot"** 按钮
4. 右侧会打开侧边栏，加载 AI 助手页面

## 文件说明

```
SVW-Copilot-Word-Addin/
├── manifest.xml    # 插件清单文件（核心配置文件）
└── README.md       # 使用说明
```

## 技术规格

- **插件类型**: Office 任务窗格插件（Task Pane Add-in）
- **支持平台**: Windows, Mac, Word Online
- **最低 Office 版本**: Office 2016 或 Office 365
- **权限级别**: ReadWriteDocument

## 自定义修改

如需修改插件配置，编辑 `manifest.xml` 文件：

- **修改选项卡名称**: 查找 `SVW.AIAssistant.Tab.Label` 字符串资源
- **修改按钮文本**: 查找 `SVW.Copilot.Button.Label` 字符串资源
- **修改目标网址**: 查找 `Taskpane.Url` URL 资源
- **修改图标**: 更新 `bt:Images` 中的图片 URL

## 注意事项

1. 此插件需要网络连接才能加载远程网页
2. 首次加载可能需要几秒钟时间
3. 如果网址变更，需要更新 `manifest.xml` 中的 `Taskpane.Url`
4. 企业部署时可能需要 IT 管理员配置受信任目录

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 插件不显示 | 检查 manifest.xml 路径是否正确，重启 Word |
| 侧边栏空白 | 检查网络连接，确认目标网址可访问 |
| 安装失败 | 确认使用 HTTPS 协议，检查 XML 格式 |
| 按钮灰色不可用 | 确认文档已保存，检查权限设置 |

## 参考资料

- [Office 加载项文档](https://docs.microsoft.com/zh-cn/office/dev/add-ins/)
- [Word 加载项开发指南](https://docs.microsoft.com/zh-cn/office/dev/add-ins/word/)
