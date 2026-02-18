---
name: ethereum-transaction-inspector
description: Deep inspection and analysis of Ethereum transactions including decoding function calls, analyzing traces, examining gas usage, and extracting token transfers. Use when users want to understand what a transaction did, debug failed transactions, or analyze transaction patterns. Triggers include transaction hash analysis, decode transaction, explain what happened, or investigate failed tx.
---

# Ethereum Transaction Inspector

Comprehensive transaction analysis including call decoding, trace analysis, gas profiling, and event extraction.

## When to Use This Skill

Use this skill when the user wants to:
- Understand what a specific transaction did
- Decode function calls and parameters
- Analyze transaction execution trace (internal calls)
- Debug failed transactions and revert reasons
- Examine gas usage patterns
- Extract token transfers and events
- Analyze transaction patterns (MEV, arbitrage, liquidations)
- Compare transactions or identify similar patterns

## Prerequisites

- Web3 Python library (`pip install web3 eth-abi eth-utils`)
- RPC endpoint with trace/debug API access (for detailed traces)
- Etherscan API key (alternative for traces and decoded data)
- Access to 4byte directory for function signature lookup

## Inspection Workflow

### Step 1: Fetch Transaction Data

Get basic transaction information:

```bash
# Using cast (Foundry)
cast tx <TX_HASH> --rpc-url <RPC_URL>

# Get transaction receipt
cast receipt <TX_HASH> --rpc-url <RPC_URL>

# Using curl (RPC)
curl -X POST <RPC_URL> \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["<TX_HASH>"],"id":1}'
```

**Extract key fields:**
- `from` - Transaction sender
- `to` - Transaction recipient (contract, EOA, or null for contract creation)
- `value` - ETH transferred
- `input` / `data` - Calldata (function call or contract creation code)
- `gas` / `gasLimit` - Gas limit set
- `gasUsed` - Actual gas consumed (from receipt)
- `gasPrice` - Legacy gas price
- `maxFeePerGas` / `maxPriorityFeePerGas` - EIP-1559 gas parameters
- `type` - Transaction type (0: legacy, 1: EIP-2930, 2: EIP-1559, 3: EIP-4844 blob)
- `accessList` - EIP-2930/2929 pre-declared storage access (type 1 & 2)
- `blobVersionedHashes` - EIP-4844 blob commitments (type 3)
- `blockNumber` / `blockHash` - Block inclusion
- `nonce` - Sender nonce
- `status` - Success (1) or failure (0) from receipt
- `v, r, s` - Signature components

### Step 2: Analyze Transaction Type

**Identify transaction type and special handling:**

1. **Contract Creation (to == null):**
   - `input` contains contract initialization code
   - Extract constructor parameters from end of input
   - Receipt contains `contractAddress` field

2. **Transaction Type Analysis:**
   - **Type 0 (Legacy):** Uses `gasPrice` only
   - **Type 1 (EIP-2930):** Adds `accessList` to pre-declare storage access
   - **Type 2 (EIP-1559):** Uses `maxFeePerGas` and `maxPriorityFeePerGas`
   - **Type 3 (EIP-4844):** Blob transactions with `blobVersionedHashes`

3. **Access List Decoding (Type 1 & 2):**
   ```json
   "accessList": [
     {
       "address": "0x...",
       "storageKeys": ["0x...", "0x..."]
     }
   ]
   ```
   - Pre-declared addresses and storage slots
   - Reduces gas cost for accessing these

### Step 3: Decode Function Call or Creation Code

**For normal transactions:**

Decode the `input` data to understand the function being called:

1. **Extract function selector** (first 4 bytes):
   ```bash
   # First 10 characters (0x + 8 hex chars)
   echo "0xa9059cbb..."
   ```

2. **Look up function signature:**
   ```bash
   # Using cast
   cast 4byte <SELECTOR>

   # Or query 4byte.directory
   curl "https://www.4byte.directory/api/v1/signatures/?hex_signature=<SELECTOR>"

   # Or use openchain signature database
   curl "https://api.openchain.xyz/signature-database/v1/lookup?function=<SELECTOR>"
   ```

3. **Decode parameters:**
   ```bash
   # Using cast
   cast 4byte-decode <CALLDATA>

   # Or manually using abi-decode
   cast abi-decode "functionName(types)" <DATA>
   ```

**For contract creation:**
- Extract init code and constructor arguments
- Identify contract type from bytecode patterns
- Match against known contract patterns (proxies, tokens, etc.)

**Example:**
```
Calldata: 0xa9059cbb000000000000000000000000abc123...0000000000000000000000000000000000000001

Decoded:
Function: transfer(address,uint256)
Parameters:
  - recipient: 0xabc123...
  - amount: 1
```

### Step 4: Fetch and Analyze Transaction Receipt

The receipt contains execution results:

```bash
cast receipt <TX_HASH> --rpc-url <RPC_URL>
```

