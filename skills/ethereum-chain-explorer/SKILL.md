---
name: ethereum-chain-explorer
description: Query and analyze Ethereum blockchain data including blocks, accounts, balances, historical data, and on-chain patterns. Use when users want to explore blockchain state, analyze address activity, query historical data, or track on-chain metrics. Triggers include checking balances, exploring addresses, analyzing blocks, or querying chain state.
---

# Ethereum Chain Explorer

Comprehensive blockchain data querying and analysis for current state, historical data, and on-chain patterns.

## When to Use This Skill

Use this skill when the user wants to:
- Query current blockchain state (latest block, gas price, etc.)
- Check account balances (ETH and tokens)
- Analyze address activity and transaction history
- Explore block data and contents
- Query historical data ranges
- Track contract deployments
- Analyze on-chain patterns and metrics
- Monitor network conditions

## Prerequisites

- Web3 Python library (`pip install web3 eth-abi eth-utils`)
- RPC endpoint (Infura, Alchemy, or local node)
- Etherscan API key (for historical data and labels)
- Archive node access (for historical state queries)

## Exploration Workflows

### Workflow 1: Query Current Blockchain State

Get real-time network information:

```bash
# Latest block number
cast block-number --rpc-url <RPC_URL>

# Latest block details
cast block latest --rpc-url <RPC_URL>

# Current gas price
cast gas-price --rpc-url <RPC_URL>

# Current base fee (post-EIP-1559)
cast basefee --rpc-url <RPC_URL>

# Chain ID
cast chain-id --rpc-url <RPC_URL>
```

**Present network status:**
```
Network Status (Ethereum Mainnet):
- Latest Block: #18,500,000
- Timestamp: 2024-01-15 10:30:45 UTC
- Base Fee: 25 Gwei
- Gas Price: 30 Gwei (median)
- Block Time: 12.05s average
```

### Workflow 2: Analyze Account/Address

Comprehensive address analysis:

**Step 1: Determine address type**
```bash
# Check if contract
cast code <ADDRESS> --rpc-url <RPC_URL>

# If non-empty, it's a contract; if empty, it's an EOA
```

**Step 2: Get ETH balance**
```bash
cast balance <ADDRESS> --rpc-url <RPC_URL>

# At specific block (requires archive node)
cast balance <ADDRESS> --block <BLOCK_NUMBER> --rpc-url <RPC_URL>
```

**Step 3: Get token balances**
```bash
# For specific ERC20 token
cast call <TOKEN_ADDRESS> "balanceOf(address)(uint256)" <ADDRESS> --rpc-url <RPC_URL>

# Common tokens to check:
# USDC: 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
# USDT: 0xdac17f958d2ee523a2206206994597c13d831ec7
# WETH: 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2
```

**Step 4: Get transaction count (nonce)**
```bash
cast nonce <ADDRESS> --rpc-url <RPC_URL>
```

**Step 5: Fetch transaction history**
```bash
# Using Etherscan API
curl "https://api.etherscan.io/api?module=account&action=txlist&address=<ADDRESS>&startblock=0&endblock=99999999&sort=desc&apikey=<KEY>"

# Get internal transactions
curl "https://api.etherscan.io/api?module=account&action=txlistinternal&address=<ADDRESS>&startblock=0&endblock=99999999&sort=desc&apikey=<KEY>"

# Get ERC20 transfers
curl "https://api.etherscan.io/api?module=account&action=tokentx&address=<ADDRESS>&startblock=0&endblock=99999999&sort=desc&apikey=<KEY>"
```

**Present address summary:**
```
Address Analysis: 0xabc...
Type: Contract (Uniswap V3 Pool)
ETH Balance: 0 ETH
Created: Block #12,345,678 (2021-05-04)
Transaction Count: 15,234 transactions
First Activity: 2021-05-04
Last Activity: 2024-01-15

Top Token Holdings:
1. USDC: 1,500,000 ($1,500,000)
2. WETH: 525 ($1,050,000)

Activity Summary:
- Swaps: 10,234
- Liquidity adds: 2,500
- Liquidity removes: 2,500
```

