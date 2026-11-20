# Sogram (Swiftgram Fork) - 完整功能变更文档

**版本**: 基于 Swiftgram commit `b460f1d8948e725331b34981cc2a563aeeae97fd` (Telegram 13.2.1)  
**构建方式**: GitHub Actions macOS (xcode-27) + Bazel，产出未签名 IPA  
**分发方式**: GitHub Release 下载 `Sogram.ipa`，需自签安装

---

## 目录
1. [核心架构变更](#核心架构变更)
2. [新增功能清单](#新增功能清单)
3. [补丁文件清单](#补丁文件清单)
4. [配置键与默认值](#配置键与默认值)
5. [设置菜单结构](#设置菜单结构)
6. [已知限制与风险](#已知限制与风险)
7. [待解决问题](#待解决问题)

---

## 核心架构变更

| 变更 | 说明 |
|------|------|
| **基线升级** | 从 Swiftgram `fb0e62ba` (13.1.1, 无模块) → `b460f1d89` (13.2.1, 完整 Swiftgram 模块) |
| **Pro 状态强制开启** | `immediateSGStatus.status = 2`、`ephemeralStatus = 2`，绕过官方订阅检查 |
| **Pro 页面合并** | 独立 Pro 页面移除，所有功能并入 Swiftgram 设置（非 Pro 用户可见） |
| **缓存策略** | 固定 `upstream_ref = b460f1d...`，每日 UTC 21:00 (北京 05:00) 自动刷新 Bazel 缓存 |
| **输出文件名** | `Sogram.ipa` (原 `Swiftgram-unsigned.ipa`) |
| **Release 清理** | 每次发布自动只保留最新 1 个 Release |

---

## 新增功能清单

### 1. 隐藏置顶消息栏
- **开关**: `hidePinnedMessages` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **隐藏置顶消息栏**
- **实现**: `ChatInterfaceTitlePanelNodes.swift` 拦截 `chatPinnedPanelIsVisible`，开启时直接返回 `false`

### 2. 敏感媒体去模糊
- **开关**: `hideSensitiveMediaBlur` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **敏感媒体去模糊**
- **覆盖范围**:
  - 聊天页 Spoiler/自毁/敏感媒体 (`ChatHistoryListNode`, `ChatMessageInteractiveMediaNode`)
  - 全部媒体页 (`PeerInfoMediaGridPaneNode`)
- **实现**: 读取 `hideSensitiveMediaBlur` 替代原 `ephemeralStatus > 1` 判断

### 3. 全局关闭广告 (4 类全屏蔽)
- **开关**: `disableAds` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **全局关闭广告**
- **屏蔽范围**:
  1. **固定广告** (频道底部固定赞助消息) - `ChatHistoryEntriesForView.swift`
  2. **动态广告** (聊天中插入的赞助消息) - `ChatHistoryEntriesForView.swift`
  3. **频道内嵌赞助帖** (带 `adAttribute` 的普通消息) - `ChatHistoryEntriesForView.swift`
  4. **Bot 聊天顶部广告面板** (adPanelMessage) - `ChatControllerNode.swift`
  5. **广告预加载/管理** - `ChatHistoryListNode.swift` (开启时跳过管理逻辑)

### 4. Pro 功能合并入 Swiftgram 设置
- **原 Pro 页面已移除**，个人资料页不再有独立 Pro 入口
- **合并功能** (均在 Swiftgram 设置 → SWIFTGRAM PRO 分区):
  - 会话备份 (`sgSessionBackupManagerController`)
  - 消息关键词过滤 (`sgMessageFilterController`)
  - 输入格式化工具栏 (`inputToolbar`)
  - 置顶/提及通知策略 (`pinnedMessageNotifications` / `mentionsAndRepliesNotifications`)
  - App 图标与 Badge 设置 (`sgAppBadgeSettingsController`)

### 5. 本地解锁 Telegram 会员
- **开关**: `localPremiumEnabled` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **本地解锁 Telegram 会员**
- **生效范围**:
  - `AccountContext.isPremium` 即时计算: `effectivePremium = isPremium || localPremiumEnabled`
  - 本地会员限额 (`UserLimits`)、语音转写权限同步放开
- **限制**: 仅本地 UI 生效，**官方资料页仍显示非会员**，无法伪造服务端订阅状态

### 6. 隐藏置顶消息栏
- **开关**: `hidePinnedMessages` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **隐藏置顶消息栏**
- **实现**: `ChatInterfaceTitlePanelNodes.swift` -> `chatPinnedPanelIsVisible` 判定处拦截

### 7. 屏蔽 Bot 聊天顶部广告面板
- **复用开关**: `disableAds`
- **实现**: `ChatControllerNode.swift` -> `displayAdPanel` 判定处加 `!disableAds` 条件

### 8. 解除 Bot iOS 限制 (部分生效)
- **开关**: `bypassBotRestriction` (Bool, 默认 false)
- **位置**: 设置 → Swiftgram → Other → **解除 Bot iOS 限制（需自担风险）**
- **已生效**: Bot 入口可进、可发消息
- **未生效**: Bot 回复消息仍显示限制 (见待解决问题)

---

## 补丁文件清单

| 文件 | 作用 | 调用顺序 |
|------|------|----------|
| `patch_sgsettings_keys.py` | 注册 6 个新配置键、默认值、属性 | 1 |
| `patch_merge_pro_settings.py` | 合并 Pro 页面到 Swiftgram 设置 | 2 |
| `patch_sgsettings_controller.py` | 设置页枚举/入口/文案/写入逻辑 | 3 |
| `patch_local_premium.py` | 本地会员即时生效 (`effectivePremium`) | 4 |
| `patch_bypass_bot_restriction.py` | **新** 解除 appleterms-ios Bot 限制 | 5 |
| `patch_disable_ads.py` | 广告全屏蔽 (5 处) | 6 |
| `patch_message_filter_hide.py` | 消息关键词过滤 -> 完全隐藏 | 7 |
| `patch_sensitive_content.py` | 敏感媒体去模糊 | 8 |
| `patch_media_grid_spoiler.py` | 媒体网格页去模糊 | 9 |
| `patch_hide_pinned_panel.py` | 隐藏置顶消息栏 | 10 |
| `patch_message_filter_hide.py` | 消息过滤隐藏 | 11 |
| `patch_sensitive_content.py` | 敏感内容去模糊 | 12 |
| `patch_media_grid_spoiler.py` | 媒体网格页去模糊 | 13 |
| `patch_hide_pinned_panel.py` | 隐藏置顶面板 | 14 |
| `patch_bypass_bot_payment.py` | 解除 Bot 支付限制 (未完善) | 15 |
| `patch_bypass_bot_restriction.py` | **新** 解除 appleterms-ios Bot 限制 | 16 |
| `apply_resign_compat.py` | 签名兼容 | 0 |
| `force_pro_status.py` | 强制 Pro 状态 | -1 |

---

## 配置键与默认值

| Key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `hidePinnedMessages` | Bool | false | 隐藏置顶消息栏 |
| `hideSensitiveMediaBlur` | Bool | false | 敏感媒体去模糊 |
| `localPremiumEnabled` | Bool | false | 本地解锁会员 |
| `disableAds` | Bool | false | 全局关闭广告 |
| `bypassBotPaymentRestriction` | Bool | false | 解除 Bot 支付限制 (未完善) |
| `bypassBotRestriction` | Bool | false | 解除 appleterms-ios Bot 限制 |

所有键均通过 `@UserDefault` 持久化到 `App Group` (或标准 `UserDefaults`)，跨进程共享。

---

## 设置菜单结构

```
Swiftgram 设置
├── 聊天列表
├── 聊天设置
├── 文件夹
├── 资料
├── Stories
├── 翻译
├── 语音转写
├── 图片质量
├── 贴纸
├── 长按菜单
├── 颜色
├── 网络加速
├── SWIFTGRAM PRO (原 Pro 页面合并)
│   ├── 会话备份
│   ├── 消息关键词过滤
│   ├── 输入格式化工具栏
│   ├── 置顶消息通知策略
│   ├── 提及与回复通知策略
│   ├── App 图标
│   └── Badge 设置
├── Other
│   ├── 隐藏置顶消息栏
│   ├── 敏感媒体去模糊
│   ├── 本地解锁 Telegram 会员
│   ├── 全局关闭广告
│   ├── 解除 Bot 支付限制
│   └── 解除 Bot iOS 限制（需自担风险）  ← 新增
├── 高级
└── 关于
```

---

## 已知限制与风险

| 风险 | 说明 | 规避建议 |
|------|------|----------|
| **Bot 限制绕过** | 仅本地生效，开启后可进 Bot、发消息，**但 Bot 回复消息仍受限** | 见待解决问题 |
| **本地会员** | 仅本地 UI 生效，官方资料页仍显示非会员 | 不可伪造服务端订阅 |
| **广告屏蔽** | 可能漏过新型广告形式 | 定期测试并补充补丁 |
| **Bot 限制绕过** | 仅本地生效，**违反 App Store 审核指南 3.1.3/4.7** | 仅限私有仓库、自用、不分发 |
| **Apple 下架风险** | 绕过 Bot 支付限制属规避 IAP | 严禁上架 App Store / TestFlight |
| **Telegram 封号** | 客户端行为异常可能触发风控 | 低频使用，勿大规模分发 |

---

## 待解决问题

### 1. Bot 回复消息仍显示限制 (优先级: 高)
**现象**: 开启 `bypassBotRestriction` 后，能进 Bot、能发消息，但 **Bot 回复的消息** 显示：
> "This message couldn't be displayed on your device. appleterms-ios"

**推测原因**: 限制检查不只在入口 (`PeerUtils.restrictionText`)，**消息渲染层**也有二次校验。

**疑似位置** (需验证):
1. `ChatMessageItemView.swift` / `ChatMessageBubbleItemNode.swift` - 消息渲染时的二次限制检查
2. `ChatMessageItemImpl.swift` - 消息内容解析时的限制判定
3. `ChatController.swift` - 消息接收/处理流程中的限制拦截
4. `ChatMessageItemCommon` - 通用消息项的限制属性读取

**建议排查步骤**:
1. 搜索 `appleterms` / `restrictionReason` / `restrictionText` 在 `ChatMessage` 相关文件中的使用
2. 在消息渲染入口加相同的 `bypassBotRestriction` 判定跳过
4. 重点关注 `ChatMessageItemView.asyncLayout` / `ChatMessageBubbleItemNode.asyncLayout`

---

## 补丁文件完整列表 (按构建顺序)

```
scripts/patch_sgsettings_keys.py
scripts/patch_merge_pro_settings.py
scripts/patch_sgsettings_controller.py
scripts/patch_local_premium.py
scripts/patch_bypass_bot_restriction.py
scripts/patch_disable_ads.py
scripts/patch_message_filter_hide.py
scripts/patch_sensitive_content.py
scripts/patch_media_grid_spoiler.py
scripts/patch_hide_pinned_panel.py
scripts/patch_bypass_bot_payment.py
scripts/patch_bypass_bot_restriction.py
scripts/apply_resign_compat.py
scripts/generate_build_config_swiftgram.py
scripts/enable_unsigned_device_build_swiftgram.py
scripts/package_unsigned_ipa.py
scripts/validate_unsigned_ipa.py
scripts/write_install_report.py
```

---

## 构建命令参考

```bash
# 手动触发构建
gh workflow run build-swiftgram-unsigned.yml \
  --ref main \
  -f upstream_ref=b460f1d8948e725331b34981cc2a563aeeae97fd \
  -f app_bundle_id=com.dmslau.sogram \
  -f app_display_name=Sogram

# 手动刷新缓存
gh workflow run refresh-bazel-cache.yml --ref main

# 查看最新 Release 下载链接
https://github.com/Dmslau/swiftgram-ipa/releases/latest/download/Sogram.ipa
```

---

## 环境变量需求 (GitHub Secrets)

| Secret | 必填 | 说明 |
|--------|------|------|
| `APIID` | ✅ | Telegram API ID (纯数字) |
| `APIHASH` | ✅ | Telegram API Hash (32位十六进制) |
| `BARK_KEY` | 可选 | Bark 推送 Key (构建完成通知) |

---

*文档生成时间: 2026-11-20 | 基于 commit `d6eff9e`*