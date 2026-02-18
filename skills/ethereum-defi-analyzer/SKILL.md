---
name: ethereum-defi-analyzer
description: Analyze DeFi protocols, liquidity pools, lending markets, yield strategies, and token economics. Use when users want to understand DeFi protocols, analyze liquidity positions, calculate yields, or investigate DeFi transactions. Triggers include analyzing DEX pools, checking lending rates, understanding DeFi protocols, or calculating DeFi metrics.
---

# Ethereum DeFi Analyzer

Comprehensive analysis of DeFi protocols including DEXs, lending platforms, yield strategies, and token economics.

## When to Use This Skill

Use this skill when the user wants to:
- Analyze DEX liquidity pools and trading pairs
- Understand lending/borrowing protocols
- Calculate yields and APY/APR
- Analyze token economics and price mechanics
- Investigate DeFi transactions and strategies
- Track TVL (Total Value Locked) and protocol metrics
- Understand protocol mechanisms and parameters
- Analyze arbitrage opportunities
- Investigate yield farming strategies

## Prerequisites

- Web3 Python library with DeFi-specific utilities
- RPC endpoint for on-chain data
- Etherscan API for contract verification
- TheGraph API access (optional, for indexed data)
- Understanding of DeFi primitives (AMM, lending, etc.)

## DeFi Protocol Categories

### 1. Decentralized Exchanges (DEXs)
- **Uniswap V2/V3** - AMM with concentrated liquidity (V3)
- **Curve** - Stableswap AMM
- **Balancer** - Weighted pools
- **SushiSwap** - Fork of Uniswap V2
- **1inch** - DEX aggregator

### 2. Lending Protocols
- **Aave** - Over-collateralized lending
- **Compound** - Algorithmic money market
- **MakerDAO** - CDP-based stablecoin
- **Spark** - Maker's lending protocol

### 3. Liquid Staking
- **Lido** - stETH
- **Rocket Pool** - rETH
- **Frax** - frxETH

### 4. Yield Aggregators
- **Yearn Finance** - Automated yield strategies
- **Convex** - Curve boost optimization
- **Beefy Finance** - Multi-chain vaults

### 5. Derivatives
- **GMX** - Perpetual trading
- **Synthetix** - Synthetic assets
- **dYdX** - Decentralized exchange with perpetuals

## Analysis Workflows

### Workflow 1: Analyze DEX Liquidity Pool

**Example: Uniswap V2 Pool**

**Step 1: Identify pool contract**
```bash
# Find pool address from factory
cast call <UNISWAP_V2_FACTORY> "getPair(address,address)(address)" <TOKEN0> <TOKEN1> --rpc-url <RPC_URL>

# Common factories:
# Uniswap V2: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
# Sushiswap: 0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac
```

**Step 2: Get pool reserves**
```bash
# Call getReserves()
cast call <POOL_ADDRESS> "getReserves()(uint112,uint112,uint32)" --rpc-url <RPC_URL>
```

**Step 3: Calculate pool metrics**
```python
# Price calculation
price_token0_in_token1 = reserve1 / reserve0
price_token1_in_token0 = reserve0 / reserve1

# Total liquidity (in terms of one token)
liquidity_in_token0 = reserve0 * 2  # Assuming balanced pool
liquidity_in_token1 = reserve1 * 2

# Get total LP supply
total_lp = cast_call(pool, "totalSupply()(uint256)")
```

**Step 4: Get fee tier**
```bash
# Uniswap V2: 0.3% fixed
# Uniswap V3: Check fee parameter
cast call <POOL_V3> "fee()(uint24)" --rpc-url <RPC_URL>
# Returns: 500 (0.05%), 3000 (0.3%), 10000 (1%)
```

**Step 5: Calculate trading volume** (requires historical data)
```bash
# Using TheGraph or Etherscan for events
# Or track Swap events
cast logs --from-block <START> --to-block <END> --address <POOL> "Swap(address,uint256,uint256,uint256,uint256,address)" --rpc-url <RPC_URL>
```

