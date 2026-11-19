# Sogram 构建项目

Swiftgram 指定源码并打包。

## Actions Secrets

配置 GitHub Actions Secrets：

- `APIID`
- `APIHASH`
- `BARK_KEY`

构建配置只从 `APIID` 和 `APIHASH` 读取真实值；缺少任一变量时构建直接失败。

## 默认构建参数

- Bundle ID：`com.dmslau.sogram`
- 显示名称：`Sogram`
- 输出文件：`Swiftgram-unsigned.ipa`

默认 `upstream_ref` 固定为 Swiftgram commit `b460f1d8948e725331b34981cc2a563aeeae97fd`（13.2.1 / master 2026-11-19）。缓存 key 稳定、构建可复现，不会被上游 master 更新影响。需要升级时，在 `workflow_dispatch` 里手动指定新的 commit 或 branch。

产出未签名包，移除了扩展、描述文件和代码签名，**无法直接安装，需自签后使用**。

## 更新日志

- **2026-11-19**
  - 强制 Pro 状态（`immediateSGStatus.status = 2`），解锁 Pro 功能
  - 消息过滤：关键词匹配直接隐藏消息（原为降低透明度）
  - 敏感内容去模糊：Spoiler 媒体、自毁媒体、敏感内容标记媒体在 Pro 下直接显示
  - 媒体网格页敏感内容去模糊
  - 自动清理旧 Release，只保留最新 1 个，最新下载链接固定：`/releases/latest/download/Swiftgram-unsigned.ipa`
  - 新增每日定时刷新 Bazel 缓存（北京时间 05:00）
  - 移除 UPSTREAM.md，合规信息合并至 README
  - Git 提交身份改为 Dmslau

## Pro 功能（需自签安装）

- 消息关键词过滤（隐藏匹配消息）
- 敏感内容直接显示（Spoiler/自毁/敏感标记）
- 输入工具栏
- 会话备份
- App 图标 / Badge 设置
- 置顶/提及通知策略（需扩展配合，未签名包不可用）

## 下载

最新 IPA 固定链接：
```
https://github.com/Dmslau/swiftgram-ipa/releases/latest/download/Swiftgram-unsigned.ipa
```