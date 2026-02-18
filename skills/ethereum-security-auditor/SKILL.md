---
name: ethereum-security-auditor
description: Security analysis and vulnerability detection for Ethereum smart contracts. Use when users want security audits, vulnerability scans, code reviews, or risk assessments of smart contracts. Triggers include security review, audit contract, find vulnerabilities, or check for exploits.
---

# Ethereum Security Auditor

Comprehensive security analysis of smart contracts including automated scanning, manual review patterns, and vulnerability detection.

## When to Use This Skill

Use this skill when the user wants to:
- Perform security audit of a smart contract
- Identify vulnerabilities and security issues
- Review access control mechanisms
- Analyze upgrade patterns and risks
- Check for common vulnerability patterns
- Assess centralization and trust assumptions
- Review recent exploits or incidents
- Generate security assessment reports

## Prerequisites

- Slither for static analysis (`pip install slither-analyzer`)
- Mythril for symbolic execution (optional: `pip install mythril`)
- Solidity compiler matching contract version
- Contract source code (verified contracts preferred)
- Understanding of common vulnerabilities

## Security Analysis Workflow

### Step 1: Obtain Contract Source

**For verified contracts:**
```bash
# Fetch from Etherscan
curl "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=<ADDRESS>&apikey=<KEY>"
```

**For unverified contracts:**
- Attempt decompilation (results may be unreliable)
- Use https://library.dedaub.com/decompile
- Focus on bytecode-level analysis

**Prepare source for analysis:**
1. Save source code to files
2. Identify compiler version
3. Install matching solc version
4. Resolve dependencies

### Step 2: Automated Security Scanning

**Run Slither (Static Analysis):**

```bash
# Basic scan
slither <CONTRACT_FILE>

# With specific checks
slither <CONTRACT_FILE> --detect reentrancy-eth,unprotected-upgrade,suicidal

# Generate detailed report
slither <CONTRACT_FILE> --json slither-report.json

# Check for specific detector
slither <CONTRACT_FILE> --detect <DETECTOR_NAME>
```

**Common Slither detectors:**
- `reentrancy-eth` - Reentrancy vulnerabilities
- `unprotected-upgrade` - Unprotected upgrade functions
- `suicidal` - Unprotected selfdestruct
- `arbitrary-send-eth` - Arbitrary ETH sending
- `controlled-delegatecall` - Controllable delegatecall
- `uninitialized-state` - Uninitialized state variables
- `tx-origin` - Dangerous use of tx.origin
- `unchecked-transfer` - Unchecked ERC20 transfers

**Run Mythril (Symbolic Execution - Optional):**

```bash
# Analyze contract
myth analyze <CONTRACT_FILE>

# With specific modules
myth analyze <CONTRACT_FILE> --modules delegatecall,ether_thief

# Analyze deployed contract
myth analyze --address <CONTRACT_ADDRESS> --rpc <RPC_URL>
```

**Document findings:**
- Severity: Critical, High, Medium, Low, Informational
- Category: Reentrancy, Access Control, etc.
- Location: Contract, function, line number
- Description: What the issue is
- Recommendation: How to fix it

### Step 3: Manual Vulnerability Review

Systematic checklist of common vulnerabilities:

#### 3.1 Reentrancy Vulnerabilities

**Pattern to check:**
```solidity
// VULNERABLE: Classic reentrancy
function withdraw() external {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");  // External call
    require(success);
    balances[msg.sender] = 0;  // State update AFTER call
}

// SAFE (Checks-Effects-Interactions)
function withdraw() external {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // State update BEFORE call
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
}

// SAFE (ReentrancyGuard)
function withdraw() external nonReentrant {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] = 0;
}
```

**Check for:**
- External calls followed by state changes
- Missing reentrancy guards
- **Read-only reentrancy** in view functions (critical for ERC4626, Curve LP tokens):
  ```solidity
  // VULNERABLE: Read-only reentrancy
  function getPrice() external view returns (uint) {
      uint lpSupply = lpToken.totalSupply();  // Can be manipulated during reentrancy
      uint reserves = getReserves();
      return reserves / lpSupply;  // Inflated price
  }
  ```
- Cross-function reentrancy (reentering through different function)
- Cross-contract reentrancy (reentering through related contract)

#### 3.2 Access Control Issues