**Present pool analysis:**
```
Uniswap V2: USDC/WETH Pool
Address: 0xabc...

Reserves:
- USDC: 50,000,000 ($50M)
- WETH: 20,000 ($40M at $2,000/ETH)

Price:
- 1 WETH = 2,500 USDC
- 1 USDC = 0.0004 WETH

Pool Metrics:
- Total Liquidity: $90M
- LP Token Supply: 1,897,366
- Fee Tier: 0.3%
- 24h Volume: $15M (estimated)
- 24h Fees: $45,000 (0.3% of volume)

Pool Share Analysis:
- 1 LP token = $47.44
- 1 LP token represents:
  - 26.36 USDC
  - 0.0105 WETH

APR Estimate:
- Fee APR: 18.25% (based on 24h volume)
- Note: Subject to impermanent loss
```

**Example: Uniswap V3 Pool (Concentrated Liquidity)**

**Additional V3 metrics:**
```bash
# Get current tick and sqrtPriceX96
cast call <POOL_V3> "slot0()(uint160,int24,uint16,uint16,uint16,uint8,bool)" --rpc-url <RPC_URL>
# Returns: sqrtPriceX96, tick, observationIndex, observationCardinality, observationCardinalityNext, feeProtocol, unlocked

# Get liquidity
cast call <POOL_V3> "liquidity()(uint128)" --rpc-url <RPC_URL>
```

**V3 Price Calculation:**
```python
# From sqrtPriceX96 to price:
# price = (sqrtPriceX96 / 2^96)^2

# Example:
sqrtPriceX96 = 1252685732681638336329256503349  # from slot0
price = (sqrtPriceX96 / (2**96))**2
# Adjust for token decimals if needed

# From tick to price:
# price = 1.0001^tick

# Example:
tick = 201200
price = 1.0001**tick ≈ 7363.5  # USDC per WETH
```

**V3-specific analysis:**
- Current tick and price
- Active liquidity at current price
- Liquidity distribution across ticks (requires tick bitmap analysis)
- Fee tier and protocol fees
- Position-specific analysis (if position NFT provided)
  - Position's tick range (tickLower, tickUpper)
  - Liquidity amount
  - Uncollected fees
  - In-range vs out-of-range status

**Analyze specific V3 position:**
```bash
# Get position details from NFT
cast call <NONFUNGIBLE_POSITION_MANAGER> "positions(uint256)" <TOKEN_ID> --rpc-url <RPC_URL>
# Returns: nonce, operator, token0, token1, fee, tickLower, tickUpper, liquidity, feeGrowthInside0LastX128, feeGrowthInside1LastX128, tokensOwed0, tokensOwed1
```

### Workflow 2: Analyze Curve Pool (Stableswap)

Curve uses different math for stablecoin swaps:

**Step 1: Identify pool**
```bash
# Curve pools are registered in registry
# Common pools: 3pool (DAI/USDC/USDT), etc.
```

**Step 2: Get balances**
```bash
# Curve pools have multiple coins
cast call <CURVE_POOL> "balances(uint256)(uint256)" 0 --rpc-url <RPC_URL>  # Coin 0
cast call <CURVE_POOL> "balances(uint256)(uint256)" 1 --rpc-url <RPC_URL>  # Coin 1
cast call <CURVE_POOL> "balances(uint256)(uint256)" 2 --rpc-url <RPC_URL>  # Coin 2
```

**Step 3: Get A parameter**
```bash
# Amplification coefficient (affects curve)
cast call <CURVE_POOL> "A()(uint256)" --rpc-url <RPC_URL>
```

**Step 4: Calculate virtual price**
```bash
cast call <CURVE_POOL> "get_virtual_price()(uint256)" --rpc-url <RPC_URL>
# Virtual price > 1e18 means pool has accrued fees
```

**Present Curve analysis:**
```
Curve 3pool (DAI/USDC/USDT)
Address: 0xabc...

Balances:
- DAI: 150M
- USDC: 180M
- USDT: 170M
- Total: $500M

Parameters:
- A: 2000 (high A = tighter peg)
- Fee: 0.04%
- Admin Fee: 50% of trading fees

Virtual Price: 1.025
- Indicates 2.5% cumulative fees earned

LP Token Value:
- 1 LP ≈ $1.025

APR:
- Base fee APR: 3.5%
- CRV rewards: 2.1%
- Total APR: 5.6%
```