### Workflow 3: Analyze Block Data

Explore block contents and patterns:

**Step 1: Fetch block data**
```bash
# By block number
cast block <BLOCK_NUMBER> --rpc-url <RPC_URL>

# By block hash
cast block <BLOCK_HASH> --rpc-url <RPC_URL>

# Latest block
cast block latest --rpc-url <RPC_URL>
```

**Step 2: Extract block information**
- `number` - Block number
- `hash` - Block hash
- `parentHash` - Previous block hash
- `timestamp` - Unix timestamp
- `miner` / `coinbase` - Block producer
- `gasUsed` / `gasLimit` - Gas metrics
- `baseFeePerGas` - EIP-1559 base fee
- `transactions` - Transaction hashes
- `size` - Block size in bytes

**Step 3: Analyze transactions in block**
```bash
# Get transaction count
cast block <BLOCK_NUMBER> --json --rpc-url <RPC_URL> | jq '.transactions | length'

# Iterate through transactions (in script)
for tx in $(cast block <BLOCK_NUMBER> --json --rpc-url <RPC_URL> | jq -r '.transactions[]'); do
  cast tx $tx --rpc-url <RPC_URL>
done
```

**Present block analysis:**
```
Block #18,500,000:
- Hash: 0xabc...
- Timestamp: 2024-01-15 10:30:45 UTC
- Miner: Flashbots (0x123...)
- Transactions: 182
- Gas Used: 29.8M / 30M (99.3%)
- Base Fee: 25.3 Gwei
- Block Reward: 2.05 ETH

Transaction Breakdown:
- DEX Swaps: 45 (24.7%)
- Token Transfers: 67 (36.8%)
- NFT Mints: 12 (6.6%)
- DeFi: 38 (20.9%)
- Other: 20 (11.0%)

Top Gas Consumers:
1. 0xabc... - 2.5M gas (Uniswap swap)
2. 0xdef... - 1.8M gas (NFT mint)
3. 0xghi... - 1.2M gas (Contract deployment)
```

### Workflow 4: Historical Data Queries

Query past state and events:

**Step 1: Determine data availability**
- Regular nodes: Recent blocks only (~128 blocks)
- Archive nodes: Full history
- Etherscan API: Full history with limits

**Step 2: Query historical balance**
```bash
# Requires archive node
cast balance <ADDRESS> --block <BLOCK_NUMBER> --rpc-url <ARCHIVE_RPC_URL>
```

**Step 3: Query historical storage**
```bash
cast storage <CONTRACT> <SLOT> --block <BLOCK_NUMBER> --rpc-url <ARCHIVE_RPC_URL>
```

**Step 4: Search for events in range**
```bash
# Using cast (searches logs)
cast logs --from-block <START> --to-block <END> --address <CONTRACT> "<EVENT_SIG>" --rpc-url <RPC_URL>

# Example: Find all USDC transfers in block range
cast logs --from-block 18000000 --to-block 18000100 --address 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 "Transfer(address,address,uint256)" --rpc-url <RPC_URL>
```

**Step 5: Time-series analysis**
For tracking metrics over time:
1. Define time range and intervals
2. Query data points at each interval
3. Aggregate and analyze trends
4. Visualize if helpful (describe chart)

**Example: Track ETH balance over time**
```python
# Pseudo-code
blocks = [start_block + i * interval for i in range(num_points)]
balances = [get_balance(address, block) for block in blocks]
# Analyze trend
```

### Workflow 5: Contract Creation Analysis

Track when and how contracts were deployed:

**Step 1: Find creation transaction**
```bash
# Using Etherscan API
curl "https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=<ADDRESS>&apikey=<KEY>"
```