**Patterns to check:**
```solidity
// Check for unprotected functions
function setOwner(address newOwner) external {
    // MISSING: require(msg.sender == owner);
    owner = newOwner;
}

// Check for weak access control
function criticalFunction() external {
    // WEAK: require(tx.origin == owner);  // Use msg.sender instead
    // BETTER: require(msg.sender == owner);
}

// Check for proper role management
// GOOD: Use OpenZeppelin AccessControl
contract MyContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    function criticalFunction() external onlyRole(ADMIN_ROLE) {
        // ...
    }
}
```

**Review:**
- Owner/admin functions have proper modifiers
- No use of tx.origin for authentication
- Role-based access control is properly implemented
- Constructor sets owner correctly
- Ownership transfer is two-step process

#### 3.3 Integer Overflow/Underflow

**For Solidity < 0.8.0:**
```solidity
// VULNERABLE (Solidity < 0.8.0)
function vulnerable(uint256 a, uint256 b) public pure returns (uint256) {
    return a + b;  // Can overflow
}

// SAFE
function safe(uint256 a, uint256 b) public pure returns (uint256) {
    return a.add(b);  // SafeMath
}
```

**Check:**
- Solidity version (0.8.0+ has built-in overflow protection)
- Use of SafeMath for older versions
- Unchecked blocks in 0.8.0+ (deliberate)

#### 3.4 Unchecked External Calls

**Patterns:**
```solidity
// VULNERABLE: Unchecked call
token.transfer(recipient, amount);  // Return value not checked

// SAFE
require(token.transfer(recipient, amount), "Transfer failed");

// BETTER: Use SafeERC20
SafeERC20.safeTransfer(token, recipient, amount);
```

**ERC20 approve race condition:**
```solidity
// VULNERABLE: Approval race
// If user calls approve(spender, 100) then approve(spender, 50)
// Spender can front-run second tx and transfer 100, then transfer 50 = 150 total

// SAFE: Use increaseAllowance/decreaseAllowance
token.increaseAllowance(spender, 50);
token.decreaseAllowance(spender, 50);

// Or check current allowance is 0 or expected value
require(token.allowance(msg.sender, spender) == 0);
token.approve(spender, newAmount);
```

**Check for:**
- Unchecked `call`, `delegatecall`, `staticcall`
- Unchecked ERC20 `transfer` / `transferFrom` / `approve`
- Proper error handling for external calls
- Approval race conditions

#### 3.5 Denial of Service Vectors

**Gas limit DoS:**
```solidity
// VULNERABLE: Unbounded loop
function distributeRewards() external {
    for (uint i = 0; i < users.length; i++) {  // Can run out of gas
        users[i].transfer(rewards[i]);
    }
}

// BETTER: Pull over push
mapping(address => uint) public pendingRewards;

function claimReward() external {
    uint reward = pendingRewards[msg.sender];
    pendingRewards[msg.sender] = 0;
    msg.sender.transfer(reward);
}
```

**Block gas limit DoS:**
- Check for unbounded loops
- Large array operations
- Expensive computations in public functions

**Unexpected revert DoS:**
- Functions that can be blocked by reverting
- Push payment patterns vulnerable to revert

#### 3.6 Front-Running Vulnerabilities

**Patterns:**
```solidity
// VULNERABLE: Front-runnable
function buy() external payable {
    uint price = getCurrentPrice();  // Can be manipulated
    require(msg.value >= price);
    // ...
}

// BETTER: Commit-reveal or slippage protection
function buy(uint maxPrice) external payable {
    uint price = getCurrentPrice();
    require(price <= maxPrice, "Price too high");
    require(msg.value >= price);
    // ...
}
```

**Check for:**
- Price oracle manipulations
- Slippage protection in DEX interactions
- Transaction ordering dependency
- MEV extraction opportunities

#### 3.7 Delegatecall Vulnerabilities

**Dangerous patterns:**
```solidity
// VULNERABLE: User-controlled delegatecall
function execute(address target, bytes memory data) external {
    (bool success,) = target.delegatecall(data);  // DANGEROUS
    require(success);
}

// Delegatecall uses caller's storage context
// Can overwrite critical variables
```

**Check for:**
- User-controlled delegatecall targets
- Storage layout mismatches in proxies
- Unprotected delegatecall functions

#### 3.8 Oracle Manipulation