### Workflow 3: Analyze Lending Protocol (Aave/Compound)

**Step 1: Identify market**
```bash
# Aave V3: Get asset data
cast call <AAVE_POOL> "getReserveData(address)" <ASSET> --rpc-url <RPC_URL>

# Returns: configuration, liquidityIndex, variableBorrowIndex, currentLiquidityRate, currentVariableBorrowRate, etc.
```

**Step 2: Get supply and borrow rates**
```bash
# Supply APY (lending rate)
cast call <AAVE_POOL> "getReserveData(address)" <ASSET> --rpc-url <RPC_URL>
# Extract currentLiquidityRate (in Ray units: 1e27)

# Convert Ray to APY:
# 1. Divide by 1e27 to get per-second rate
# 2. APY = (1 + ratePerSecond)^31536000 - 1
# Approximation: APY ≈ rate / 1e27 (for small rates)

# Borrow APY
# Extract currentVariableBorrowRate, same conversion
```

**Ray units example:**
```
currentLiquidityRate = 28000000000000000000000000 (Ray)
rate_per_second = 28000000000000000000000000 / 1e27 = 0.028
APY ≈ 2.8% (simplified)
Exact: APY = (1 + 0.028/31536000)^31536000 - 1 ≈ 2.838%
```

**Step 3: Calculate utilization**
```python
utilization = total_borrows / total_liquidity
# High utilization = higher rates
```

**Step 4: Check collateral factors and liquidation thresholds**
```bash
# LTV (Loan-to-Value), Liquidation Threshold, Liquidation Bonus
# Encoded in configuration
```

**Step 5: Analyze specific position** (if address provided)
```bash
# Get user account data
cast call <AAVE_POOL> "getUserAccountData(address)" <USER_ADDRESS> --rpc-url <RPC_URL>
# Returns: totalCollateralBase, totalDebtBase, availableBorrowsBase, currentLiquidationThreshold, ltv, healthFactor
```

**Present lending analysis:**
```
Aave V3: USDC Market
Address: 0xabc...

Market Overview:
- Total Supply: $500M
- Total Borrows: $350M
- Utilization: 70%

Interest Rates:
- Supply APY: 2.8%
- Variable Borrow APY: 4.5%
- Stable Borrow APY: 5.2%

Parameters:
- LTV: 80% (can borrow up to 80% of collateral value)
- Liquidation Threshold: 85%
- Liquidation Penalty: 5%

Incentives:
- Supply rewards: 0.5% in stkAAVE
- Borrow rewards: 0.3% in stkAAVE

User Position (0xuser...):
- Supplied: $100,000 USDC
- Borrowed: $50,000 USDT
- Health Factor: 1.6 (safe, >1 required)
- Available to borrow: $30,000
- Current yield: 2.8% on supply - 4.5% on borrow = -1.7% net cost
```

**Health Factor Analysis:**
```
Health Factor = (Collateral * Liquidation Threshold) / Total Borrows

Example:
- Collateral: $100,000 USDC
- Liquidation Threshold: 85%
- Borrows: $50,000 USDT
- Health Factor: ($100,000 * 0.85) / $50,000 = 1.7

Interpretation:
- HF > 1: Safe position
- HF = 1: At liquidation threshold
- HF < 1: Position can be liquidated

Liquidation Price:
- Calculate price drop needed to reach HF = 1
```

### Workflow 4: Analyze Liquid Staking (Lido Example)

**Step 1: Get stETH/ETH rate**
```bash
# Lido: stETH
cast call <LIDO> "getPooledEthByShares(uint256)(uint256)" 1000000000000000000 --rpc-url <RPC_URL>
# Input: 1e18 (1 share), Output: current ETH value
```

**Step 2: Get total metrics**
```bash
# Total ETH staked
cast call <LIDO> "getTotalPooledEther()(uint256)" --rpc-url <RPC_URL>

# Total shares
cast call <LIDO> "getTotalShares()(uint256)" --rpc-url <RPC_URL>
```

**Step 3: Calculate APR**
```python
# Track exchange rate change over time
current_rate = pooled_eth / total_shares
# Compare to historical rate
apr = (current_rate / historical_rate - 1) * (365 / days_elapsed)
```

