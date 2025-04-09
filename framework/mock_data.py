"""
Mock Data Generator

This module provides utilities for generating mock data for testing and development.
It's particularly useful for simulating responses from external APIs or databases.
"""

import random
import datetime
from typing import Dict, Any, List, Optional, Union


def generate_stock_data(symbol: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate mock stock data for a given symbol.
    
    Args:
        symbol: Stock ticker symbol
        name: Company name (generated from symbol if None)
        
    Returns:
        Dictionary with mock stock data
    """
    # Generate company name if not provided
    if name is None:
        name = f"{symbol.title()} Inc."
    
    # Generate random price between 10 and 500
    price = round(random.uniform(10, 500), 2)
    
    # Generate random price changes
    price_change_1d = round(random.uniform(-5, 5), 2)
    price_change_5d = round(random.uniform(-10, 10), 2)
    price_change_20d = round(random.uniform(-15, 15), 2)
    
    # Calculate percentage changes
    price_change_percent_1d = round(price_change_1d / price * 100, 2)
    
    # Generate random volatility between 10 and 50
    volatility = round(random.uniform(10, 50), 1)
    
    # Generate random volume
    volume = random.randint(100000, 10000000)
    
    # Generate random market cap
    market_cap = price * random.randint(1000000, 1000000000)
    
    # Generate random ratios
    pe_ratio = round(random.uniform(10, 100), 2)
    dividend_yield = round(random.uniform(0, 5), 2)
    
    # Generate mock options data
    options_data = {
        "available": True,
        "expiration_date": (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
        "put_call_ratio": round(random.uniform(0.5, 1.5), 2),
        "implied_volatility": round(random.uniform(20, 60), 1),
        "total_call_volume": random.randint(1000, 100000),
        "total_put_volume": random.randint(1000, 100000)
    }
    
    # Generate mock institutional indicator
    sentiment = random.choice(["bullish", "neutral", "bearish"])
    strength = random.randint(1, 10)
    
    institutional_indicator = {
        "sentiment": sentiment,
        "strength": strength,
        "description": f"Simulated institutional activity indicator shows {sentiment} sentiment with strength {strength}/10"
    }
    
    # Generate mock strategies
    strategies = []
    
    if volatility > 30:
        strategies.append({
            "type": "iron_condor",
            "description": f"Consider an iron condor options strategy for {symbol} to capitalize on high volatility",
            "risk_level": "moderate"
        })
    
    if price_change_5d > 0:
        strategies.append({
            "type": "bull_call_spread",
            "description": f"Consider a bull call spread for {symbol} based on positive momentum",
            "risk_level": "moderate"
        })
    elif price_change_5d < 0:
        strategies.append({
            "type": "bear_put_spread",
            "description": f"Consider a bear put spread for {symbol} based on negative momentum",
            "risk_level": "moderate"
        })
    
    strategies.append({
        "type": "long_position",
        "description": f"Buy {symbol} shares and hold for long-term growth",
        "risk_level": "moderate"
    })
    
    # Assemble the mock stock data
    stock_data = {
        "symbol": symbol,
        "name": name,
        "sector": random.choice(["Technology", "Healthcare", "Energy", "Financial", "Consumer"]),
        "industry": random.choice(["Software", "Hardware", "Biotechnology", "Banking", "Retail"]),
        "current_price": price,
        "price_change_1d": price_change_1d,
        "price_change_1d_percent": price_change_percent_1d,
        "price_change_5d": price_change_5d,
        "price_change_20d": price_change_20d,
        "volatility": volatility,
        "average_volume": volume,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "dividend_yield": dividend_yield,
        "options_data": options_data,
        "institutional_indicator": institutional_indicator,
        "strategies": strategies
    }
    
    return stock_data


def generate_sector_data() -> List[Dict[str, Any]]:
    """
    Generate mock sector data.
    
    Returns:
        List of sector data dictionaries
    """
    sectors = [
        "Technology", "Healthcare", "Energy", "Financial", "Consumer Discretionary",
        "Consumer Staples", "Industrials", "Materials", "Utilities", "Real Estate",
        "Communication Services"
    ]
    
    sector_data = []
    
    for sector in sectors:
        # Generate random volatility between 5 and 40
        volatility = round(random.uniform(5, 40), 1)
        
        # Generate random momentum between -10 and 10
        momentum = round(random.uniform(-10, 10), 1)
        
        # Generate random volume ratio between 0.5 and 2.5
        volume_ratio = round(random.uniform(0.5, 2.5), 2)
        
        # Determine signal based on momentum and volume
        if momentum > 5 and volume_ratio > 1.2:
            signal = "bullish"
        elif momentum < -5 and volume_ratio > 1.2:
            signal = "bearish"
        else:
            signal = "neutral"
        
        # If very high volatility, add "volatile_" prefix to signal
        if volatility > 30:
            signal = f"volatile_{signal}"
        
        sector_data.append({
            "name": sector,
            "volatility": volatility,
            "momentum": momentum,
            "volume_ratio": volume_ratio,
            "signal": signal
        })
    
    # Sort by volatility (highest first)
    sector_data.sort(key=lambda x: x["volatility"], reverse=True)
    
    return sector_data


def generate_portfolio_data(num_holdings: int = 10) -> List[Dict[str, Any]]:
    """
    Generate mock portfolio holdings data.
    
    Args:
        num_holdings: Number of holdings to generate
        
    Returns:
        List of portfolio holdings
    """
    # Define possible asset classes
    asset_classes = ["equity", "fixed_income", "cash", "alternatives"]
    asset_class_weights = [0.6, 0.3, 0.05, 0.05]  # Probabilities for selection
    
    # Define sectors for equity
    sectors = [
        "Technology", "Healthcare", "Energy", "Financial", "Consumer Discretionary",
        "Consumer Staples", "Industrials", "Materials", "Utilities", "Real Estate",
        "Communication Services"
    ]
    
    # Generate random total portfolio value between 100k and 1M
    total_value = random.uniform(100000, 1000000)
    remaining_value = total_value
    
    holdings = []
    
    # Generate random holdings
    for i in range(num_holdings - 1):  # Save the last one to ensure total equals 100%
        # Select random asset class
        asset_class = random.choices(asset_classes, asset_class_weights)[0]
        
        # Generate holding value (between 1% and 20% of remaining value)
        max_value = min(remaining_value * 0.2, remaining_value * 0.99)
        min_value = min(remaining_value * 0.01, max_value)
        value = random.uniform(min_value, max_value)
        remaining_value -= value
        
        holding = {
            "asset_class": asset_class,
            "value": round(value, 2)
        }
        
        # Add equity-specific fields
        if asset_class == "equity":
            holding["symbol"] = f"TICK{i}"
            holding["name"] = f"Ticker {i} Inc."
            holding["sector"] = random.choice(sectors)
            holding["quantity"] = random.randint(10, 1000)
        
        # Add fixed income specific fields
        elif asset_class == "fixed_income":
            holding["name"] = random.choice([
                "Corporate Bond Fund", "Government Treasury", "Municipal Bond",
                "High Yield Bond Fund", "TIPS", "International Bond Fund"
            ])
            holding["yield"] = round(random.uniform(1, 8), 2)
            holding["maturity"] = random.randint(1, 30)
        
        # Add cash specific fields
        elif asset_class == "cash":
            holding["name"] = random.choice([
                "Money Market Fund", "Cash", "Savings Account", "Certificate of Deposit"
            ])
            holding["yield"] = round(random.uniform(0, 5), 2)
        
        # Add alternatives specific fields
        else:
            holding["name"] = random.choice([
                "REIT Fund", "Commodity Fund", "Hedge Fund", "Private Equity",
                "Gold Fund", "Oil & Gas Partnership"
            ])
            holding["category"] = random.choice([
                "Real Estate", "Commodities", "Hedge Funds", "Private Equity"
            ])
        
        holdings.append(holding)
    
    # Add the last holding to make the total exactly match
    asset_class = random.choices(asset_classes, asset_class_weights)[0]
    
    last_holding = {
        "asset_class": asset_class,
        "value": round(remaining_value, 2)
    }
    
    # Add asset class specific fields for the last holding
    if asset_class == "equity":
        last_holding["symbol"] = f"TICK{num_holdings}"
        last_holding["name"] = f"Ticker {num_holdings} Inc."
        last_holding["sector"] = random.choice(sectors)
        last_holding["quantity"] = random.randint(10, 1000)
    elif asset_class == "fixed_income":
        last_holding["name"] = random.choice([
            "Corporate Bond Fund", "Government Treasury", "Municipal Bond",
            "High Yield Bond Fund", "TIPS", "International Bond Fund"
        ])
        last_holding["yield"] = round(random.uniform(1, 8), 2)
        last_holding["maturity"] = random.randint(1, 30)
    elif asset_class == "cash":
        last_holding["name"] = random.choice([
            "Money Market Fund", "Cash", "Savings Account", "Certificate of Deposit"
        ])
        last_holding["yield"] = round(random.uniform(0, 5), 2)
    else:  # alternatives
        last_holding["name"] = random.choice([
            "REIT Fund", "Commodity Fund", "Hedge Fund", "Private Equity",
            "Gold Fund", "Oil & Gas Partnership"
        ])
        last_holding["category"] = random.choice([
            "Real Estate", "Commodities", "Hedge Funds", "Private Equity"
        ])
    
    holdings.append(last_holding)
    
    return holdings


def generate_investment_strategy(risk_tolerance: str, investment_horizon: str, 
                               investment_goals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a mock investment strategy.
    
    Args:
        risk_tolerance: Risk tolerance level (conservative, moderate, aggressive)
        investment_horizon: Investment time horizon (short, medium, long)
        investment_goals: List of investment goals
        
    Returns:
        Mock investment strategy
    """
    # Define asset allocation based on risk profile and horizon
    asset_allocations = {
        'conservative': {
            'short': {'stocks': 20, 'bonds': 60, 'cash': 20, 'alternatives': 0},
            'medium': {'stocks': 30, 'bonds': 60, 'cash': 5, 'alternatives': 5},
            'long': {'stocks': 40, 'bonds': 50, 'cash': 0, 'alternatives': 10}
        },
        'moderate': {
            'short': {'stocks': 40, 'bonds': 40, 'cash': 15, 'alternatives': 5},
            'medium': {'stocks': 60, 'bonds': 30, 'cash': 5, 'alternatives': 5},
            'long': {'stocks': 70, 'bonds': 20, 'cash': 0, 'alternatives': 10}
        },
        'aggressive': {
            'short': {'stocks': 60, 'bonds': 20, 'cash': 15, 'alternatives': 5},
            'medium': {'stocks': 75, 'bonds': 15, 'cash': 5, 'alternatives': 5},
            'long': {'stocks': 85, 'bonds': 5, 'cash': 0, 'alternatives': 10}
        }
    }
    
    # Get asset allocation for the specified profile
    allocation = asset_allocations.get(
        risk_tolerance, 
        asset_allocations['moderate']
    ).get(
        investment_horizon, 
        asset_allocations['moderate']['medium']
    )
    
    # Define mock approaches based on goals
    approaches = []
    
    for goal in investment_goals:
        goal_type = goal.get('type', '').lower()
        
        if goal_type == 'retirement':
            approaches.append({
                'goal': 'Retirement Planning',
                'description': 'Build a diversified portfolio focused on long-term growth and eventual income.',
                'recommendations': [
                    'Maximize tax-advantaged retirement accounts',
                    'Focus on low-cost index funds for core holdings',
                    'Gradually shift to more conservative allocations as retirement approaches'
                ]
            })
        elif goal_type == 'education':
            approaches.append({
                'goal': 'Education Funding',
                'description': 'Save for education expenses with a time-based approach.',
                'recommendations': [
                    'Utilize 529 plans or education-specific savings vehicles',
                    'Use age-based portfolios that become more conservative as education start date approaches',
                    'Consider direct tuition payment options for tax advantages'
                ]
            })
        elif goal_type == 'home_purchase':
            approaches.append({
                'goal': 'Home Purchase',
                'description': 'Build savings for down payment while managing risk based on purchase timeline.',
                'recommendations': [
                    'Keep funds for near-term purchases (< 3 years) in high-yield savings or short-term bonds',
                    'For longer timeframes, consider a more diversified approach with some equity exposure',
                    'Establish separate emergency fund before allocating to down payment'
                ]
            })
        elif goal_type == 'income':
            approaches.append({
                'goal': 'Income Generation',
                'description': 'Create reliable income streams from investment portfolio.',
                'recommendations': [
                    'Focus on dividend-paying stocks and bonds',
                    'Consider REITs and preferred securities for income diversification',
                    'Implement a yield-focused strategy while maintaining appropriate risk levels'
                ]
            })
    
    # Generate volatility approach
    volatility_approaches = {
        'conservative': {
            'description': 'Prioritize capital preservation with selective opportunities during volatility.',
            'strategies': [
                'Maintain higher cash reserves (10-15%) to deploy during market corrections',
                'Focus on defensive sectors with strong balance sheets',
                'Implement stop-loss orders on individual positions (10-15% below purchase)',
                'Consider protective puts on major positions during high market uncertainty'
            ]
        },
        'moderate': {
            'description': 'Balance between protection and opportunity during market volatility.',
            'strategies': [
                'Maintain moderate cash reserves (5-10%) for opportunistic purchases',
                'Implement dollar-cost averaging during extended market downturns',
                'Utilize options for selective hedging of concentrated positions',
                'Focus on quality companies that can weather economic downturns'
            ]
        },
        'aggressive': {
            'description': 'View volatility primarily as an opportunity for enhanced returns.',
            'strategies': [
                'Maintain minimal cash reserves (3-5%) for tactical opportunities',
                'Increase position sizing during significant market corrections',
                'Consider leveraged ETFs for short-term tactical positions',
                'Utilize options for both hedging and return enhancement'
            ]
        }
    }
    
    volatility_approach = volatility_approaches.get(risk_tolerance, volatility_approaches['moderate'])
    
    return {
        'asset_allocation': allocation,
        'goal_based_approaches': approaches,
        'volatility_approach': volatility_approach,
        'rebalancing_frequency': 'Quarterly' if risk_tolerance == 'aggressive' else 'Semi-annually',
        'tax_efficiency_focus': 'High' if len(investment_goals) > 2 else 'Medium'
    }


def generate_volatility_opportunities(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate mock volatility opportunities.
    
    Args:
        count: Number of opportunities to generate
        
    Returns:
        List of volatility opportunity dictionaries
    """
    opportunities = []
    
    for i in range(count):
        # Generate random symbol
        symbol = f"TICK{i}"
        
        # Generate random sector
        sector = random.choice([
            "Technology", "Healthcare", "Energy", "Financial", "Consumer Discretionary",
            "Consumer Staples", "Industrials", "Materials", "Utilities", "Real Estate",
            "Communication Services"
        ])
        
        # Generate random volatility between 20 and 50
        volatility = round(random.uniform(20, 50), 1)
        
        # Generate random momentum between -20 and 20
        momentum = round(random.uniform(-20, 20), 1)
        
        # Generate random price between 10 and 500
        price = round(random.uniform(10, 500), 2)
        
        # Generate random volume
        volume = random.randint(100000, 10000000)
        
        # Generate mock opportunity
        opportunity = {
            "symbol": symbol,
            "name": f"{symbol} Inc.",
            "sector": sector,
            "volatility": volatility,
            "momentum": momentum,
            "price": price,
            "volume": volume,
            "source": "Daily volatility scan"
        }
        
        opportunities.append(opportunity)
    
    # Sort by volatility (highest first)
    opportunities.sort(key=lambda x: x["volatility"], reverse=True)
    
    return opportunities


def generate_market_analysis() -> Dict[str, Any]:
    """
    Generate a mock market analysis.
    
    Returns:
        Dictionary with market analysis data
    """
    # Generate current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Generate sector data
    volatile_sectors = generate_sector_data()
    
    # Generate volatility opportunities
    volatility_opportunities = generate_volatility_opportunities(15)
    
    # Assemble market analysis
    analysis = {
        "analysis_date": timestamp,
        "market_overview": {
            "market_sentiment": random.choice(["bullish", "neutral", "bearish"]),
            "volatility_index": round(random.uniform(15, 35), 1),
            "trading_volume_ratio": round(random.uniform(0.8, 1.5), 2),
            "volatile_sectors": volatile_sectors[:5]  # Top 5 most volatile sectors
        },
        "volatility_opportunities": volatility_opportunities,
        "opportunity_count": len(volatility_opportunities)
    }
    
    return analysis


def generate_educational_content(topic: str, level: str = "beginner") -> Dict[str, Any]:
    """
    Generate mock educational content.
    
    Args:
        topic: Content topic
        level: Expertise level (beginner, intermediate, advanced)
        
    Returns:
        Dictionary with educational content
    """
    # Define content library
    content_library = {
        'options_trading': {
            'beginner': {
                'title': 'Introduction to Options Trading',
                'summary': 'Learn the basics of options contracts and how they can be used in your portfolio.',
                'sections': [
                    {
                        'heading': 'What are Options?',
                        'content': 'Options are financial derivatives that give the buyer the right, but not the obligation, to buy or sell an underlying asset at a predetermined price (strike price) before a specific date (expiration date). Call options provide the right to buy, while put options provide the right to sell.'
                    },
                    {
                        'heading': 'Key Terms',
                        'content': 'Strike Price: The price at which the option can be exercised. Premium: The price paid to acquire an option. Expiration Date: The date after which the option becomes void. In-the-Money: When an option has intrinsic value.'
                    },
                    {
                        'heading': 'Basic Strategies for Beginners',
                        'content': 'Covered Calls: Selling call options against stock you already own to generate income. Protective Puts: Buying put options to protect against downside in stocks you own, similar to insurance.'
                    }
                ],
                'conclusion': 'Options can be valuable tools for income generation and risk management, but require careful study before implementation.'
            },
            'intermediate': {
                'title': 'Intermediate Options Strategies',
                'summary': 'Explore more advanced options strategies and their risk/reward profiles.',
                'sections': [
                    {
                        'heading': 'Vertical Spreads',
                        'content': 'Bull Call Spread: Buying a call option while selling a higher strike call option with the same expiration. Bear Put Spread: Buying a put option while selling a lower strike put option with the same expiration. These spreads reduce cost but cap potential profit.'
                    },
                    {
                        'heading': 'Iron Condors',
                        'content': 'An iron condor combines a bull put spread with a bear call spread. This creates a range where the strategy is profitable if the underlying asset stays within that range until expiration, making it ideal for low-volatility expectations.'
                    },
                    {
                        'heading': 'Greeks and Risk Management',
                        'content': 'Delta measures an option\'s sensitivity to changes in the underlying asset price. Theta measures time decay. Vega measures sensitivity to volatility changes. Managing these factors is crucial for options success.'
                    }
                ],
                'conclusion': 'Intermediate strategies allow for more precise risk/reward targeting but require more active management and understanding of option pricing factors.'
            },
            'advanced': {
                'title': 'Advanced Options Trading Techniques',
                'summary': 'Master complex options strategies for volatility trading and portfolio enhancement.',
                'sections': [
                    {
                        'heading': 'Volatility Trading',
                        'content': 'Long Straddle: Buying both a call and put at the same strike price to profit from significant price movement in either direction. Long Strangle: Similar to a straddle but using out-of-the-money options, reducing cost but requiring larger moves.'
                    },
                    {
                        'heading': 'Calendar Spreads',
                        'content': 'Selling a near-term option while buying a longer-term option at the same strike price. This strategy exploits time decay differentials and can be structured as neutral, bullish, or bearish.'
                    },
                    {
                        'heading': 'Ratio Spreads and Backspreads',
                        'content': 'These involve buying and selling different quantities of options at different strikes. They create asymmetric payoff profiles that can be used for specific market outlooks and volatility expectations.'
                    }
                ],
                'conclusion': 'Advanced options strategies require sophisticated risk management, thorough understanding of volatility behavior, and careful position sizing.'
            }
        },
        'portfolio_diversification': {
            'beginner': {
                'title': 'Diversification Basics',
                'summary': 'Learn why diversification is essential for managing investment risk.',
                'sections': [
                    {
                        'heading': 'What is Diversification?',
                        'content': 'Diversification means spreading investments across various asset classes and securities to reduce risk. The principle is based on the observation that different assets often respond differently to the same economic event.'
                    },
                    {
                        'heading': 'Asset Classes for Diversification',
                        'content': 'Stocks: Ownership in companies, higher growth potential but more volatile. Bonds: Loans to governments or corporations, more stable but lower returns. Cash: Highly liquid assets like savings accounts or money market funds. Alternatives: Real estate, commodities, or other non-traditional investments.'
                    },
                    {
                        'heading': 'Benefits of Diversification',
                        'content': 'Reduced portfolio volatility. Protection against significant losses in any single investment. More consistent returns over time. Preservation of capital during market downturns.'
                    }
                ],
                'conclusion': 'Proper diversification is one of the most fundamental risk management techniques for investors of all experience levels.'
            },
            'intermediate': {
                'title': 'Advanced Diversification Strategies',
                'summary': 'Explore beyond basic asset classes to enhance portfolio resilience.',
                'sections': [
                    {
                        'heading': 'Correlation Analysis',
                        'content': 'Correlation measures how investments move in relation to each other. Low or negative correlations between assets provide the strongest diversification benefits. Modern portfolio theory uses correlation to optimize the risk/return profile of a portfolio.'
                    },
                    {
                        'heading': 'Factor Diversification',
                        'content': 'Beyond asset classes, consider diversifying across risk factors such as: Value vs. Growth. Small-cap vs. Large-cap. Quality, Momentum, and Minimum Volatility factors. Geographic regions and developed vs. emerging markets.'
                    },
                    {
                        'heading': 'Alternative Investments',
                        'content': 'REITs (Real Estate Investment Trusts) provide exposure to real estate. Commodities can hedge against inflation. Private equity offers exposure to non-public companies. Hedge fund strategies can provide returns uncorrelated with traditional markets.'
                    }
                ],
                'conclusion': 'Effective intermediate diversification requires understanding correlations between assets and economic factors affecting different markets.'
            },
            'advanced': {
                'title': 'Institutional Diversification Techniques',
                'summary': 'Master sophisticated diversification approaches used by institutional investors.',
                'sections': [
                    {
                        'heading': 'Risk Parity Approach',
                        'content': 'Rather than allocating by dollar amount, risk parity allocates based on risk contribution. This typically involves leveraging lower-risk assets like bonds to contribute equally to portfolio risk as higher-risk assets like stocks.'
                    },
                    {
                        'heading': 'Tail Risk Hedging',
                        'content': 'Specifically diversifying against extreme market events (black swans). Strategies include out-of-the-money put options, volatility investments, trend-following systems, and alternative strategies with crisis alpha.'
                    },
                    {
                        'heading': 'Dynamic Asset Allocation',
                        'content': 'Adjusting diversification based on changing market conditions. This includes tactical asset allocation, risk-responsive rebalancing, and regime-based models that adapt to different economic environments.'
                    }
                ],
                'conclusion': 'Advanced diversification goes beyond static allocation to dynamically manage risk across multiple dimensions and market conditions.'
            }
        }
    }
    
    # Check if topic exists
    if topic not in content_library:
        return {
            'error': f"Topic '{topic}' not found",
            'available_topics': list(content_library.keys())
        }
    
    # Check if level exists for topic
    if level not in content_library[topic]:
        # Default to beginner
        level = 'beginner'
        note = f"Content for '{level}' level not found, providing beginner content instead."
    else:
        note = None
    
    # Get content
    content = content_library[topic][level]
    
    # Add related topics
    related_topics = list(set(content_library.keys()) - {topic})
    
    result = {
        'content': content,
        'related_topics': related_topics
    }
    
    # Add note if level was not found
    if note:
        result['note'] = note
    
    return result