**Step 2: Analyze creation transaction**
- Creator address
- Creation block and timestamp
- Constructor parameters
- Initial code
- Creation cost (gas)

**Step 3: Check for factory pattern**
- Was it created by another contract?
- Is it one of many similar contracts?
- What factory pattern is used?

**Present creation analysis:**
```
Contract Creation: 0xabc...
- Creator: 0xdef... (Uniswap Factory)
- Creation Tx: 0x123...
- Block: #12,345,678 (2021-05-04 08:30:00 UTC)
- Gas Used: 3,500,000
- Creation Cost: 0.15 ETH ($450 at time)

Constructor Parameters:
- token0: 0xUSDC...
- token1: 0xWETH...
- fee: 3000 (0.3%)

Pattern: Uniswap V3 Pool (factory-deployed)
```

### Workflow 6: Network Monitoring

Track real-time network conditions:

**Metrics to monitor:**
```bash
# Gas prices
cast gas-price --rpc-url <RPC_URL>
cast basefee --rpc-url <RPC_URL>

# Block production rate
# Sample several blocks and calculate average time

# Network hash rate (approximate from difficulty)
cast block latest --json --rpc-url <RPC_URL> | jq '.difficulty'

# Pending transaction count (if available)
# Some nodes expose mempool data
```

**Present network status:**
```
Ethereum Network Status:

Gas Market:
- Base Fee: 25 Gwei (stable)
- Priority Fee: 1-2 Gwei
- Fast: 30 Gwei (~30s)
- Standard: 27 Gwei (~1min)
- Slow: 25 Gwei (~3min)

Block Production:
- Latest: #18,500,000
- Time: 12s ago
- Average Block Time: 12.1s
- Utilization: 95% (28.5M / 30M gas)

Network Health: ✓ Normal
```

## Advanced Queries

### Query Contract Storage

For understanding contract state:

**Step 1: Identify storage layout**
- Read contract source or ABI
- Map variables to slots
- Account for storage packing

**Step 2: Read storage slots**
```bash
cast storage <CONTRACT> <SLOT> --rpc-url <RPC_URL>
```

**Step 3: Decode storage values**
- uint256: Direct hex to decimal
- address: Take last 20 bytes
- bool: 0 or 1
- Packed variables: Decode bit positions
- Mappings: keccak256(key . slot)
- Arrays: Length at slot, data at keccak256(slot)

**Example: Read mapping value**
```bash
# For mapping(address => uint256) at slot 0
# Compute slot for specific key
cast index <KEY_ADDRESS> 0

# Read that computed slot
cast storage <CONTRACT> <COMPUTED_SLOT> --rpc-url <RPC_URL>
```

### Analyze Address Activity Patterns

Identify behavior patterns:

1. **Transaction frequency:**
   - High frequency: Bot, arbitrageur, protocol
   - Low frequency: Regular user
   - Burst patterns: Specific activities

2. **Transaction types:**
   - Predominantly swaps: Trader
   - NFT activities: Collector
   - Contract deployments: Developer
   - Diverse: Active user/protocol

3. **Value patterns:**
   - Large values: Whale, protocol
   - Consistent values: Bot, automated
   - Random values: Human user

4. **Time patterns:**
   - 24/7 activity: Bot
   - Business hours: Human
   - Event-triggered: Responder

5. **Counterparties:**
   - Few addresses: Focused activity
   - Many addresses: Broad activity
   - Specific protocols: Use-case specific

### Track Token Economics

For tracking token metrics:

**Supply tracking:**
```bash
# Total supply
cast call <TOKEN> "totalSupply()(uint256)" --rpc-url <RPC_URL>

# Circulating supply (if function exists)
cast call <TOKEN> "circulatingSupply()(uint256)" --rpc-url <RPC_URL>
```

**Holder distribution:**
- Top holders (via Etherscan)
- Distribution analysis (concentration risk)

