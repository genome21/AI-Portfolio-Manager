import functions_framework
from flask import jsonify, Request
import json
import datetime
import numpy as np

# This module acts as the integration point for Google Agent Space
# It exposes OpenAPI-compliant endpoints that the Agent can call

# Function declarations - implementation will be added incrementally
@functions_framework.http
def volatility_opportunities(request):
    """API endpoint for retrieving current volatility opportunities.
    This is used by the Agent to answer questions about market opportunities.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with volatility opportunities
    """
    try:
        # Import the function to get mock analysis data
        from scheduled_analysis import get_latest_analysis
        
        # Get the latest market analysis with mock data
        analysis = get_latest_analysis()
        
        # Filter or limit results if query parameters are provided
        request_args = request.args
        
        # Filter by minimum volatility if specified
        min_volatility = request_args.get('min_volatility')
        if min_volatility and min_volatility.isdigit():
            min_vol = float(min_volatility)
            analysis['volatility_opportunities'] = [
                opp for opp in analysis.get('volatility_opportunities', [])
                if opp.get('volatility', 0) >= min_vol
            ]
        
        # Filter by momentum direction if specified
        momentum_direction = request_args.get('momentum_direction')
        if momentum_direction in ['positive', 'negative']:
            analysis['volatility_opportunities'] = [
                opp for opp in analysis.get('volatility_opportunities', [])
                if (momentum_direction == 'positive' and opp.get('momentum', 0) > 0) or
                   (momentum_direction == 'negative' and opp.get('momentum', 0) < 0)
            ]
        
        # Limit number of results if specified
        limit = request_args.get('limit')
        if limit and limit.isdigit():
            analysis['volatility_opportunities'] = analysis.get('volatility_opportunities', [])[:int(limit)]
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving volatility opportunities: {str(e)}'
        }), 500

