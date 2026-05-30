# 数据字段修复验证 Skill

**触发词**: 数据为空, 字段缺失, UI显示空白, 修复数据, null字段

## 核心原则

**改完代码不算修好。跑完三层验证 + 确认字段非空才算修好。**

## 三层验证协议

修任何涉及 UI 显示数据的问题，必须逐层通过：

### Layer 1: 代码语法

```bash
python -c "import data_fetch.lof_iopv.source"
```

### Layer 2: API 返回值

```bash
python scripts/verify_data_field.py lof-arbitrage rows[0].iopv
```

### Layer 3: 字段非空断言（关键）

```bash
python scripts/verify_data_field.py lof-arbitrage rows[0].iopv 161125
python scripts/verify_data_field.py lof-arbitrage rows[0].premiumRate 161125
python scripts/verify_data_field.py lof-arbitrage rows[0].dailyLimit 161125
```

## 执行流程

```
用户: "XX字段是空的"
  ↓
AI: 分析根因（哪层返回了 null）
  ↓
AI: 修改代码
  ↓
AI: Layer 1 语法 → PASS
  ↓
AI: Layer 2 调API → 检查字段
  ↓
字段仍为 null → 回到修改代码，不说"修好了"
  ↓
AI: Layer 3 字段非空 → PASS
  ↓
AI: "修好了，字段值为 xxx"
```

## 常见 null 根因

| 字段 | 常见根因 | 排查方向 |
|------|----------|----------|
| nav / navDate | eastmoney lsjz API 502 | 检查API状态，DB历史数据 |
| iopv | NAV为null或持仓为空 | 先确保nav非空 |
| premiumRate | iopv或price为null | 先确保iopv非空 |
| fxRatio | 汇率API超时 | 查DB fx_rates表 |
| stockRatio | akshare持仓比例API失败 | 检查akshare连通性 |
| dailyLimit | 东方财富HTML regex不匹配 | 检查HTML结构变化 |
| r2 / maxErr | 回测结果文件不存在 | 查backtest results_v2.json |

## 验证脚本

`scripts/verify_data_field.py`:

```bash
python scripts/verify_data_field.py <endpoint> <field_path> [code]

# 示例
python scripts/verify_data_field.py lof-arbitrage rows[0].iopv 161125
python scripts/verify_data_field.py ah rows[0].ahPremiumRate
python scripts/verify_data_field.py exchange-rate data.usd.cny
```

返回码：0=通过（字段有值），1=失败（null或API错误）

## 禁止行为

- 改完代码就说"修好了"
- 只检查语法就认为完成
- 假设"代码逻辑对了数据就有了"
- 不看API实际返回的JSON
- 必须跑 verify_data_field.py 确认字段非空
- 如果字段仍为null，继续排查，不交付