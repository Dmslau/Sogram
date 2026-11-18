# Swiftgram IPA 构建项目

本项目基于 Dmslau/Sogram 的无 Mac 构建脚手架，GitHub Actions 在 macOS runner 上递归拉取 Swiftgram/Telegram-iOS 并执行 Swiftgram 自带的 Bazel/Make 构建系统。

## 首次构建

1. 在仓库 Actions Secrets 配置 `TG_API_ID`、`TG_API_HASH` 和 `BARK_KEY`。
2. 运行 **Build Swiftgram unsigned IPA**。
3. 首次使用默认 `org.swiftgram.build`；需要安装/重签时可改为自己的非官方 Bundle ID。
4. 构建产物为 `Swiftgram-unsigned.ipa`，扩展、描述文件和 Mach-O 签名会被移除，后续需要自行重签，不能直接安装。

构建配置保留 Swiftgram 模板的 `tg` scheme，并使用 Swiftgram 源码仓库原有的 API ID/hash 机制；API 值由 Actions Secret 注入，不写入本仓库。首轮使用随机/自定义 Bundle ID，不使用官方 Telegram Bundle ID。