**Key receipt fields:**
- `status` - 1 (success) or 0 (failure)
- `gasUsed` - Actual gas consumed
- `logs` - Events emitted
- `logsBloom` - Bloom filter for logs
- `effectiveGasPrice` - Actual gas price paid (EIP-1559: baseFee + priorityFee)
- `cumulativeGasUsed` - Total gas used in block up to this transaction
- `contractAddress` - If contract creation, the new contract address
- `blobGasUsed` / `blobGasPrice` - For EIP-4844 blob transactions

### Step 4: Decode Events/Logs

Events provide insights into state changes:

1. **Extract event logs** from receipt

2. **For each log:**
   - `address` - Contract that emitted the event
   - `topics[0]` - Event signature hash
   - `topics[1-3]` - Indexed parameters
   - `data` - Non-indexed parameters

3. **Decode events:**
   ```bash
   # Compute event signature hash
   cast keccak "Transfer(address,address,uint256)"

   # Decode event data
   cast abi-decode "Transfer(address,address,uint256)" <DATA>
   ```

**Common events:**
- `Transfer(address,address,uint256)` - ERC20/721 transfers
- `Approval(address,address,uint256)` - Token approvals
- `Swap(...)` - DEX swaps
- `Deposit(address,uint256)` - Deposits to contracts

### Step 5: Trace Transaction Execution

For deep analysis, fetch execution trace:

**Method 1: Using debug_traceTransaction**
```bash
# Get full trace
cast run <TX_HASH> --rpc-url <RPC_URL> --trace

# Using curl
curl -X POST <RPC_URL> \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"debug_traceTransaction","params":["<TX_HASH>",{"tracer":"callTracer"}],"id":1}'
```

**Method 2: Using Etherscan**
```bash
curl "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=<TX_HASH>&apikey=<KEY>"
```

**Trace analysis reveals:**
- Internal contract calls (CALL, DELEGATECALL, STATICCALL)
- Call hierarchy and depth
- Input and output of each call
- Gas usage per call
- Where reverts occurred (for failed transactions)

**Call types:**
- `CALL` - Regular contract call (with value transfer)
- `STATICCALL` - Read-only call (cannot modify state)
- `DELEGATECALL` - Call in caller's context (used by proxies)
- `CREATE` / `CREATE2` - Contract creation

### Step 6: Analyze Gas Usage

Break down where gas was spent:

1. **Base transaction cost:** 21,000 gas
2. **Calldata cost:**
   - 4 gas per zero byte
   - 16 gas per non-zero byte
3. **Execution cost:** Opcodes executed
4. **Storage operations:** SSTORE (20,000 gas for new slot, 5,000 for update)

**Gas analysis questions:**
- What are the most expensive operations?
- Are there optimization opportunities?
- Is gas usage expected for this type of transaction?

```bash
# Profile gas usage with trace
cast run <TX_HASH> --rpc-url <RPC_URL> --debug
```

### Step 7: Extract Token Transfers

Identify all token movements:

1. **From events:**
   - ERC20: Look for `Transfer(address,address,uint256)` events
   - ERC721: `Transfer(address,address,uint256)` with tokenId
   - ERC1155: `TransferSingle` and `TransferBatch`

2. **From traces:**
   - ETH transfers in `value` fields of calls
   - Internal transfers via traces

**Output format:**
```
Token Transfers:
1. 100 USDC from 0xaaa... to 0xbbb...
2. 0.5 WETH from 0xbbb... to 0xccc...
3. 1.2 ETH from 0xccc... to 0xddd...
```

### Step 8: Analyze Failed Transactions

For failed transactions (status = 0):

1. **Identify revert point** in trace
2. **Extract revert reason:**
   ```bash
   cast run <TX_HASH> --rpc-url <RPC_URL> --trace
   ```

3. **Common failure reasons:**
   - Out of gas
   - Require/assert failures
   - Custom errors
   - Arithmetic errors (overflow/underflow in older Solidity)
   - Reentrancy guards
   - Access control violations

4. **Decode revert reason:**
   - If custom error: decode error selector and parameters
   - If string: decode UTF-8 message
   - If empty: likely out of gas or assert

**Example:**
```
Revert reason: "ERC20: transfer amount exceeds balance"
Reverted at: Contract 0xabc..., function transfer()
```

## Output Format

Present transaction analysis in structured sections:

### Transaction Summary
- **Hash:**
- **Status:** Success / Failed
- **Block:** #number (timestamp)
- **From:** address
- **To:** address (contract name if known)
- **Value:** ETH amount

### Function Call
- **Function:** `functionName(parameters)`
- **Decoded Parameters:**
  - param1: value
  - param2: value

### Execution Overview
Brief narrative of what happened:
"This transaction called the `swap` function on Uniswap V3, exchanging 1,000 USDC for 0.285 WETH. The swap went through two pools (USDC/WETH direct pool) and emitted 3 events."

### Events Emitted
List key events with decoded parameters:
1. **Transfer** (USDC: 0xaaa...)
   - from: 0xuser...
   - to: 0xpool...
   - amount: 1,000 USDC

