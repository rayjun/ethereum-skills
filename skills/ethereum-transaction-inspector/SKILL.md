---
name: ethereum-transaction-inspector
description: 深度分析以太坊交易。涵盖函数调用解码、内部 Trace 追踪、Gas 消耗剖析及代币转账提取。适用于理解交易行为、调试失败交易或分析 MEV 模式。
---

# 以太坊交易检查员 (Ethereum Transaction Inspector)

该技能专注于单笔交易的深度取证与行为分析。

## 使用场景 (When to Use)
- **交易溯源**: 用户询问“这笔交易做了什么？”
- **失败调试**: 交易状态为失败，用户需要知道具体的回退 (Revert) 原因。
- **内部调用分析**: 涉及合约间复杂交互，需要查看 `DELEGATECALL` 或内部 `CALL`。
- **Gas 审计**: 分析交易中哪些步骤最耗费 Gas。
- **资产流向**: 提取一笔交易中涉及的所有代币和 ETH 转移。

## 边界与衔接 (Boundaries)
- **如果发现涉及多个区块的模式分析** -> 移交给 `ethereum-chain-explorer`。
- **如果需要深入了解被调用合约的逻辑** -> 移交给 `ethereum-contract-analyzer`。
- **如果怀疑交易涉及安全攻击（如黑客行为）** -> 移交给 `ethereum-security-auditor`。

## 核心工作流 (Workflow)
1. **基础检索**: 使用 `cast tx` 获取基本信息，`cast receipt` 获取执行结果。
2. **解码 Calldata**: 提取前 4 字节，通过 4byte.directory 或 `cast 4byte-decode` 解码。
3. **Trace 追踪**: 使用 `cast run --trace` 深入内部调用栈。
4. **事件提取**: 解码收据中的 `logs`，识别 ERC20/721 转账。
5. **原因诊断**: 对于失败交易，定位回退位置并提取错误信息（Error Selector）。

## 推荐工具
- `cast` (Foundry): 执行几乎所有的链上查询和解码。
- `jq`: 用于处理复杂的 JSON 返回。

## 输出格式
- **概览**: 哈希、状态、发送/接收方、Value。
- **行为解码**: 被调用的函数及参数。
- **资金流动**: [Token] [Amount] [From] -> [To]。
- **失败诊断**: (仅失败交易) 具体的错误信息及位置。
- **Gas 总结**: 实际消耗量及价格。
