# 极简计时器 - Android APP

一个简洁优雅的多窗口计时APP，支持正计时和倒计时。

## 功能特性

- ✅ 多独立计时窗口（2列网格布局）
- ✅ 正计时/倒计时双模式
- ✅ 窗口重命名和备注
- ✅ 批量操作（开始/暂停/重置/删除）
- ✅ 8种清新主题色
- ✅ 本地数据自动保存
- ✅ 倒计时结束震动提醒

## GitHub Actions 自动构建

本项目使用 GitHub Actions 自动构建 Android APK。

### 构建步骤

1. **Fork 或创建仓库**
   - 在 GitHub 创建新仓库
   - 上传本项目所有文件

2. **触发构建**
   - 推送代码到 `main` 分支会自动触发构建
   - 或手动触发：进入仓库 → Actions → Build Android APK → Run workflow

3. **下载 APK**
   - 构建完成后，在 Actions 页面下载 artifacts
   - 或在 Releases 页面下载自动发布的 APK

### 构建时间

首次构建约 15-20 分钟（需要下载 Android SDK 和依赖）
后续构建约 5-10 分钟

## 本地开发

### 环境要求

- Python 3.8+
- Kivy 2.2.1
- Buildozer（用于打包APK）

### 安装依赖

```bash
pip install kivy==2.2.1
```

### 运行桌面版

```bash
python main.py
```

### 构建 APK（本地）

```bash
# 安装 buildozer
pip install buildozer cython

# 构建调试版APK
buildozer android debug

# 构建发布版APK
buildozer android release
```

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── build.yml      # GitHub Actions 配置
├── main.py                # 主程序
├── buildozer.spec         # Buildozer 配置
└── README.md              # 说明文档
```

## 技术栈

- **Python 3.11**
- **Kivy 2.2.1** - 跨平台GUI框架
- **Buildozer** - Android打包工具
- **GitHub Actions** - CI/CD自动化

## 许可证

MIT License