### Token Transfers
Summary of all token movements:
- 1,000 USDC from User → Pool
- 0.285 WETH from Pool → User

### Internal Calls (if complex)
Call tree showing contract interactions:
```
1. User → Uniswap Router: swap()
   ├─ 2. Router → USDC: transferFrom()
   ├─ 3. Router → Pool: swap()
   │  └─ 4. Pool → WETH: transfer()
   └─ 5. Router → WETH: transfer()
```

### Gas Analysis
- **Gas Limit:** amount
- **Gas Used:** amount (percentage of limit)
- **Gas Price:** price in Gwei
- **Total Cost:** ETH cost
- **Efficiency notes:** (if notable)

### Storage Changes (if available)
- Contract: storage slot changes
- Before → After values

### Failed Transaction Details (if applicable)
- **Revert Reason:** message or error
- **Failed At:** contract and function
- **Explanation:** why it failed

### Notes & Observations
- Interesting patterns
- Potential issues or risks
- MEV activity (if detected)

## Advanced Analysis

### Pattern Recognition

Identify common transaction patterns:

1. **DEX Swaps:**
   - Single swap: A → B
   - Multi-hop: A → B → C
   - Split routes: Parallel swaps

2. **Arbitrage:**
   - Buy on DEX1, sell on DEX2
   - Flash loan → trade → repay

3. **Liquidations:**
   - Identify liquidation functions
   - Extract collateral and debt

4. **MEV:**
   - Sandwich attacks (front-run, victim, back-run)
   - Flash bots bundles

### Transaction Comparison

When comparing multiple transactions:
1. Identify similarities and differences
2. Look for patterns in parameters
3. Compare gas usage
4. Track same actors across transactions

### Time-Series Analysis

For analyzing multiple related transactions:
1. Track state evolution
2. Identify trends
3. Calculate rates (volume, frequency)

## Integration with Other Skills

**Chain to other skills:**
- If contract analysis is needed → invoke `ethereum-contract-analyzer`
- If DeFi protocol understanding is needed → invoke `ethereum-defi-analyzer`
- If security concerns arise → invoke `ethereum-security-auditor`
- For broader pattern analysis → invoke `ethereum-chain-explorer`

## Common Commands Reference

```bash
# Basic transaction info
cast tx <TX_HASH> --rpc-url <RPC_URL>
cast receipt <TX_HASH> --rpc-url <RPC_URL>

# Decode calldata
cast 4byte-decode <CALLDATA>
cast abi-decode "function(types)" <DATA>

# Lookup function signature
cast 4byte <SELECTOR>

# Trace transaction
cast run <TX_HASH> --rpc-url <RPC_URL> --trace

# Compute event signature
cast keccak "EventName(types)"

# Decode event data
cast abi-decode "EventName(types)" <DATA>

# Get block timestamp
cast block <BLOCK_NUMBER> --rpc-url <RPC_URL>

# Pretty print trace
cast run <TX_HASH> --rpc-url <RPC_URL> --debug
```

## Error Handling

**Transaction not found:**
- Verify transaction hash
- Check if mempool transaction (not yet mined)
- Ensure correct network

**Trace unavailable:**
- Node may not support debug API
- Try Etherscan API as fallback
- Use basic receipt for partial analysis

**Decode failures:**
- Function signature not in 4byte directory
- Custom ABI needed
- Analyze bytecode to infer structure

## Examples

### Example 1: Simple ERC20 Transfer
```
User: "What did transaction 0x123... do?"

Process:
1. Fetch transaction data
2. Decode: transfer(recipient, amount)
3. Extract Transfer event
4. Present: "Transferred 100 USDC to 0xabc..."
```

### Example 2: Complex DeFi Transaction
```
User: "Explain this Uniswap transaction 0x456..."

Process:
1. Fetch transaction and receipt
2. Decode multicall with multiple swaps
3. Trace internal calls
4. Extract all Transfer events
5. Build token flow diagram
6. Calculate effective exchange rate
7. Present comprehensive analysis
```

### Example 3: Failed Transaction Debug
```
User: "Why did my transaction fail? 0x789..."

Process:
1. Confirm status = 0
2. Trace execution
3. Find revert point
4. Extract revert reason: "Insufficient balance"
5. Explain context
6. Suggest fix
```

## Tips for Effective Inspection

1. **Start with receipt:** Status and events give quick overview
2. **Decode systematically:** Function → Events → Trace
3. **Follow the value:** Track ETH and token flows
4. **Check timestamps:** Context matters (price movements, network congestion)
5. **Look for patterns:** Similar transactions may reveal intent
6. **Verify assumptions:** Cross-reference with block explorer
7. **Consider gas:** Unusual gas usage indicates complexity or issues

## Resources

- **4byte Directory:** https://www.4byte.directory
- **Etherscan:** https://etherscan.io
- **Foundry Book:** https://book.getfoundry.sh
- **Ethereum JSON-RPC Spec:** https://ethereum.github.io/execution-apis/api-documentation/
- **EVM Opcodes:** https://www.evm.codes/