**Transfer activity:**
- Volume over time
- Unique addresses
- Velocity metrics

## Output Formats

### Address Summary Format
```
Address: 0xabc...
Label: Uniswap V3: USDC/WETH Pool
Type: Contract

Balances:
- ETH: 0
- USDC: 1.5M
- WETH: 525

Activity:
- First Seen: Block #12,345,678
- Total Transactions: 15,234
- Last Activity: 2 hours ago

Description: [Brief description of address purpose/behavior]
```

### Block Summary Format
```
Block #18,500,000
Time: 2024-01-15 10:30:45 UTC
Hash: 0xabc...
Miner: Flashbots

Metrics:
- Transactions: 182
- Gas Used: 29.8M / 30M
- Base Fee: 25.3 Gwei
- Size: 125 KB

[Additional analysis as needed]
```

### Historical Query Format
```
Query: [Description of what was queried]
Time Range: Block #X to #Y (Date - Date)
Data Points: N

Results:
[Present data in tables, lists, or describe trends]

Analysis:
[Interpret the data]
```

## Integration with Other Skills

**Chain to other skills:**
- For contract addresses → invoke `ethereum-contract-analyzer`
- For specific transactions → invoke `ethereum-transaction-inspector`
- For DeFi protocol addresses → invoke `ethereum-defi-analyzer`
- For security analysis of contracts → invoke `ethereum-security-auditor`

## Common Commands Reference

```bash
# Current state
cast block-number --rpc-url <RPC_URL>
cast block latest --rpc-url <RPC_URL>
cast gas-price --rpc-url <RPC_URL>
cast basefee --rpc-url <RPC_URL>

# Account queries
cast balance <ADDRESS> --rpc-url <RPC_URL>
cast nonce <ADDRESS> --rpc-url <RPC_URL>
cast code <ADDRESS> --rpc-url <RPC_URL>

# Block queries
cast block <BLOCK_NUMBER> --rpc-url <RPC_URL>

# Contract calls
cast call <CONTRACT> "functionName()(returnType)" --rpc-url <RPC_URL>

# Storage
cast storage <CONTRACT> <SLOT> --rpc-url <RPC_URL>

# Event logs
cast logs --from-block <START> --to-block <END> "<EVENT_SIG>" --rpc-url <RPC_URL>

# Utilities
cast to-base <NUMBER> <BASE>  # Convert between number formats
cast to-dec <HEX>  # Hex to decimal
cast to-hex <DECIMAL>  # Decimal to hex
cast index <KEY> <SLOT>  # Compute mapping slot
```

## Error Handling

**Rate limiting:**
- Respect RPC provider limits
- Use delays between requests
- Batch requests when possible

**Archive data unavailable:**
- Regular node can't serve old state
- Use Etherscan API as fallback
- Explain limitations to user

**Large data ranges:**
- Break into smaller chunks
- Sample data points
- Use indexed data sources (TheGraph)

**Network issues:**
- Retry with exponential backoff
- Try alternative RPC endpoints
- Check endpoint status

## Tips for Effective Exploration

1. **Start broad:** Get overview before drilling down
2. **Use labels:** Etherscan labels help identify known addresses
3. **Cross-reference:** Verify data from multiple sources
4. **Context matters:** Consider when events occurred (market conditions, network state)
5. **Watch for patterns:** Regular patterns suggest automation or protocols
6. **Verify assumptions:** Check if address is what you think it is
7. **Use archive wisely:** Archive queries are expensive, use strategically

## Resources

- **Etherscan:** https://etherscan.io
- **Ethereum JSON-RPC Docs:** https://ethereum.github.io/execution-apis/api-documentation/
- **Foundry Book:** https://book.getfoundry.sh
- **Web3.py Docs:** https://web3py.readthedocs.io
- **Ethereum Yellow Paper:** https://ethereum.github.io/yellowpaper/paper.pdf