**Step 4: Analyze withdrawal queue** (if withdrawals are queued)
```bash
# Check withdrawal request status
cast call <LIDO_WITHDRAWAL> "getWithdrawalStatus(uint256[])(tuple[])" [<REQUEST_ID>] --rpc-url <RPC_URL>
```

**Present staking analysis:**
```
Lido: stETH
Address: 0xae7ab96520de3a18e5e111b5eaab095312d7fe84

Metrics:
- Total ETH Staked: 8,500,000 ETH ($17B)
- Total stETH Supply: 8,475,000
- Exchange Rate: 1 stETH = 1.003 ETH
- Market Share: 28.5% of all staked ETH

APR:
- Staking APR: 3.8%
- Fee: 10% (0.38% to Lido)
- Net APR: 3.42%

Peg Status:
- stETH/ETH Price: 0.999 (-0.1% depeg)
- Curve Pool Liquidity: $500M
- Secondary market: Healthy

Withdrawals:
- Queue Length: 1,234 requests
- Estimated Wait: 3-5 days
```

### Workflow 5: Calculate Yield Farming Returns

**Step 1: Identify yield sources**
- Trading fees (LP positions)
- Lending interest
- Protocol incentive tokens
- Boosted rewards (e.g., Curve + Convex)

**Step 2: Calculate base yield**
```python
# LP fees
fee_apr = (24h_volume * fee_rate * 365) / pool_tvl

# Lending
lending_apr = supply_rate  # Usually annualized already

# Staking
staking_apr = (rewards_per_year * reward_token_price) / staked_value
```

**Step 3: Add incentive yields**
```python
# Additional token rewards
incentive_apr = (annual_rewards_in_usd) / deposited_value
```

**Step 4: Calculate compounding** (APY from APR)
```python
# Daily compounding
apy = (1 + apr/365)^365 - 1

# Auto-compounding vaults
# Account for compound frequency and harvest costs
```

**Step 5: Account for risks**
- Impermanent loss (for LPs)
- Liquidation risk (for leveraged positions)
- Smart contract risk
- Token price risk

**Present yield analysis:**
```
Curve 3pool → Convex Strategy

Base APR Breakdown:
- Curve trading fees: 3.5%
- CRV rewards: 2.1%
- CVX rewards: 1.8%
- Total APR: 7.4%

With Auto-compounding:
- Compound frequency: Daily
- APY: 7.68%

Additional Boosts (if applicable):
- veCRV boost: +0.5% → 7.9% APR
- vlCVX boost: +0.3% → 8.2% APR
- Boosted APY: 8.54%

Risks:
- Smart contract risk: Moderate (audited, battle-tested)
- Impermanent loss: Low (stablecoin pool)
- Liquidation risk: None (no leverage)
- Token depreciation: CRV and CVX price exposure

Capital Efficiency:
- $10,000 deposit
- Annual yield: $854 (at boosted APY)
- Monthly yield: $71
```

### Workflow 6: Analyze Arbitrage Opportunity

**Step 1: Identify price discrepancies**
```bash
# Get price from multiple DEXs
# Uniswap
cast call <UNISWAP_POOL> "getReserves()(uint112,uint112,uint32)" --rpc-url <RPC_URL>

# Sushiswap
cast call <SUSHI_POOL> "getReserves()(uint112,uint112,uint32)" --rpc-url <RPC_URL>

# Calculate prices and compare
```

**Step 2: Calculate profit potential**
```python
# Simple arbitrage: buy low, sell high
buy_price = price_on_dex1
sell_price = price_on_dex2
gross_profit = sell_price - buy_price

# Account for fees
dex1_fee = amount * 0.003  # 0.3%
dex2_fee = amount * 0.003
gas_cost = gas_used * gas_price

net_profit = gross_profit - dex1_fee - dex2_fee - gas_cost
```

**Step 3: Check liquidity constraints**
- Available liquidity in pools
- Price impact of trade size
- Slippage tolerance

**Step 4: Simulate trade**
```python
# Uniswap V2 swap formula
amount_out = (amount_in * 997 * reserve_out) / (reserve_in * 1000 + amount_in * 997)

# Account for price impact
price_impact = (ideal_amount - actual_amount) / ideal_amount
```

