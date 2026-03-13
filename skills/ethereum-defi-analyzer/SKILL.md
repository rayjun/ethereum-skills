---
name: ethereum-defi-analyzer
description: DeFi 协议与收益分析。涵盖流动性池（Uniswap, Curve）、借贷市场（Aave, Compound）、收益农耕及套利机会分析。适用于计算收益率、风险评估及协议调研。
---

# 以太坊 DeFi 分析师 (Ethereum DeFi Analyzer)

该技能专注于去中心化金融协议的数学模型、收益核算与风险控制。

## 使用场景 (When to Use)
- **收益测算**: 计算 LP 池的 APR/APY，包含代币激励。
- **风险量化**: 评估特定借贷仓位的健康因子 (Health Factor) 及清算风险。
- **机制调研**: 解释 Uniswap V3 的集中流动性或 Curve 的放大系数 (A)。
- **套利侦查**: 计算跨协议、跨池的差价及包含手续费后的真实利润。

## 边界与衔接 (Boundaries)
- **如果需要审计 DeFi 合约的代码安全性** -> 移交给 `ethereum-security-auditor`。
- **如果需要查看某次大额清算交易的轨迹** -> 移交给 `ethereum-transaction-inspector`。

## 核心工作流 (Workflow)
1. **池子定位**: 通过 Factory 合约找到目标 Pool 地址。
2. **参数抓取**: 使用 `cast call` 获取 `reserves`, `price`, `utilization` 等实时数据。
3. **数学演算**: 应用相应的协议公式（如 AMM 恒定乘积公式、Ray 单位转换等）。
4. **风险核算**: 计算无偿损失 (IL) 或模拟价格波动下的清算临界点。
5. **策略对比**: 比较不同协议的收益与风险权重。

## 推荐工具
- `cast`: 用于调用协议的 Read-only 函数。
- 协议文档引用: 熟知 Aave, Uniswap 等主流协议的架构。

## 输出格式
- **资产配置**: 池中资产比例及 USD 总值。
- **收益明细**: 基础费用 + 奖励代币 = 总 APR。
- **风险指标**: 健康因子、清算价格、最大滑点承受力。
- **策略点评**: 对该策略的流动性及风险水平给出建议。
