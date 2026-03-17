# Alpha Monitor iOS App（私有安装版）

这是一个给你自己使用、也可以分享给指定人安装的苹果 App 项目骨架。

## 目标

把你现在网页中的核心能力，收敛成一个 iPhone 应用：
- AH/AB 机会概览
- 套利监控
- 分红持仓
- 提醒列表
- 留言查看

## 技术路线（最适合私有分发）

- App 框架：Expo + React Native
- 数据接口：你现有站点的 `/api/dashboard`
- 分发方式：Apple TestFlight（仅你或你邀请的人可安装）

## 为什么推荐 TestFlight

- 不需要公开上架给所有人
- 你可以控制谁能安装
- 更新版本后，测试用户自动收到更新

## 本地启动（开发阶段）

1. 安装 Node.js 18+
2. 进入目录：`cd "C:\Users\93724\Desktop\Alpha monitor"`
3. 安装依赖：`npm install`
4. 启动：`npx expo start`

## 你需要改的唯一配置

打开 `src/services/dashboardApi.ts`，把：
`API_BASE_URL` 改成你的真实服务地址（必须 https）。

例如：
`https://your-domain.com`

## 私有安装发布路径（生产）

1. 注册 Apple Developer（99 美元/年）
2. 用 EAS Build 打包 iOS
3. 上传到 App Store Connect
4. 在 TestFlight 添加安装人员（你自己 + 你分享的人）

## 重要说明

- 这是“私有可分享安装”，不是“公开全民可下载”。
- 你的数据接口建议加鉴权（例如 API Key 或登录态），避免外部访问。
