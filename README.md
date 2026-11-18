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

建议把 `upstream_ref` 设置为已经验证过的固定 Swiftgram commit，而不是 `master`，以保证构建可复现。

IPA 为 arm64 未签名包。为便于后续个人证书重签，构建会移除扩展、描述文件和代码签名，因此不能直接安装。
