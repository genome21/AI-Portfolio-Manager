# AI Portfolio Manager

An Algorithmic Portfolio Manager Agent for retail investors using Google Cloud technologies. This solution empowers retail investors to achieve their financial goals through personalized and automated portfolio management.

## Project Overview

Retail investors often lack the time, expertise, and access to sophisticated tools needed to effectively manage their investment portfolios. This leads to suboptimal investment decisions, missed opportunities, and potentially lower returns.

Our AI Portfolio Manager Agent solves this problem by providing:

1. **Volatility-Based Opportunity Detection**: Identifies high-volatility stocks across the entire market for potential trading opportunities
2. **Personalized Strategy Generation**: Creates custom investment strategies based on individual risk profiles and goals
3. **Portfolio Analysis and Optimization**: Analyzes existing portfolios and recommends improvements
4. **Automated Trading Execution**: Implements strategies with configurable automation levels
5. **Educational Content**: Delivers tailored educational materials to improve investor knowledge

## Architecture

The solution is built on Google Cloud Platform using the following components:

1. **Google Agent Space**: Powers the conversational interface for retail investors
2. **Cloud Functions**: Implement the core analytical and trading capabilities
3. **Cloud Storage**: Stores analysis results and user data
4. **Cloud Scheduler**: Triggers scheduled market analysis
5. **Yahoo Finance API**: Provides market data (free tier for hackathon)

## Technical Components

### Market Analysis Modules

- **market_scanner.py**: Scans the market for volatility opportunities
- **scheduled_analysis.py**: Performs daily market analysis and stores results

### Portfolio Management Modules

- **portfolio_manager.py**: Analyzes and optimizes investment portfolios
- **strategy_generator.py**: Creates personalized investment strategies
- **trade_executor.py**: Executes trading actions through brokerage APIs

### Agent Integration

- **agent_api.py**: Exposes Cloud Functions as API endpoints for Agent Space
- **openapi.yaml**: Defines the API specification for Agent integration

## Data Sources

For the hackathon implementation, we're using:

- **Yahoo Finance API** (via yfinance Python library): Historical price data, company fundamentals, options chain information
- **Simulated institutional data**: For proof-of-concept implementation

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone https://github.com/username/ai-portfolio-manager.git
   cd ai-portfolio-manager
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Deploy Cloud Functions**:
   ```
   gcloud functions deploy market_volatility_scan --runtime python312 --trigger-http --allow-unauthenticated
   gcloud functions deploy analyze_portfolio --runtime python312 --trigger-http --allow-unauthenticated
   # Deploy remaining functions...
   ```

4. **Set up scheduled analysis**:
   ```
   gcloud scheduler jobs create http daily-market-analysis --schedule="0 18 * * *" --uri="https://REGION-PROJECT_ID.cloudfunctions.net/run_scheduled_analysis" --http-method=GET
   ```

5. **Configure Agent Space**:
   - Create a new Agent in Google Agent Space
   - Upload the OpenAPI specification from config/openapi.yaml
   - Configure the Agent with appropriate prompts and behavior

## Usage Scenarios

1. **Market Opportunity Exploration**:
   - "Show me today's high volatility stocks with positive momentum"
   - "Explain the trading strategy recommended for NVDA"
   - "Which sectors are showing unusual activity today?"

2. **Portfolio Management**:
   - "Analyze my current portfolio for diversification issues"
   - "Generate an investment strategy for my retirement goal"
   - "Recommend how to rebalance my portfolio"

3. **Trading Execution**:
   - "Execute the recommended trades for my portfolio"
   - "Place a limit order for 10 shares of AAPL at $190"
   - "Review my pending trades"

4. **Education**:
   - "Explain options trading at a beginner level"
   - "Teach me about portfolio diversification"
   - "What are iron condors and when should I use them?"

## Future Enhancements

1. **Enhanced Data Sources**: Integration with premium market data providers for more accurate signals
2. **Expanded Strategy Library**: Additional trading strategies for different market conditions
3. **Tax Optimization**: Improved tax-aware trading recommendations
4. **Multi-Broker Support**: Connect to a wider range of brokerage platforms
5. **Performance Tracking**: Historical performance tracking against benchmarks

## Team Information

- **Team Name**: Synapse
- **Industry**: FSI (Financial Services Industry)
- **Domain**: Product & Services

## License

[License information]
