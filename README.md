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
- 输出文件：`Sogram.ipa`

默认 `upstream_ref` 固定为 Swiftgram commit `b460f1d8948e725331b34981cc2a563aeeae97fd`（13.2.1 / master 2026-11-19）。缓存 key 稳定、构建可复现，不会被上游 master 更新影响。需要升级时，在 `workflow_dispatch` 里手动指定新的 commit 或 branch。

产出未签名包，移除了扩展、描述文件和代码签名，**无法直接安装，需自签后使用**。

## 下载

最新 IPA 固定链接：
```
https://github.com/Dmslau/swiftgram-ipa/releases/latest/download/Sogram.ipa
```