**Patterns:**
```solidity
// VULNERABLE: Single block price
function getPrice() public view returns (uint) {
    (uint reserve0, uint reserve1,) = pair.getReserves();
    return reserve1 / reserve0;  // Can be manipulated in same block
}

// BETTER: Time-weighted average price (TWAP)
function getTWAP() public view returns (uint) {
    return oracle.consult(token, amountIn, twapInterval);
}
```

**Check for:**
- Flash loan resistant pricing
- TWAP or Chainlink oracles
- Multiple oracle sources
- Price manipulation protections

#### 3.9 Timestamp Dependence

**Patterns:**
```solidity
// WEAK: Miner can manipulate ~15 seconds
function checkExpiry() public view returns (bool) {
    return block.timestamp > expiryTime;
}

// OK for longer durations (hours/days)
// RISKY for short durations (seconds/minutes)
```

**Check for:**
- Critical logic depending on `block.timestamp`
- Short time windows that miners could manipulate

#### 3.10 Signature Replay Attacks

**Patterns:**
```solidity
// VULNERABLE: Signature can be replayed
function executeWithSignature(bytes memory signature, ...) external {
    address signer = recoverSigner(signature, ...);
    require(signer == authorized);
    // Execute action
}

// SAFE: Use nonces
mapping(address => uint) public nonces;

function executeWithSignature(bytes memory signature, uint nonce, ...) external {
    require(nonces[msg.sender] == nonce);
    nonces[msg.sender]++;
    address signer = recoverSigner(signature, nonce, ...);
    require(signer == authorized);
    // Execute action
}

// BETTER: Use EIP-712 structured data
bytes32 structHash = keccak256(abi.encode(
    TYPEHASH,
    request.param1,
    request.param2,
    nonce
));
bytes32 digest = keccak256(abi.encodePacked(
    "\x19\x01",
    DOMAIN_SEPARATOR,
    structHash
));
address signer = ecrecover(digest, v, r, s);
```

**Signature malleability:**
```solidity
// VULNERABLE: Malleable signatures
function verify(bytes32 hash, uint8 v, bytes32 r, bytes32 s) {
    address signer = ecrecover(hash, v, r, s);
    require(signer == authorized);
}

// SAFE: Check s value (EIP-2)
require(uint256(s) <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0, "Invalid s");
require(v == 27 || v == 28, "Invalid v");
address signer = ecrecover(hash, v, r, s);

// BETTER: Use OpenZeppelin ECDSA library
address signer = ECDSA.recover(hash, signature);
```

**Check for:**
- Nonce or unique identifier in signatures
- EIP-712 structured data hashing for off-chain signatures
- Replay protection across chains (chain ID in signature)
- Signature malleability protection (s-value check)
- Signature expiration timestamps
- Contract address in signature (prevent cross-contract replay)

### Step 4: Proxy and Upgrade Analysis

For upgradeable contracts:

**Transparent Proxy Pattern:**
```solidity
// Check for:
// 1. Storage layout compatibility
// 2. Function selector collisions
// 3. Uninitialized implementation contracts
// 4. Proper initialization (no constructor logic)
```

**UUPS Pattern:**
```solidity
// Check for:
// 1. Upgrade function is protected
// 2. Authorization logic cannot be bypassed
// 3. Implementation has _authorizeUpgrade
```

**Beacon Pattern:**
```solidity
// Check for:
// 1. Beacon controller access control
// 2. Multiple proxies affected by upgrade
```

