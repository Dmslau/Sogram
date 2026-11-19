# Upstream source and licensing notice

Base project: [TelegramMessenger/Telegram-iOS](https://github.com/TelegramMessenger/Telegram-iOS)

Default workflow ref: `b460f1d8948e725331b34981cc2a563aeeae97fd` (Swiftgram 13.2.1 / master as of 2026-11-19). The source and recursive Git submodules are fetched by GitHub Actions rather than copied into this repository. The ref is pinned for reproducible builds; override it in `workflow_dispatch` only when you intentionally want a newer upstream snapshot.

上游 README 要求使用自己的 API ID，标明非官方身份，不要使用 Telegram 的标准名称和纸飞机标志，遵守其安全建议，并按 GNU GPL 公开代码。本仓库只保存构建脚本和补丁；修改后的完整源码在 runner 上生成。如果分发 IPA，需要同时提供对应源码。不要把这个 App 说成官方 Telegram。
