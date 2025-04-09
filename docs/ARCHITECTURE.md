# AI Portfolio Manager - Architecture Overview

This document outlines the architecture and components of the AI Portfolio Manager system.

## System Architecture

The AI Portfolio Manager is built using Google Cloud technologies with a conversational AI interface:

- **Frontend**: Agent Builder and DialogFlow Conversational Agents
- **Backend**: Google Cloud Functions powering specialized financial tools
- **Data Sources**: Mock financial data with extensibility for real-time market data

```
┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │
│  Agent Builder &  │     │  Google Cloud     │
│  DialogFlow       │◄───►│  Functions        │
│                   │     │                   │
└───────────────────┘     └────────┬──────────┘
                                   │
                                   ▼
                          ┌───────────────────┐
                          │                   │
                          │  Mock Financial   │
                          │  Data / yfinance  │
                          │                   │
                          └───────────────────┘
```

## Core Components

### 1. Market Scanner Module
- **Purpose**: Identifies high-volatility trading opportunities across the market
- **Implementation Files**: 
  - `market_scanner.py` - Core scanning logic
  - `scheduled_analysis.py` - Mock market data provider
- **API Endpoint**: `/volatility_opportunities`
- **Parameters**:
  - `min_volatility`: Minimum volatility threshold (e.g., 30%)
  - `momentum_direction`: Filter by momentum direction ('positive' or 'negative')
  - `limit`: Maximum number of results to return
- **Features**:
  - Sector-based volatility analysis
  - Momentum tracking
  - Institutional sentiment indicators
  - Strategy recommendations for volatile assets

### 2. Stock Analysis Module
- **Purpose**: Deep-dive analysis of individual stocks
- **Implementation Files**:
  - `agent_api.py` - Contains analyze_symbol function
- **API Endpoint**: `/analyze_symbol`
- **Parameters**:
  - `symbol`: Stock ticker symbol (e.g., AAPL)
- **Features**:
  - Price and historical metrics
  - Volatility and momentum calculation
  - Options data analysis
  - Institutional sentiment indicators
  - Personalized trading strategies

### 3. Portfolio Analysis Module
- **Purpose**: Holistic analysis of investment portfolios
- **Implementation Files**:
  - `portfolio_manager.py` - Analytics logic
- **API Endpoint**: `/portfolio_analyzer`
- **Parameters**:
  - `holdings`: Array of portfolio holdings (including symbol, value, asset_class, sector)
  - `risk_profile`: User's risk tolerance (conservative, moderate, aggressive)
- **Features**:
  - Asset allocation visualization
  - Risk metrics calculation (volatility, drawdown, Sharpe ratio)
  - Diversification scoring
  - Concentration analysis
  - Personalized rebalancing recommendations

### 4. Strategy Generation Module
- **Purpose**: Creates personalized investment strategies
- **Implementation Files**:
  - `strategy_generator.py` - Strategy creation logic
- **API Endpoint**: `/generate_investment_strategy`
- **Parameters**:
  - `investor_profile`: Object containing risk_tolerance, investment_horizon, and investment_goals
- **Features**:
  - Custom asset allocation by risk profile
  - Goal-based investment approaches
  - Volatility management strategies
  - Implementation timelines
  - Rebalancing recommendations

### 5. Educational Content Module
- **Purpose**: Delivers targeted educational investing content
- **Implementation Files**:
  - `agent_api.py` - Contains educational_content function
- **API Endpoint**: `/educational_content`
- **Parameters**:
  - `topic`: Content topic (e.g., "options_trading", "portfolio_diversification")
  - `level`: Expertise level (beginner, intermediate, advanced)
- **Features**:
  - Comprehensive topic coverage
  - Content tailored to expertise level
  - Related topics suggestions

### 6. Sector Analysis Module
- **Purpose**: Provides sector-level market insights
- **Implementation Files**:
  - `agent_api.py` - Contains sector_analysis function
- **API Endpoint**: `/sector_analysis`
- **Features**:
  - Sector volatility metrics
  - Momentum indicators
  - Volume analysis
  - Bullish/bearish sector insights

### 7. Trade Execution Module
- **Purpose**: Simulates trade execution (mock implementation)
- **Implementation Files**: 
  - `trade_executor.py` - Mock execution logic
- **API Endpoint**: `/execute_portfolio_action`
- **Parameters**:
  - `action_type`: Type of action (execute_trades, approve_trades, rebalance_portfolio)
  - `trades`: Array of trade objects
  - `investor_id`: Identifier for the investor
  - `execution_mode`: Level of automation (advisory_only, approval_required, fully_automated)
- **Features**:
  - Multi-mode execution (advisory, approval-based, automated)
  - Order validation
  - Trade simulation

## Integration Approach

### API Layer

The system exposes a unified API through Google Cloud Functions:

- **Main Entry Point**: `main.py` routes requests to appropriate handlers
- **Error Handling**: Consistent error format across all endpoints
- **Authentication**: Handled at the Google Cloud level (not implemented in mock version)

### Data Flow

1. User interacts with the Agent Builder/DialogFlow interface
2. Agent identifies intent and calls appropriate Cloud Function
3. Cloud Function processes request and returns structured data
4. Agent formats response and presents it to the user

## Deployment

All components are deployed as Google Cloud Functions with HTTP triggers. The DialogFlow agent is configured to interact with these functions through webhook calls.

## Extensibility

The system is designed for easy extension:

1. **Real-time Data**: Framework ready for yfinance integration for live market data
2. **Additional Analysis**: Risk metrics and analysis techniques can be expanded
3. **UI Enhancement**: Visualization-ready data structures in all API responses
4. **Portfolio Tracking**: Architecture supports adding historical tracking

## Conversation Examples

The system includes example conversations for each tool showing:
1. When to use each tool
2. How to format parameters for different scenarios
3. How to interpret and present the results to users