@functions_framework.http
def sector_analysis(request):
    """API endpoint for retrieving sector-level analysis.
    This is used by the Agent to answer questions about sector performance.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with sector analysis
    """
    try:
        # Import the function to get mock analysis data
        from scheduled_analysis import get_latest_analysis
        
        # Get the latest market analysis with mock data
        analysis = get_latest_analysis()
        
        # Extract just the sector data
        sector_data = analysis.get('market_overview', {}).get('volatile_sectors', [])
        
        # Generate additional sector insights
        sector_insights = generate_sector_insights(sector_data)
        
        return jsonify({
            'sector_analysis': {
                'timestamp': analysis.get('analysis_date'),
                'sectors': sector_data,
                'insights': sector_insights
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving sector analysis: {str(e)}'
        }), 500

def generate_sector_insights(sector_data):
    """Generate insights from sector data
    
    Args:
        sector_data: List of sector analysis data
        
    Returns:
        List of sector insights
    """
    insights = []
    
    # Look for highly volatile sectors
    high_volatility_sectors = [s for s in sector_data if s.get('volatility', 0) > 20]
    if high_volatility_sectors:
        sector_names = ', '.join([s.get('name') for s in high_volatility_sectors[:3]])
        insights.append({
            'type': 'high_volatility',
            'description': f"High volatility detected in {sector_names} sectors, suggesting potential trading opportunities."
        })
    
    # Look for momentum trends
    bullish_sectors = [s for s in sector_data if s.get('momentum', 0) > 5]
    bearish_sectors = [s for s in sector_data if s.get('momentum', 0) < -5]
    
    if bullish_sectors:
        sector_names = ', '.join([s.get('name') for s in bullish_sectors[:3]])
        insights.append({
            'type': 'bullish_momentum',
            'description': f"Positive momentum in {sector_names} sectors, indicating potential upward trends."
        })
    
    if bearish_sectors:
        sector_names = ', '.join([s.get('name') for s in bearish_sectors[:3]])
        insights.append({
            'type': 'bearish_momentum',
            'description': f"Negative momentum in {sector_names} sectors, suggesting caution or potential short opportunities."
        })
    
    # Look for unusual volume
    high_volume_sectors = [s for s in sector_data if s.get('volume_ratio', 0) > 1.5]
    if high_volume_sectors:
        sector_names = ', '.join([s.get('name') for s in high_volume_sectors[:3]])
        insights.append({
            'type': 'unusual_volume',
            'description': f"Unusual trading volume in {sector_names} sectors, indicating increased market interest."
        })
    
    return insights

@functions_framework.http
def handle_analyze_symbol(request):
    """API endpoint for analyzing a specific stock symbol.
    This is used by the Agent to answer questions about specific stocks.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with symbol analysis
    """
    # Get the request JSON or query params
    symbol = None
    
    if request.method == 'GET':
        symbol = request.args.get('symbol')
    elif request.is_json:
        request_data = request.get_json()
        symbol = request_data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Missing symbol parameter'}), 400
    
    # Convert to uppercase
    symbol = symbol.upper()
    
    try:
        # For hackathon, let's use a mock data approach instead of yfinance
        # to avoid the SQLite dependency issue
        
        # Mock data for demo purposes
        mock_data = {
            'AAPL': {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "current_price": 187.43,
                "price_change_1d": 0.75,
                "price_change_5d": 1.32,
                "price_change_20d": 2.3,
                "volatility": 22.8,
                "average_volume": 64287500,
                "market_cap": 2936518000000,
                "pe_ratio": 29.12,
                "dividend_yield": 0.52,
                "options_data": {
                    "available": True,
                    "expiration_date": "2025-04-18",
                    "put_call_ratio": 0.82,
                    "implied_volatility": 24.5,
                    "total_call_volume": 215400,
                    "total_put_volume": 176628
                },
                "institutional_indicator": {
                    "sentiment": "bullish",
                    "strength": 6,
                    "description": "Simulated institutional activity indicator shows bullish sentiment with strength 6/10"
                },
                "strategies": [
                    {
                        "type": "covered_call",
                        "description": "Consider a covered call strategy for AAPL to generate income",
                        "risk_level": "low"
                    },
                    {
                        "type": "long_position",
                        "description": "Buy AAPL shares and hold for long-term growth",
                        "risk_level": "moderate"
                    },
                    {
                        "type": "protective_put",
                        "description": "Buy AAPL shares with protective puts for downside protection",
                        "risk_level": "low"
                    }
                ]
            },
            'TSLA': {
                "symbol": "TSLA",
                "name": "Tesla, Inc.",
                "sector": "Automotive",
                "industry": "Electric Vehicles",
                "current_price": 244.58,
                "price_change_1d": 2.14,
                "price_change_5d": 5.21,
                "price_change_20d": 6.5,
                "volatility": 38.9,
                "average_volume": 31245900,
                "market_cap": 778526000000,
                "pe_ratio": 68.21,
                "dividend_yield": 0,
                "options_data": {
                    "available": True,
                    "expiration_date": "2025-04-18",
                    "put_call_ratio": 0.82,
                    "implied_volatility": 43.2,
                    "total_call_volume": 98700,
                    "total_put_volume": 80934
                },
                "institutional_indicator": {
                    "sentiment": "bullish",
                    "strength": 7,
                    "description": "Simulated institutional activity indicator shows bullish sentiment with strength 7/10"
                },
                "strategies": [
                    {
                        "type": "momentum_swing",
                        "description": "Consider a momentum swing trade on TSLA to capitalize on positive momentum",
                        "risk_level": "high"
                    },
                    {
                        "type": "bull_call_spread",
                        "description": "Consider a bull call spread for TSLA to leverage upward momentum with defined risk",
                        "risk_level": "moderate"
                    },
                    {
                        "type": "protective_put",
                        "description": "Consider a protective put strategy for TSLA to guard against potential volatility",
                        "risk_level": "moderate"
                    }
                ]
            },
            'MSFT': {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "current_price": 411.22,
                "price_change_1d": 1.05,
                "price_change_5d": 2.74,
                "price_change_20d": 3.8,
                "volatility": 25.3,
                "average_volume": 28451200,
                "market_cap": 3018725000000,
                "pe_ratio": 34.87,
                "dividend_yield": 0.73,
                "options_data": {
                    "available": True,
                    "expiration_date": "2025-04-18",
                    "put_call_ratio": 0.75,
                    "implied_volatility": 26.8,
                    "total_call_volume": 143500,
                    "total_put_volume": 107625
                },
                "institutional_indicator": {
                    "sentiment": "bullish",
                    "strength": 7,
                    "description": "Simulated institutional activity indicator shows bullish sentiment with strength 7/10"
                },
                "strategies": [
                    {
                        "type": "long_position",
                        "description": "Buy MSFT shares and hold for long-term growth",
                        "risk_level": "moderate"
                    },
                    {
                        "type": "bull_call_spread",
                        "description": "Consider a bull call spread for MSFT to leverage upward momentum",
                        "risk_level": "moderate"
                    }
                ]
            },
            'NVDA': {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "sector": "Technology",
                "industry": "Semiconductors",
                "current_price": 926.43,
                "price_change_1d": 2.14,
                "price_change_5d": 5.21,
                "price_change_20d": 8.7,
                "volatility": 42.3,
                "average_volume": 28456700,
                "market_cap": 2283415000000,
                "pe_ratio": 62.34,
                "dividend_yield": 0.04,
                "options_data": {
                    "available": True,
                    "expiration_date": "2025-04-18",
                    "put_call_ratio": 0.65,
                    "implied_volatility": 48.7,
                    "total_call_volume": 142500,
                    "total_put_volume": 92625
                },
                "institutional_indicator": {
                    "sentiment": "bullish",
                    "strength": 8,
                    "description": "Simulated institutional activity indicator shows bullish sentiment with strength 8/10"
                },
                "strategies": [
                    {
                        "type": "bull_call_spread",
                        "description": "Consider a bull call spread for NVDA based on positive momentum",
                        "risk_level": "moderate"
                    },
                    {
                        "type": "momentum_long",
                        "description": "Consider a long position in NVDA with trailing stop loss",
                        "risk_level": "high"
                    }
                ]
            }
        }
        
        # Add a few more default stocks if needed
        if symbol not in mock_data:
            # Return a generic response for unknown symbols
            return jsonify({
                "symbol": symbol,
                "name": f"{symbol} Inc.",
                "sector": "Unknown",
                "industry": "Unknown",
                "current_price": 100.00,
                "price_change_1d": 0.50,
                "price_change_5d": 1.25,
                "price_change_20d": 2.1,
                "volatility": 30.5,
                "average_volume": 10000000,
                "market_cap": 100000000000,
                "pe_ratio": 25.00,
                "dividend_yield": 0.5,
                "options_data": {
                    "available": True,
                    "expiration_date": "2025-04-18",
                    "put_call_ratio": 0.80,
                    "implied_volatility": 35.0,
                    "total_call_volume": 50000,
                    "total_put_volume": 40000
                },
                "institutional_indicator": {
                    "sentiment": "neutral",
                    "strength": 5,
                    "description": "Simulated institutional activity indicator shows neutral sentiment with strength 5/10"
                },
                "strategies": [
                    {
                        "type": "wait_and_watch",
                        "description": f"Monitor {symbol} for clearer signals before taking a position",
                        "risk_level": "low"
                    }
                ]
            })
        
        # Return the data for the requested symbol
        return jsonify(mock_data[symbol])
    
    except Exception as e:
        return jsonify({'error': f'Error analyzing symbol {symbol}: {str(e)}'}), 500

@functions_framework.http
def portfolio_analyzer(request):
    """API endpoint for analyzing a portfolio.
    This is used by the Agent to answer questions about portfolio performance and recommendations.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with portfolio analysis
    """
    # This function is a mock implementation for the hackathon
    
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    try:
        request_data = request.get_json()
        
        # Check if request contains needed parameters
        if 'holdings' not in request_data:
            return jsonify({'error': 'Missing holdings parameter'}), 400
        
        holdings = request_data['holdings']
        risk_profile = request_data.get('risk_profile', 'moderate')
        
        # Calculate portfolio metrics
        # For hackathon, we'll use mock calculations
        total_value = sum(holding.get('value', 0) for holding in holdings)
        
        # Calculate asset allocation
        asset_classes = {}
        sectors = {}
        
        for holding in holdings:
            # Asset class allocation
            asset_class = holding.get('asset_class', 'unknown').lower()
            value = holding.get('value', 0)
            
            if asset_class not in asset_classes:
                asset_classes[asset_class] = 0
            asset_classes[asset_class] += value
            
            # Sector allocation (for equities)
            if asset_class == 'equity':
                sector = holding.get('sector', 'unknown')
                if sector not in sectors:
                    sectors[sector] = 0
                sectors[sector] += value
        
        # Convert to percentages
        asset_allocation = {
            'by_asset_class': {
                asset_class: {
                    'value': value,
                    'percentage': round((value / total_value * 100) if total_value > 0 else 0, 1)
                } for asset_class, value in asset_classes.items()
            },
            'by_sector': {
                sector: {
                    'value': value,
                    'percentage': round((value / asset_classes.get('equity', 1) * 100) 
                                     if asset_classes.get('equity', 0) > 0 else 0, 1)
                } for sector, value in sectors.items()
            }
        }
        
        # Mock risk metrics
        risk_metrics = {
            'portfolio_volatility': 24.5,
            'max_drawdown': -28.3,
            'sharpe_ratio': 0.92,
            'beta': 1.15
        }
        
        # Calculate diversification metrics
        holding_values = [h.get('value', 0) for h in holdings]
        holding_values.sort(reverse=True)
        
        top_holding_concentration = (holding_values[0] / total_value * 100) if total_value > 0 and holding_values else 0
        
        # Herfindahl index calculation
        herfindahl = sum((value / total_value * 100) ** 2 for value in holding_values) if total_value > 0 else 0
        
        diversification = {
            'asset_class_count': len(asset_classes),
            'sector_count': len(sectors),
            'security_count': len(holdings),
            'top_holding_concentration': round(top_holding_concentration, 1),
            'top5_concentration': round(sum(holding_values[:5]) / total_value * 100 if total_value > 0 else 0, 1),
            'herfindahl_index': round(herfindahl, 2),
            'diversification_score': round(max(0, min(100, 100 - (herfindahl / 100) - 
                                              (20 if len(asset_classes) == 1 else 0))), 1)
        }
        
        # Generate mock recommendations
        recommendations = []
        
        # Asset allocation recommendations
        target_allocations = {
            'conservative': {'equity': 40, 'fixed_income': 50, 'alternatives': 5, 'cash': 5},
            'moderate': {'equity': 60, 'fixed_income': 30, 'alternatives': 7, 'cash': 3},
            'aggressive': {'equity': 80, 'fixed_income': 15, 'alternatives': 3, 'cash': 2}
        }
        
        targets = target_allocations.get(risk_profile, target_allocations['moderate'])
        
        for asset_class, target in targets.items():
            current = asset_allocation['by_asset_class'].get(asset_class, {'percentage': 0})['percentage']
            
            if abs(current - target) >= 10:  # Only recommend if off by at least 10%
                if current < target:
                    recommendations.append({
                        'type': 'rebalance',
                        'asset_class': asset_class,
                        'current_allocation': current,
                        'target_allocation': target,
                        'description': f"Increase {asset_class} allocation from {current}% to {target}%",
                        'priority': 'high' if abs(current - target) > 20 else 'medium'
                    })
                else:
                    recommendations.append({
                        'type': 'rebalance',
                        'asset_class': asset_class,
                        'current_allocation': current,
                        'target_allocation': target,
                        'description': f"Decrease {asset_class} allocation from {current}% to {target}%",
                        'priority': 'high' if abs(current - target) > 20 else 'medium'
                    })
        
        # Sector concentration recommendation
        for sector, data in asset_allocation['by_sector'].items():
            if data['percentage'] > 30:  # Flag sectors over 30%
                recommendations.append({
                    'type': 'sector_concentration',
                    'sector': sector,
                    'current_allocation': data['percentage'],
                    'description': f"Reduce concentration in {sector} sector from {data['percentage']}%",
                    'priority': 'medium'
                })
        
        # Concentration risk
        if diversification['top_holding_concentration'] > 20:
            # Find the largest holding
            largest_holding = max(holdings, key=lambda x: x.get('value', 0))
            recommendations.append({
                'type': 'concentration',
                'description': f"Reduce position size in {largest_holding.get('name', largest_holding.get('symbol', 'your largest holding'))}",
                'details': f"Your largest position represents {diversification['top_holding_concentration']}% of your portfolio.",
                'priority': 'high' if diversification['top_holding_concentration'] > 30 else 'medium'
            })
        
        # Diversification recommendation
        if diversification['diversification_score'] < 60:
            recommendations.append({
                'type': 'diversification',
                'description': "Improve portfolio diversification by adding more securities across different sectors and asset classes",
                'details': f"Your diversification score is {diversification['diversification_score']}/100.",
                'priority': 'high' if diversification['diversification_score'] < 40 else 'medium'
            })
        
        # Sort recommendations by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        return jsonify({
            'portfolio_value': total_value,
            'asset_allocation': asset_allocation,
            'risk_metrics': risk_metrics,
            'diversification': diversification,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Portfolio analysis error: {str(e)}'}), 500

@functions_framework.http
def generate_investment_strategy(request):
    """API endpoint for generating an investment strategy.
    This is used by the Agent to create personalized investment strategies.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with investment strategy
    """
    # Check that request is JSON
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    request_data = request.get_json()
    
    # Validate required parameters
    if 'investor_profile' not in request_data:
        return jsonify({'error': 'Missing investor profile'}), 400
    
    try:
        investor_profile = request_data['investor_profile']
        
        # Extract key investor parameters
        risk_tolerance = investor_profile.get('risk_tolerance', 'moderate')
        investment_horizon = investor_profile.get('investment_horizon', 'medium')
        investment_goals = investor_profile.get('investment_goals', [])
        
        # Generate overall strategy based on investor profile
        strategy = generate_overall_strategy(
            risk_tolerance, 
            investment_horizon, 
            investment_goals
        )
        
        # If existing portfolio provided, generate transition plan
        if 'current_portfolio' in request_data:
            current_portfolio = request_data['current_portfolio']
            transition_plan = generate_transition_plan(
                current_portfolio, 
                strategy, 
                risk_tolerance
            )
            strategy['transition_plan'] = transition_plan
        
        return jsonify({
            'investment_strategy': strategy,
            'generated_at': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Strategy generation error: {str(e)}'}), 500

def generate_overall_strategy(risk_tolerance, investment_horizon, investment_goals):
    """Generate an overall investment strategy based on investor profile
    
    Args:
        risk_tolerance: Risk tolerance level (conservative, moderate, aggressive)
        investment_horizon: Investment time horizon (short, medium, long)
        investment_goals: List of investment goals
        
    Returns:
        Dictionary with investment strategy details
    """
    # Define asset allocation based on risk profile
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
    
    # Define investment approaches based on goals
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
    
    # Generate recommended approach for volatility
    volatility_approach = generate_volatility_approach(risk_tolerance)
    
    return {
        'asset_allocation': allocation,
        'goal_based_approaches': approaches,
        'volatility_approach': volatility_approach,
        'rebalancing_frequency': 'Quarterly' if risk_tolerance == 'aggressive' else 'Semi-annually',
        'tax_efficiency_focus': 'High' if sum(goal.get('amount', 0) for goal in investment_goals) > 500000 else 'Medium'
    }

def generate_volatility_approach(risk_tolerance):
    """Generate approach for handling market volatility
    
    Args:
        risk_tolerance: Risk tolerance level
        
    Returns:
        Dictionary with volatility approach details
    """
    approaches = {
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
    
    return approaches.get(risk_tolerance, approaches['moderate'])

def generate_transition_plan(current_portfolio, target_strategy, risk_tolerance):
    """Generate a transition plan from current portfolio to target strategy
    
    Args:
        current_portfolio: Current portfolio holdings
        target_strategy: Target investment strategy
        risk_tolerance: Risk tolerance level
        
    Returns:
        Dictionary with transition plan details
    """
    # Analyze current asset allocation
    current_allocation = {
        'stocks': 0,
        'bonds': 0,
        'cash': 0,
        'alternatives': 0
    }
    
    total_value = sum(holding.get('value', 0) for holding in current_portfolio)
    
    for holding in current_portfolio:
        asset_class = holding.get('asset_class', '').lower()
        value = holding.get('value', 0)
        
        if asset_class in current_allocation:
            current_allocation[asset_class] += value / total_value * 100
    
    # Get target allocation from strategy
    target_allocation = target_strategy.get('asset_allocation', {})
    
    # Calculate differences
    allocation_diff = {
        asset: target_allocation.get(asset, 0) - current_allocation.get(asset, 0)
        for asset in target_allocation
    }
    
    # Generate transition timeline based on risk tolerance
    timeline = {
        'conservative': '12-18 months',
        'moderate': '6-12 months',
        'aggressive': '3-6 months'
    }.get(risk_tolerance, '6-12 months')
    
    # Generate transition steps
    steps = []
    
    for asset, diff in allocation_diff.items():
        if abs(diff) >= 5:  # Only address significant differences (5% or more)
            if diff > 0:
                steps.append({
                    'action': f"Increase {asset} allocation",
                    'change': f"+{round(diff, 1)}%",
                    'description': f"Gradually increase {asset} allocation through regular investments.",
                    'priority': 'high' if diff > 15 else 'medium' if diff > 10 else 'low'
                })
            else:
                steps.append({
                    'action': f"Decrease {asset} allocation",
                    'change': f"{round(diff, 1)}%",
                    'description': f"Reduce {asset} exposure through strategic sales or rebalancing.",
                    'priority': 'high' if diff < -15 else 'medium' if diff < -10 else 'low'
                })
    
    # Sort steps by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    steps.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    return {
        'current_allocation': current_allocation,
        'target_allocation': target_allocation,
        'timeline': timeline,
        'implementation_steps': steps,
        'tax_considerations': [
            'Consider implementing changes in tax-advantaged accounts first to minimize tax impact',
            'Prioritize selling over-valued assets or those with tax losses if reducing allocation',
            'Establish regular investment schedule to achieve target allocation over the transition period'
        ]
    }

@functions_framework.http
def execute_portfolio_action(request):
    """API endpoint for executing portfolio actions.
    This is used by the Agent to implement investment decisions.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with execution results
    """
    # Check that request is JSON
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    request_data = request.get_json()
    
    # Validate required parameters
    if 'action_type' not in request_data or 'investor_id' not in request_data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    action_type = request_data['action_type']
    investor_id = request_data['investor_id']
    
    try:
        # Import here to avoid circular imports
        from trade_executor import execute_trades, approve_pending_trades
        
        # Handle different action types
        if action_type == 'execute_trades':
            # Validate trades parameter
            if 'trades' not in request_data:
                return jsonify({'error': 'Missing trades parameter'}), 400
            
            # Call the trade executor
            result = execute_trades({
                'trades': request_data['trades'],
                'investor_id': investor_id,
                'execution_mode': request_data.get('execution_mode', 'approval_required')
            })
            
            return result
            
        elif action_type == 'approve_trades':
            # Validate pending_id parameter
            if 'pending_id' not in request_data:
                return jsonify({'error': 'Missing pending_id parameter'}), 400
            
            # Call the approve trades function
            result = approve_pending_trades({
                'pending_id': request_data['pending_id'],
                'investor_id': investor_id
            })
            
            return result
            
        elif action_type == 'rebalance_portfolio':
            # Call the portfolio optimization function
            from portfolio_manager import portfolio_optimization
            
            # Validate holdings parameter
            if 'holdings' not in request_data:
                return jsonify({'error': 'Missing holdings parameter'}), 400
            
            result = portfolio_optimization({
                'holdings': request_data['holdings'],
                'risk_tolerance': request_data.get('risk_tolerance', 'medium'),
                'objective': request_data.get('objective', 'balanced')
            })
            
            return result
            
        else:
            return jsonify({'error': f'Unsupported action type: {action_type}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Action execution error: {str(e)}'}), 500

@functions_framework.http
def educational_content(request):
    """API endpoint for retrieving educational content about investing.
    This is used by the Agent to provide personalized educational material.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with educational content
    """
    # Get query parameters
    topic = request.args.get('topic', '').lower()
    expertise_level = request.args.get('level', 'beginner').lower()
    
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
    
    # Return relevant content based on topic and expertise level
    if topic in content_library:
        if expertise_level in content_library[topic]:
            return jsonify({
                'content': content_library[topic][expertise_level],
                'related_topics': list(set(content_library.keys()) - {topic})
            })
        else:
            # Default to beginner if specified level not found
            return jsonify({
                'content': content_library[topic]['beginner'],
                'related_topics': list(set(content_library.keys()) - {topic}),
                'note': f"Content for '{expertise_level}' level not found, providing beginner content instead."
            })
    else:
        # Return available topics if requested topic not found
        return jsonify({
            'available_topics': list(content_library.keys()),
            'error': f"Topic '{topic}' not found"
        }), 404
