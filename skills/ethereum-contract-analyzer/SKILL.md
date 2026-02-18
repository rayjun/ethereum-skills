---
name: ethereum-contract-analyzer
description: Analyze Ethereum smart contracts from source code, bytecode, ABI, and storage layout. Use when users want to understand contract functionality, structure, patterns, or standards compliance. Triggers include requests to analyze contracts, explain contract code, decode ABIs, or identify contract patterns.
---

# Ethereum Contract Analyzer

Comprehensive analysis of Ethereum smart contracts including source code structure, ABI decoding, pattern recognition, and standards compliance.

## When to Use This Skill

Use this skill when the user wants to:
- Analyze a smart contract by address or source code
- Understand contract functionality and structure
- Decode and explain ABI (Application Binary Interface)
- Identify contract patterns (proxy, upgradeable, ERC standards)
- Extract contract dependencies and imports
- Analyze contract bytecode or opcodes
- Understand contract storage layout

## Prerequisites

Before starting analysis, ensure:
- Web3 Python library is available (`pip install web3 eth-abi eth-utils`)
- Etherscan API key is configured (for fetching verified source)
- RPC endpoint is available (for on-chain data)

## Analysis Workflow

### Step 1: Identify Contract Source

**If given contract address:**
1. Use Etherscan API to fetch verified source code
2. Extract compiler version and optimization settings
3. Fetch ABI and creation bytecode
4. Get contract creation transaction

**If given source code directly:**
1. Parse the Solidity/Vyper code
2. Extract pragma and imports
3. Identify contract structure

**Commands:**
```bash
# Fetch contract from Etherscan
curl "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=<ADDRESS>&apikey=<KEY>"

# Or use cast (Foundry)
cast code <ADDRESS> --rpc-url <RPC_URL>
cast interface <ADDRESS> --rpc-url <RPC_URL>
```

### Step 2: Structural Analysis

Analyze the contract structure:

1. **Identify contract type:**
   - Regular contract
   - Abstract contract
   - Library
   - Interface
   - Proxy contract

2. **Extract components:**
   - State variables (public, private, immutable, constant)
   - Functions (public, external, internal, private)
   - Modifiers
   - Events
   - Errors (custom errors)
   - Structs and enums
   - Inheritance hierarchy

3. **Analyze access control:**
   - Owner/admin functions
   - Role-based access control (if present)
   - Permissionless functions

**Key Questions to Answer:**
- What are the core functions and their purposes?
- What state does the contract maintain?
- How is access controlled?
- What events does it emit?

### Step 3: ABI Analysis

Decode and explain the ABI:

1. **Parse ABI JSON** to extract:
   - Function signatures and selectors
   - Input/output parameter types
   - Event signatures
   - Error signatures

2. **Categorize functions:**
   - Read-only (view/pure)
   - State-changing
   - Payable functions
   - Administrative functions

3. **Generate human-readable interface:**
   ```
   Function: transfer(address recipient, uint256 amount)
   Selector: 0xa9059cbb
   Type: Non-payable, state-changing
   Purpose: Transfer tokens to recipient
   ```

**Commands:**
```bash
# Get function selectors
cast sig "transfer(address,uint256)"

# Decode calldata
cast 4byte-decode <CALLDATA>
```

### Step 4: Pattern Recognition

Identify common patterns and standards:

1. **Token Standards:**
   - ERC20 (fungible tokens)
   - ERC20 with ERC2612 (permit/gasless approvals)
   - ERC721 (NFTs)
   - ERC721A (gas-optimized batch minting)
   - ERC1155 (multi-token)
   - ERC777 (advanced tokens with hooks)
   - ERC4626 (tokenized vaults)

2. **Proxy Patterns:**
   - Transparent proxy (EIP-1967)
   - UUPS (Universal Upgradeable Proxy Standard, EIP-1822)
   - Beacon proxy (EIP-1967)
   - Diamond proxy (EIP-2535, multi-facet)
   - Minimal proxy (EIP-1167, clone factory)
   - Metamorphic contracts (CREATE2 + selfdestruct)

3. **DeFi Patterns:**
   - Automated Market Maker (AMM)
   - Lending pool
   - Staking contract
   - Vault/strategy

4. **Access Control:**
   - Ownable
   - AccessControl (role-based)
   - Multi-sig

**Detection Checklist:**
- Check for standard interface implementations (ERC165 supportsInterface)
- Look for proxy storage slots (EIP-1967)
- Identify initialization patterns (proxies use initializers instead of constructors)
- Check for delegate calls and their targets
- Detect minimal proxy pattern (0x363d3d373d3d3d363d73...5af43d82803e903d91602b57fd5bf3)
- Check if deployed via CREATE2 (deterministic addresses)

### Step 5: Dependency Analysis

Map out contract dependencies:

1. **Direct imports:**
   - OpenZeppelin contracts
   - Custom libraries
   - Interfaces

2. **External calls:**
   - Which contracts does this call?
   - What data does it rely on?

3. **Inheritance chain:**
   - Parent contracts
   - Override analysis

### Step 6: Storage Layout Analysis

For deep analysis, examine storage:

1. **Storage slots:**
   - Use `cast storage` to inspect values
   - Map variables to slot numbers
   - Identify packed variables

2. **Proxy storage:**
   - Implementation slot (EIP-1967: `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`)
   - Admin slot (EIP-1967: `0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103`)
   - Beacon slot (EIP-1967: `0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50`)

3. **Mapping storage calculation:**
   - For `mapping(address => uint256)` at slot N:
     - Storage location = `keccak256(abi.encode(key, slot))`
   - For `mapping(uint256 => mapping(address => uint256))` at slot N:
     - Inner slot = `keccak256(abi.encode(outerKey, slot))`
     - Storage location = `keccak256(abi.encode(innerKey, innerSlot))`

