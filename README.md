# 以太坊专家技能集 (Ethereum Expert Skills)

这是一个为 Gemini CLI 开发的专业以太坊 (Ethereum) 分析技能集。它包含了一系列相互关联的技能，旨在帮助开发者、安全研究员和 DeFi 玩家对区块链数据、智能合约、交易模式及以太坊提案进行深度挖掘和自动化分析。

## 技能列表 (Available Skills)

| 技能名称 | 标识符 | 核心功能 |
| :--- | :--- | :--- |
| **以太坊交易检查员** | `ethereum-transaction-inspector` | 深度分析交易哈希、解码函数调用、追踪内部调用流及调试失败交易。 |
| **以太坊安全审计员** | `ethereum-security-auditor` | 自动化漏洞扫描（Slither/Mythril）、人工审计核对清单及合约风险评估。 |
| **以太坊提案研究员** | `ethereum-proposal-researcher` | 研究 ethresear.ch 提案，评估技术可行性、潜在影响及实施技术债。 |
| **以太坊 DeFi 分析师** | `ethereum-defi-analyzer` | 分析 DEX 流动性、借贷利率、计算 APY/APY 及评估无偿损失风险。 |
| **以太坊合约分析师** | `ethereum-contract-analyzer` | 解析合约源代码、识别代理模式（Proxy）、解码 ABI 及分析存储布局。 |
| **以太坊区块链浏览器** | `ethereum-chain-explorer` | 查询实时网络状态、账户余额、历史事件日志及合约部署记录。 |

## 安装方式 (Installation)

### 1. 克隆仓库
首先，将此仓库克隆到您的本地工作区：

```bash
git clone https://github.com/your-repo/ethereum-skills.git
cd ethereum-skills
```

### 2. 配置 Gemini CLI
将技能目录添加到您的 Gemini CLI 配置文件中，或者直接在当前工作区启动。

如果您希望全局可用，可以使用类似以下命令（视您的 CLI 版本而定）：
```bash
gemini skill install ./skills/ethereum-chain-explorer
# ... 为其他技能执行类似操作
```

### 3. 前置依赖 (Prerequisites)

为了使这些技能发挥最佳性能，建议安装以下工具：

- **Foundry (推荐)**: 包含强大的 `cast` 工具，用于链上查询。
  ```bash
  curl -L https://foundry.paradigm.xyz | bash
  foundryup
  ```
- **Python 依赖**: 技能中的自动化分析脚本依赖以下库。
  ```bash
  pip install web3 eth-abi eth-utils slither-analyzer mythril beautifulsoup4 requests
  ```
- **RPC 节点**: 您需要一个以太坊 RPC 节点（如 Infura, Alchemy 或本地节点）的 URL。建议在环境变量中配置 `ETH_RPC_URL`。

## 使用示例 (Usage Examples)

您可以直接向 Gemini 提出指令，技能会根据您的描述自动触发：

- **交易分析**: `"帮我看看这笔失败的交易是怎么回事：0x789..."`
- **合约审计**: `"对这个地址进行安全审查，看看有没有重入漏洞：0xabc..."`
- **DeFi 分析**: `"计算一下 Uniswap V3 USDC/WETH 池子的当前收益率和价格区间分布。"`
- **提案研究**: `"分析一下 ethresear.ch 上关于加密内存池（Encrypted Mempool）的最新提案。"`

## 项目结构 (Project Structure)

```text
ethereum-skills/
├── README.md           # 项目主文档
└── skills/             # 技能集目录
    ├── ethereum-chain-explorer/        # 区块链浏览器技能
    ├── ethereum-contract-analyzer/     # 合约分析技能
    ├── ethereum-defi-analyzer/         # DeFi 分析技能
    ├── ethereum-proposal-researcher/   # 提案研究技能
    ├── ethereum-security-auditor/      # 安全审计技能
    └── ethereum-transaction-inspector/ # 交易检查技能
```

## 贡献与反馈
欢迎通过 Issue 或 Pull Request 提交新的技能或改进现有功能。
