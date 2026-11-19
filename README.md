# Sogram 构建项目

本仓库在 GitHub Actions 上构建 Swiftgram 上游源码并打包未签名 IPA。

## Actions Secrets

请配置以下 GitHub Actions Secrets：

- `APIID`
- `APIHASH`
- `BARK_KEY`

构建配置只从 `APIID` 和 `APIHASH` 读取真实值；缺少任一变量时构建直接失败，绝不使用 Swiftgram 上游示例凭据。

## 默认构建参数

- Bundle ID：`com.dmslau.sogram`
- 显示名称：`Sogram`
- 输出文件：`Swiftgram-unsigned.ipa`

默认 `upstream_ref` 固定为 Swiftgram commit `b460f1d8948e725331b34981cc2a563aeeae97fd`（13.2.1 / master 2026-11-19）。缓存 key 稳定、构建可复现，不会被上游 master 更新牵着走。需要升级时，在 `workflow_dispatch` 里手动指定新的 commit 或 branch。

IPA 为 arm64 未签名包。为便于后续个人证书重签，构建会移除扩展、描述文件和代码签名，因此不能直接安装。