**Common issues:**
- Storage collisions between proxy and implementation
- **Storage layout changes between upgrades** (adding variables before existing ones)
- **Namespace collision** (function selectors clashing between proxy and implementation)
- Uninitialized implementation allowing takeover
- Missing initialization functions
- Constructor code in implementation (won't execute via proxy)
- Function selector clashes (especially in transparent proxies)
- **Storage gaps missing** in upgradeable contracts (should reserve slots for future variables)

**Storage collision example:**
```solidity
// Proxy storage
contract Proxy {
    address implementation;  // slot 0
    address admin;           // slot 1
}

// BAD Implementation (collides with proxy)
contract BadImplementation {
    uint256 public value;  // slot 0 - COLLISION with implementation address!
}

// GOOD Implementation (uses EIP-1967 slots or explicit gaps)
contract GoodImplementation {
    // Reserve slots for proxy variables
    uint256[50] private __gap;  // Reserve 50 slots
    uint256 public value;        // Safe slot
}
```

**Namespace collision check:**
```python
# Check if implementation function selector matches proxy's admin functions
# Transparent proxy: admin functions (upgrade, changeAdmin) should not clash
# with implementation functions
```

**Analyze with Slither:**
```bash
slither <CONTRACT> --detect uninitialized-storage,unprotected-upgrade,function-init-state,proxy-patterns
```

### Step 5: Economic and Game Theory Analysis

Beyond code, analyze economic security:

**Tokenomics:**
- Inflation/deflation mechanisms
- Mint/burn permissions
- Supply caps and controls
- Fee mechanisms

**Incentive alignment:**
- Are users incentivized to act honestly?
- Can malicious actors profit?
- Collateral requirements sufficient?

**Game theory attacks:**
- Governance attacks (flash loan voting)
- Oracle manipulation profitability
- MEV extraction
- Bank run scenarios

**Liquidity risks:**
- Sufficient liquidity for normal operations
- Cascading liquidation risks
- Protocol insolvency scenarios

### Step 6: Centralization and Trust Analysis

**Identify central points of control:**

1. **Admin keys:**
   - Who controls them?
   - What can they do?
   - Are they behind multisig/timelock?

2. **Upgrade permissions:**
   - Who can upgrade contracts?
   - Is there a timelock?
   - Community governance?

3. **Pause functionality:**
   - Who can pause?
   - What gets paused?
   - Emergency response plan?

4. **Parameter control:**
   - Who sets fees, rates, limits?
   - Governance or admin?

**Trust assumptions:**
- Which entities must act honestly?
- What happens if they don't?
- Single points of failure?

**Present centralization assessment:**
```
Centralization Analysis:

Admin Controls:
- Owner address: 0xabc... (EOA - HIGH RISK)
- Can: Pause protocol, change fees, upgrade contracts
- Timelock: None (CRITICAL)

Upgrade Mechanism:
- Pattern: Transparent Proxy
- Controlled by: Owner EOA
- Protection: None

Risk Level: HIGH
- Single EOA controls critical functions
- No timelock delays
- No multisig protection

Recommendations:
1. Move owner to multisig (3-of-5 or higher)
2. Implement timelock (48h minimum)
3. Establish governance process
4. Document emergency procedures
```

### Step 7: Dependency Analysis

**Review external dependencies:**

1. **Imported libraries:**
   - OpenZeppelin: Well-audited ✓
   - Custom libraries: Review carefully
   - Unmaintained libraries: Risk

2. **External contracts:**
   - Which contracts are called?
   - Are they trusted?
   - What if they're compromised/paused?

3. **Oracles:**
   - Which price feeds?
   - Single or multiple sources?
   - Fallback mechanisms?

4. **Bridges:**
   - Cross-chain dependencies
   - Canonical bridge tokens?

### Step 8: Gas Optimization Review (Secondary)

While not strictly security, inefficient gas usage can lead to DoS:

**Check for:**
- Excessive SSTORE operations
- Inefficient loops
- Redundant storage reads
- Storage vs memory usage
- Packing opportunities

## Security Report Format

Structure findings in a comprehensive report:

### Executive Summary
- Overall risk level: Critical / High / Medium / Low
- Number of issues found by severity
- Key recommendations
- Scope of audit

### Contract Overview
- Contract purpose and functionality
- Architecture and patterns used
- External dependencies

### Findings

**For each finding:**

```
[SEVERITY] Issue Title

Location: Contract.sol, function functionName(), line X

Description:
[Detailed description of the vulnerability]

Impact:
[What could happen if exploited]

Proof of Concept:
[Code example or attack scenario]

Recommendation:
[How to fix it]

References:
[Related CVEs, SWC entries, or similar exploits]
```

**Severity definitions:**
- **Critical:** Direct loss of funds, protocol can be drained
- **High:** Significant impact, theft or loss likely
- **Medium:** Limited impact, conditional exploitation
- **Low:** Minor issues, edge cases
- **Informational:** Best practices, code quality

### Automated Tool Results
- Slither findings summary
- Mythril results (if run)
- False positive analysis

### Centralization Risks
- Admin powers
- Upgrade controls
- Trust assumptions

### Recommendations
1. Priority fixes
2. Best practice improvements
3. Monitoring suggestions

## Common Vulnerability Categories (SWC Registry)

Reference: https://swcregistry.io/

- SWC-101: Integer Overflow and Underflow
- SWC-102: Outdated Compiler Version
- SWC-103: Floating Pragma
- SWC-104: Unchecked Call Return Value
- SWC-105: Unprotected Ether Withdrawal
- SWC-106: Unprotected SELFDESTRUCT
- SWC-107: Reentrancy
- SWC-108: State Variable Default Visibility
- SWC-109: Uninitialized Storage Pointer
- SWC-110: Assert Violation
- SWC-111: Use of Deprecated Functions
- SWC-112: Delegatecall to Untrusted Callee
- SWC-113: DoS with Failed Call
- SWC-114: Transaction Order Dependence
- SWC-115: Authorization through tx.origin
- SWC-116: Timestamp Dependence
- SWC-120: Weak Sources of Randomness
- SWC-123: Requirement Violation
- SWC-125: Incorrect Inheritance Order

## Historical Exploit Patterns

Learn from past exploits:

**Famous exploits:**
1. **The DAO (2016):** Reentrancy, $60M stolen
2. **Parity Multisig (2017):** Uninitialized proxy, $150M frozen
3. **bZx (2020):** Flash loan attack, $350k
4. **Harvest Finance (2020):** Flash loan arbitrage, $24M
5. **Poly Network (2021):** Access control, $600M (returned)
6. **Wormhole (2022):** Signature verification, $320M
7. **Euler Finance (2023):** Donation attack, $200M

**Pattern recognition:**
- Flash loan enabled attacks
- Oracle manipulation
- Reentrancy variants
- Access control failures
- Logic errors in complex protocols

## Integration with Other Skills

**Chain to other skills:**
- Before auditing → invoke `ethereum-contract-analyzer` for context
- For analyzing exploits → invoke `ethereum-transaction-inspector`
- For understanding protocol → invoke `ethereum-defi-analyzer`
- For on-chain verification → invoke `ethereum-chain-explorer`

## Common Commands Reference

```bash
# Slither analysis
slither <CONTRACT_FILE>
slither <CONTRACT_FILE> --detect <DETECTOR>
slither <CONTRACT_FILE> --json report.json

# Mythril analysis
myth analyze <CONTRACT_FILE>
myth analyze --address <ADDRESS> --rpc <RPC>

# Solidity compiler
solc --version
solc --optimize --bin --abi <CONTRACT_FILE>

# Check for known issues
# Use https://github.com/crytic/not-so-smart-contracts
```

## Tips for Effective Security Review

1. **Assume malicious actors:** Think like an attacker
2. **Check assumptions:** Verify all invariants
3. **Test edge cases:** Boundaries, zero values, max values
4. **Follow the money:** Trace all value flows
5. **Trust but verify:** Even audited code can have issues
6. **Consider composability:** How do contracts interact?
7. **Think economically:** Is it profitable to attack?
8. **Stay updated:** New attack vectors emerge constantly
9. **Use multiple tools:** Different tools catch different issues
10. **Manual review essential:** Automated tools miss logic errors

## False Positive Analysis

Not all tool findings are real issues:

**Common false positives:**
- Slither warnings in known-safe patterns
- View function reentrancy (if truly read-only)
- Intentional unchecked blocks (0.8.0+)
- Admin functions flagged as centralized (expected)

**Always verify:**
- Understand the context
- Check if protection exists elsewhere
- Verify exploitability

## Resources

**Tools:**
- Slither: https://github.com/crytic/slither
- Mythril: https://github.com/ConsenSys/mythril
- Echidna (fuzzing): https://github.com/crytic/echidna
- Manticore: https://github.com/trailofbits/manticore

**References:**
- SWC Registry: https://swcregistry.io/
- Smart Contract Security Best Practices: https://consensys.github.io/smart-contract-best-practices/
- DeFi Threat Matrix: https://github.com/manifoldfinance/defi-threat
- Rekt News: https://rekt.news (exploit analyses)

**Learning:**
- Ethernaut (CTF): https://ethernaut.openzeppelin.com/
- Damn Vulnerable DeFi: https://www.damnvulnerabledefi.xyz/
- Secureum: https://secureum.substack.com/