4. **Array storage:**
   - Array length stored at slot N
   - Array data starts at `keccak256(slot)`
   - Element i at: `keccak256(slot) + i`

**Commands:**
```bash
# Read storage slot
cast storage <ADDRESS> <SLOT> --rpc-url <RPC_URL>

# Get implementation address for proxy (bytes32 to address, take last 20 bytes)
cast storage <PROXY_ADDRESS> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url <RPC_URL> | cast parse-bytes32-address

# Calculate mapping slot
cast index address <KEY_ADDRESS> <SLOT>
cast storage <ADDRESS> $(cast index address <KEY> <SLOT>) --rpc-url <RPC_URL>

# Calculate array element slot
cast keccak $(cast to-bytes32 <SLOT>)
```

### Step 7: Bytecode Analysis (Advanced)

For unverified contracts or deep analysis:

1. **Fetch bytecode:**
   ```bash
   cast code <ADDRESS> --rpc-url <RPC_URL>
   ```

2. **Disassemble:**
   ```bash
   # Basic disassembly with cast
   cast disassemble <BYTECODE>

   # Better decompilation with heimdall-rs (if available)
   heimdall decompile <ADDRESS> --rpc-url <RPC_URL>

   # Online decompilers (use with caution)
   # https://library.dedaub.com/decompile
   # https://ethervm.io/decompile
   ```

3. **Identify patterns:**
   - Constructor code vs runtime code (split at CODECOPY)
   - Function selectors in dispatcher (look for EQ, JUMPI pattern)
   - Proxy patterns in bytecode (DELEGATECALL usage)
   - Minimal proxy detection (specific bytecode pattern)

4. **Vyper contracts:**
   - Different bytecode structure (no function dispatcher with JUMPI)
   - Method ID table at beginning
   - Different storage layout conventions
   - Can identify by checking for Vyper-specific patterns

## Output Format

Present analysis in structured sections:

### Contract Overview
- **Address:** (if applicable)
- **Name:**
- **Type:** (Contract/Proxy/Library)
- **Compiler:** Solidity version
- **Standards:** ERC20, ERC721, etc.

### Core Functionality
Explain in plain language what the contract does.

### Key Functions
List and explain important functions:
- `functionName(params)` - Purpose and behavior

### State Variables
- Variable name and type
- Purpose and visibility

### Events
- Event signatures and purposes

### Patterns & Architecture
- Identified patterns (proxy, upgradeable, etc.)
- Inheritance structure
- Dependencies

### Access Control
- How permissions are managed
- Admin/owner functions

### Storage Analysis (if performed)
- Key storage slots and their contents

### Notes & Observations
- Interesting implementation details
- Potential areas of concern (refer to security-auditor for deep analysis)

## Integration with Other Skills

**Chain to other skills:**
- If security analysis is needed → invoke `ethereum-security-auditor`
- If contract interactions need analysis → invoke `ethereum-transaction-inspector`
- If it's a DeFi protocol → invoke `ethereum-defi-analyzer`

## Common Commands Reference

```bash
# Fetch contract source (Etherscan)
curl "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=<ADDRESS>&apikey=<KEY>"

# Get ABI (cast)
cast interface <ADDRESS> --rpc-url <RPC_URL>

# Get bytecode
cast code <ADDRESS> --rpc-url <RPC_URL>

# Get storage
cast storage <ADDRESS> <SLOT> --rpc-url <RPC_URL>

# Compute function selector
cast sig "functionName(types)"

# Decode calldata
cast 4byte-decode <CALLDATA>

# Disassemble bytecode
cast disassemble <BYTECODE>
```

## Error Handling

**Contract not verified:**
- Analyze bytecode directly
- Look for similar contracts
- Use decompilers (dedaub, ethervm) with caution

**RPC errors:**
- Check RPC endpoint connectivity
- Verify contract address
- Ensure correct network

**Missing ABI:**
- Fetch from Etherscan
- Extract from verified source
- Use 4byte directory for function signatures

## Examples

### Example 1: Analyze ERC20 Token
```
User: "Analyze the USDC token contract"

Process:
1. Identify USDC address: 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
2. Fetch source from Etherscan
3. Identify as FiatTokenV2_1 (CENTRE Consortium implementation)
4. Analyze ERC20 compliance
5. Identify additional features: minting, blacklisting, pausing
6. Document admin roles and permissions
7. Present structured analysis
```

### Example 2: Analyze Proxy Contract
```
User: "What's at address 0x... and how does it work?"

Process:
1. Fetch bytecode
2. Detect proxy pattern (presence of delegatecall)
3. Read implementation slot
4. Fetch implementation contract
5. Analyze both proxy and implementation
6. Explain upgrade mechanism
7. Document admin controls
```

## Tips for Effective Analysis

1. **Start broad, then narrow:** Get overview first, then dive into specific areas
2. **Follow the data:** Trace how state variables are modified
3. **Check standards compliance:** Use standard interfaces as checklists
4. **Look for anomalies:** Unusual patterns may indicate bugs or innovative designs
5. **Context matters:** Consider when contract was deployed and ecosystem it operates in
6. **Document assumptions:** Note what you can verify vs what you infer

## Resources

- **Solidity Documentation:** https://docs.soliditylang.org
- **EIP Standards:** https://eips.ethereum.org
- **OpenZeppelin Contracts:** https://docs.openzeppelin.com/contracts
- **4byte Directory:** https://www.4byte.directory
- **Foundry Book:** https://book.getfoundry.sh