**Present arbitrage analysis:**
```
Arbitrage Opportunity: USDC/WETH

Price Discrepancy:
- Uniswap: 1 WETH = 2,500 USDC
- Sushiswap: 1 WETH = 2,515 USDC
- Difference: 15 USDC (0.6%)

Optimal Trade:
- Buy: 10 WETH on Uniswap for 25,000 USDC
- Sell: 10 WETH on Sushiswap for 25,150 USDC
- Gross profit: 150 USDC

Costs:
- Uniswap fee: 75 USDC (0.3%)
- Sushiswap fee: 75.45 USDC (0.3%)
- Gas cost: ~50 USDC (at 30 Gwei)
- Total costs: 200.45 USDC

Net Profit: -50.45 USDC (NOT PROFITABLE)

Notes:
- Opportunity too small after fees
- Would need >1% price difference or larger size
- Flash loan could eliminate capital requirement but adds fees
```

## Advanced Analyses

### Impermanent Loss Calculator

For LP positions:

```python
def calculate_impermanent_loss(price_ratio_change):
    """
    price_ratio_change: (current_price / initial_price)
    """
    il = 2 * sqrt(price_ratio_change) / (1 + price_ratio_change) - 1
    return il * 100  # Percentage

# Example:
# Initial: 1 ETH = $2000
# Current: 1 ETH = $3000
# price_ratio_change = 3000 / 2000 = 1.5
# IL = -2.02%
```

**Present IL analysis:**
```
Impermanent Loss Analysis

Initial Position:
- 1 ETH + 2,000 USDC ($4,000 total)
- ETH Price: $2,000

Current Position (in pool):
- 0.816 ETH + 2,449 USDC
- ETH Price: $3,000
- Pool Value: $4,898

If Held (not in pool):
- 1 ETH + 2,000 USDC = $5,000

Impermanent Loss: -$102 (-2.04%)

Fees Earned: $150
Net Result: +$48 (+1.2%)

Break-even: Fees cover IL after 2 months
```

### Liquidation Risk Calculator

For leveraged/borrowed positions:

```python
def calculate_liquidation_price(collateral_value, debt_value, liquidation_threshold, collateral_asset_price):
    """
    Calculate price at which position gets liquidated
    """
    liquidation_price = (debt_value / (collateral_value / collateral_asset_price)) / liquidation_threshold
    return liquidation_price
```

### Protocol TVL Tracking

```python
# Calculate total value locked
tvl = sum([get_asset_balance(asset) * get_price(asset) for asset in assets])

# Track over time for trends
```

## Integration with Other Skills

**Chain to other skills:**
- For contract analysis → invoke `ethereum-contract-analyzer`
- For transaction analysis → invoke `ethereum-transaction-inspector`
- For security concerns → invoke `ethereum-security-auditor`
- For on-chain data → invoke `ethereum-chain-explorer`

## Common Contracts Reference

```
Uniswap V2 Factory: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
Uniswap V3 Factory: 0x1F98431c8aD98523631AE4a59f267346ea31F984
Sushiswap Factory: 0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac

Aave V3 Pool: 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
Compound V3 (USDC): 0xc3d688B66703497DAA19211EEdff47f25384cdc3

Lido stETH: 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84
Rocket Pool rETH: 0xae78736Cd615f374D3085123A210448E74Fc6393

Curve 3pool: 0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7
Convex Booster: 0xF403C135812408BFbE8713b5A23a04b3D48AAE31
```

## Tips for Effective DeFi Analysis

1. **Verify contracts:** Always confirm contract addresses
2. **Check audits:** Review security audits for protocols
3. **Understand mechanisms:** Know how the protocol works
4. **Calculate real yields:** Account for all costs and risks
5. **Monitor health:** Track position health factors
6. **Consider composability:** Understand protocol dependencies
7. **Track governance:** Protocol parameters can change
8. **Assess risks:** Smart contract, economic, and systemic risks

## Resources

- **DeFi Llama:** https://defillama.com
- **Uniswap Docs:** https://docs.uniswap.org
- **Aave Docs:** https://docs.aave.com
- **Curve Docs:** https://docs.curve.fi
- **DeFi Prime:** https://defiprime.com
- **Token Terminal:** https://tokenterminal.com