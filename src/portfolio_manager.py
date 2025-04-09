
import functions_framework
from flask import jsonify
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from concurrent.futures import ThreadPoolExecutor

@functions_framework.http
def analyze_portfolio(request):
    """
    Cloud Function that analyzes a portfolio of holdings.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON response with portfolio analysis results
    """
    # Get the request JSON
    request_json = request.get_json(silent=True)
    
    # Check if request contains needed parameters
    if not request_json or 'holdings' not in request_json:
        return jsonify({'error': 'Missing holdings parameter'}), 400
    
    holdings = request_json['holdings']
    risk_profile = request_json.get('risk_profile', 'moderate')
    
    # Calculate portfolio metrics
    try:
        # Basic portfolio metrics
        total_value = sum(holding.get('value', 0) for holding in holdings)
        
        # Calculate asset allocation
        asset_allocation = calculate_asset_allocation(holdings)
        
        # Calculate risk metrics
        risk_metrics = calculate_risk_metrics(holdings)
        
        # Calculate diversification metrics
        diversification = calculate_diversification(holdings)
        
        # Generate recommendations
        recommendations = generate_portfolio_recommendations(
            holdings, 
            asset_allocation, 
            risk_metrics, 
            diversification,
            risk_profile
        )
        
        # Return analysis results
        return jsonify({
            'portfolio_value': total_value,
            'asset_allocation': asset_allocation,
            'risk_metrics': risk_metrics,
            'diversification': diversification,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

def calculate_asset_allocation(holdings):
    """
    Calculate asset allocation breakdown
    
    Args:
        holdings: List of portfolio holdings
        
    Returns:
        Dictionary with asset allocation data
    """
    # Group by asset class
    asset_classes = {}
    total_value = sum(holding.get('value', 0) for holding in holdings)
    
    # Sum up values by asset class
    for holding in holdings:
        asset_class = holding.get('asset_class', 'unknown')
        if asset_class not in asset_classes:
            asset_classes[asset_class] = 0
        asset_classes[asset_class] += holding.get('value', 0)
    
    # Convert to percentages
    asset_allocation = {
        asset_class: {
            'value': value,
            'percentage': (value / total_value * 100) if total_value > 0 else 0
        }
        for asset_class, value in asset_classes.items()
    }
    
    # Group by sector for equity holdings
    sectors = {}
    total_equity = asset_classes.get('equity', 0)
    
    for holding in holdings:
        if holding.get('asset_class') == 'equity':
            sector = holding.get('sector', 'unknown')
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += holding.get('value', 0)
    
    # Convert to percentages
    sector_allocation = {
        sector: {
            'value': value,
            'percentage': (value / total_equity * 100) if total_equity > 0 else 0
        }
        for sector, value in sectors.items()
    }
    
    return {
        'by_asset_class': asset_allocation,
        'by_sector': sector_allocation
    }

def calculate_risk_metrics(holdings):
    """
    Calculate portfolio risk metrics
    
    Args:
        holdings: List of portfolio holdings
        
    Returns:
        Dictionary with risk metrics data
    """
    # Get symbols
    symbols = [holding.get('symbol') for holding in holdings if holding.get('symbol')]
    weights = []
    
    # Calculate weights
    total_value = sum(holding.get('value', 0) for holding in holdings)
    for holding in holdings:
        if holding.get('symbol'):
            weight = holding.get('value', 0) / total_value if total_value > 0 else 0
            weights.append(weight)
    
    # For hackathon, use simplified metrics
    # In production, we would calculate actual portfolio volatility using historical returns
    
    # Download historical data for all symbols at once
    try:
        # Get history for past 2 years
        data = yf.download(symbols, period="2y")['Adj Close']
        
        # Calculate daily returns
        returns = data.pct_change().dropna()
        
        # Calculate volatility
        volatility = returns.std() * np.sqrt(252) * 100
        
        # Calculate portfolio volatility (simplified approach)
        portfolio_volatility = 0
        
        # If we have multiple securities, calculate using covariance
        if len(symbols) > 1:
            # Calculate covariance matrix
            cov_matrix = returns.cov() * 252
            # Convert weights to numpy array
            np_weights = np.array(weights)
            # Calculate portfolio variance
            portfolio_variance = np_weights.T.dot(cov_matrix).dot(np_weights)
            # Take square root to get volatility
            portfolio_volatility = np.sqrt(portfolio_variance) * 100
        else:
            # For single security, just use its volatility
            portfolio_volatility = volatility.iloc[0] if len(volatility) > 0 else 0
        
        # Calculate max drawdown
        max_drawdown = calculate_max_drawdown(returns, weights)
        
        return {
            'portfolio_volatility': round(float(portfolio_volatility), 2),
            'max_drawdown': round(float(max_drawdown), 2),
            'sharpe_ratio': 0.8,  # Placeholder for hackathon
            'beta': 1.1  # Placeholder for hackathon
        }
    
    except Exception as e:
        print(f"Error calculating risk metrics: {str(e)}")
        # Return placeholder data for hackathon
        return {
            'portfolio_volatility': 12.5,
            'max_drawdown': -15.3,
            'sharpe_ratio': 0.8,
            'beta': 1.1
        }

def calculate_max_drawdown(returns, weights):
    """
    Calculate maximum drawdown for the portfolio
    
    Args:
        returns: DataFrame of historical returns
        weights: List of portfolio weights
        
    Returns:
        Maximum drawdown percentage
    """
    try:
        # Calculate portfolio returns based on weights
        portfolio_returns = returns.dot(weights)
        
        # Calculate cumulative returns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.cummax()
        
        # Calculate drawdown
        drawdown = (cumulative_returns / running_max - 1) * 100
        
        # Find maximum drawdown
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    except Exception as e:
        print(f"Error calculating max drawdown: {str(e)}")
        return -15.0  # Placeholder for hackathon

def calculate_diversification(holdings):
    """
    Calculate portfolio diversification metrics
    
    Args:
        holdings: List of portfolio holdings
        
    Returns:
        Dictionary with diversification metrics
    """
    # Count unique asset classes, sectors, and securities
    asset_classes = set()
    sectors = set()
    securities = set()
    
    for holding in holdings:
        if holding.get('asset_class'):
            asset_classes.add(holding.get('asset_class'))
        
        if holding.get('sector'):
            sectors.add(holding.get('sector'))
        
        if holding.get('symbol'):
            securities.add(holding.get('symbol'))
    
    # Calculate concentration metrics
    total_value = sum(holding.get('value', 0) for holding in holdings)
    
    # Top holding concentration
    sorted_holdings = sorted(holdings, key=lambda x: x.get('value', 0), reverse=True)
    top_holding_concentration = 0
    if sorted_holdings and total_value > 0:
        top_holding_concentration = sorted_holdings[0].get('value', 0) / total_value * 100
    
    # Top 5 holdings concentration
    top5_concentration = 0
    if len(sorted_holdings) >= 5 and total_value > 0:
        top5_value = sum(h.get('value', 0) for h in sorted_holdings[:5])
        top5_concentration = top5_value / total_value * 100
    
    # Calculate Herfindahl-Hirschman Index (HHI) for concentration
    hhi = 0
    if total_value > 0:
        hhi = sum((holding.get('value', 0) / total_value * 100) ** 2 for holding in holdings)
    
    # Create diversification score (0-100)
    # Higher is better diversified
    # Factors: number of assets, HHI, top holding concentration
    diversification_score = 100
    
    # Reduce score based on too few securities
    if len(securities) < 10:
        diversification_score -= (10 - len(securities)) * 5
    
    # Reduce score based on HHI (high concentration)
    if hhi > 1000:
        diversification_score -= min(50, (hhi - 1000) / 200)
    
    # Reduce score based on top holding concentration
    if top_holding_concentration > 15:
        diversification_score -= min(30, (top_holding_concentration - 15) * 2)
    
    # Ensure score is between 0-100
    diversification_score = max(0, min(100, diversification_score))
    
    return {
        'asset_class_count': len(asset_classes),
        'sector_count': len(sectors),
        'security_count': len(securities),
        'top_holding_concentration': round(top_holding_concentration, 2),
        'top5_concentration': round(top5_concentration, 2),
        'herfindahl_index': round(hhi, 2),
        'diversification_score': round(diversification_score, 2)
    }

def generate_portfolio_recommendations(holdings, asset_allocation, risk_metrics, diversification, risk_profile):
    """
    Generate portfolio recommendations based on analysis
    
    Args:
        holdings: List of portfolio holdings
        asset_allocation: Asset allocation data
        risk_metrics: Risk metrics data
        diversification: Diversification metrics
        risk_profile: Investor risk profile
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Define target asset allocations based on risk profile
    target_allocations = {
        'conservative': {'equity': 40, 'fixed_income': 50, 'alternatives': 5, 'cash': 5},
        'moderate': {'equity': 60, 'fixed_income': 30, 'alternatives': 7, 'cash': 3},
        'aggressive': {'equity': 80, 'fixed_income': 15, 'alternatives': 3, 'cash': 2}
    }
    
    selected_targets = target_allocations.get(risk_profile, target_allocations['moderate'])
    
    # Check asset allocation against targets
    current_allocation = asset_allocation['by_asset_class']
    for asset_class, target in selected_targets.items():
        current = current_allocation.get(asset_class, {'percentage': 0})['percentage']
        
        # If allocation is off by more than 10%, recommend rebalancing
        if abs(current - target) > 10:
            if current < target:
                recommendations.append({
                    'type': 'rebalance',
                    'asset_class': asset_class,
                    'current_allocation': round(current, 2),
                    'target_allocation': target,
                    'description': f"Increase {asset_class} allocation from {round(current, 2)}% to {target}%",
                    'priority': 'high' if abs(current - target) > 20 else 'medium'
                })
            else:
                recommendations.append({
                    'type': 'rebalance',
                    'asset_class': asset_class,
                    'current_allocation': round(current, 2),
                    'target_allocation': target,
                    'description': f"Decrease {asset_class} allocation from {round(current, 2)}% to {target}%",
                    'priority': 'high' if abs(current - target) > 20 else 'medium'
                })
    
    # Check diversification
    if diversification['diversification_score'] < 60:
        recommendations.append({
            'type': 'diversification',
            'description': "Improve portfolio diversification by adding more securities across different sectors",
            'details': f"Your diversification score is {diversification['diversification_score']}/100.",
            'priority': 'high' if diversification['diversification_score'] < 40 else 'medium'
        })
    
    # Check concentration risk
    if diversification['top_holding_concentration'] > 20:
        top_holding = sorted(holdings, key=lambda x: x.get('value', 0), reverse=True)[0]
        recommendations.append({
            'type': 'concentration',
            'description': f"Reduce position size in {top_holding.get('name', top_holding.get('symbol', 'top holding'))}",
            'details': f"Your largest position represents {round(diversification['top_holding_concentration'], 2)}% of your portfolio.",
            'priority': 'high' if diversification['top_holding_concentration'] > 30 else 'medium'
        })
    
    # Check sector concentration
    sector_allocation = asset_allocation['by_sector']
    for sector, data in sector_allocation.items():
        if data['percentage'] > 30:
            recommendations.append({
                'type': 'sector_concentration',
                'sector': sector,
                'current_allocation': round(data['percentage'], 2),
                'description': f"Reduce concentration in {sector} sector from {round(data['percentage'], 2)}%",
                'priority': 'medium'
            })
    
    # Check risk level against profile
    target_volatility = {
        'conservative': 10,
        'moderate': 15,
        'aggressive': 20
    }
    
    portfolio_volatility = risk_metrics['portfolio_volatility']
    volatility_target = target_volatility.get(risk_profile, 15)
    
    if portfolio_volatility > volatility_target * 1.2:  # 20% higher than target
        recommendations.append({
            'type': 'risk_reduction',
            'description': f"Reduce portfolio risk. Current volatility ({portfolio_volatility}%) exceeds target for {risk_profile} profile.",
            'details': "Consider adding more defensive positions or fixed income to reduce overall volatility.",
            'priority': 'high'
        })
    elif portfolio_volatility < volatility_target * 0.8:  # 20% lower than target
        recommendations.append({
            'type': 'risk_increase',
            'description': f"Consider increasing risk exposure. Current volatility ({portfolio_volatility}%) is below target for {risk_profile} profile.",
            'details': "You may be missing out on potential returns given your risk tolerance.",
            'priority': 'low'
        })
    
    # Sort recommendations by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    return recommendations

@functions_framework.http
def portfolio_optimization(request):
    """
    Cloud Function to optimize a portfolio based on modern portfolio theory.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with optimized portfolio allocation
    """
    # Get the request JSON
    request_json = request.get_json(silent=True)
    
    # Check if request contains needed parameters
    if not request_json or 'holdings' not in request_json:
        return jsonify({'error': 'Missing holdings parameter'}), 400
    
    holdings = request_json['holdings']
    risk_tolerance = request_json.get('risk_tolerance', 'medium')  # low, medium, high
    objective = request_json.get('objective', 'balanced')  # income, balanced, growth
    
    try:
        # Get list of symbols from holdings
        symbols = [h.get('symbol') for h in holdings if h.get('symbol')]
        
        # Current weights in portfolio
        total_value = sum(h.get('value', 0) for h in holdings)
        current_weights = {h.get('symbol'): h.get('value', 0) / total_value for h in holdings if h.get('symbol')}
        
        # Get historical data for optimization
        historical_data = get_historical_data(symbols)
        
        # Run optimization
        optimized_weights = optimize_portfolio(
            historical_data, 
            risk_tolerance,
            objective,
            current_weights
        )
        
        # Create rebalancing recommendations
        rebalancing_plan = create_rebalancing_plan(
            holdings,
            optimized_weights,
            total_value
        )
        
        # Calculate expected metrics for the optimized portfolio
        expected_metrics = calculate_expected_metrics(
            historical_data,
            optimized_weights
        )
        
        return jsonify({
            'optimized_weights': optimized_weights,
            'rebalancing_plan': rebalancing_plan,
            'expected_metrics': expected_metrics,
            'optimization_timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Optimization error: {str(e)}'}), 500

def get_historical_data(symbols, period="2y"):
    """
    Get historical price data for a list of symbols
    
    Args:
        symbols: List of ticker symbols
        period: Lookback period
        
    Returns:
        DataFrame with historical returns
    """
    # Download historical data
    data = yf.download(symbols, period=period)['Adj Close']
    
    # Calculate returns
    returns = data.pct_change().dropna()
    
    return returns

def optimize_portfolio(returns, risk_tolerance, objective, current_weights):
    """
    Optimize portfolio weights based on modern portfolio theory
    
    Args:
        returns: Historical returns DataFrame
        risk_tolerance: Risk tolerance level
        objective: Investment objective
        current_weights: Current portfolio weights
        
    Returns:
        Dictionary with optimized weights
    """
    # For hackathon, use a simplified optimization approach
    # In production, would use quadratic programming for proper MPT optimization
    
    # Calculate expected returns (annualized)
    expected_returns = returns.mean() * 252
    
    # Calculate covariance matrix (annualized)
    cov_matrix = returns.cov() * 252
    
    # Risk tolerance factor (higher = more risk)
    risk_factors = {
        'low': 0.5,
        'medium': 1.0,
        'high': 2.0
    }
    
    # Objective factor (higher = more growth focus)
    objective_factors = {
        'income': 0.5,
        'balanced': 1.0,
        'growth': 1.5
    }
    
    risk_factor = risk_factors.get(risk_tolerance, 1.0)
    objective_factor = objective_factors.get(objective, 1.0)
    
    # Simplified optimization - adjust weights based on risk/return profile
    # This is a very simplistic approach for the hackathon
    # Real optimization would solve the quadratic programming problem
    
    # Start with equal weights as baseline
    equal_weights = {symbol: 1.0 / len(returns.columns) for symbol in returns.columns}
    
    # Calculate volatility for each asset
    volatility = np.sqrt(np.diag(cov_matrix))
    volatility_dict = {symbol: vol for symbol, vol in zip(returns.columns, volatility)}
    
    # Calculate Sharpe ratio for each asset (assuming risk-free rate of 0.02)
    risk_free_rate = 0.02
    sharpe_ratios = {symbol: (er - risk_free_rate) / volatility_dict[symbol] 
                    if volatility_dict[symbol] > 0 else 0 
                    for symbol, er in expected_returns.items()}
    
    # Adjust weights based on Sharpe ratios and risk tolerance
    total_sharpe = sum(max(0, sr) for sr in sharpe_ratios.values())
    if total_sharpe > 0:
        # Higher Sharpe ratio = higher weight
        sharpe_weights = {symbol: max(0, sharpe_ratios[symbol]) / total_sharpe 
                         for symbol in sharpe_ratios}
    else:
        # If all Sharpe ratios are negative, use inverse volatility weighting
        total_inv_vol = sum(1 / vol if vol > 0 else 0 for vol in volatility_dict.values())
        sharpe_weights = {symbol: (1 / volatility_dict[symbol]) / total_inv_vol 
                         if volatility_dict[symbol] > 0 else 0 
                         for symbol in volatility_dict}
    
    # Create a blend based on risk tolerance and objective
    blend_factor = risk_factor * objective_factor
    blended_weights = {}
    
    for symbol in returns.columns:
        # More aggressive = more weight on Sharpe-based allocation
        # More conservative = more weight on equal-weighted allocation
        if blend_factor > 1:
            # More aggressive than default
            blended_weights[symbol] = sharpe_weights.get(symbol, 0)
        else:
            # More conservative than default
            blended_weights[symbol] = (blend_factor * sharpe_weights.get(symbol, 0) + 
                                     (1 - blend_factor) * equal_weights.get(symbol, 0))
    
    # Ensure weights sum to 1
    total_weight = sum(blended_weights.values())
    normalized_weights = {symbol: weight / total_weight for symbol, weight in blended_weights.items()}
    
    # Convert weights to percentages
    return {symbol: round(weight * 100, 2) for symbol, weight in normalized_weights.items()}

def create_rebalancing_plan(holdings, optimized_weights, total_value):
    """
    Create a rebalancing plan based on optimized weights
    
    Args:
        holdings: Current portfolio holdings
        optimized_weights: Optimized portfolio weights in percentage
        total_value: Total portfolio value
        
    Returns:
        List of rebalancing actions
    """
    rebalancing_actions = []
    
    # Create lookup for current holdings
    holdings_dict = {h.get('symbol'): h for h in holdings if h.get('symbol')}
    
    # Calculate current weights
    current_weights = {h.get('symbol'): h.get('value', 0) / total_value * 100 
                     for h in holdings if h.get('symbol')}
    
    # For each holding in optimized weights
    for symbol, target_weight in optimized_weights.items():
        current_weight = current_weights.get(symbol, 0)
        
        # Calculate the difference
        weight_diff = target_weight - current_weight
        value_diff = (weight_diff / 100) * total_value
        
        # If difference is significant (> 1%), add to rebalance plan
        if abs(weight_diff) >= 1:
            holding = holdings_dict.get(symbol, {'symbol': symbol})
            
            if weight_diff > 0:
                rebalancing_actions.append({
                    'symbol': symbol,
                    'name': holding.get('name', symbol),
                    'action': 'buy',
                    'current_weight': round(current_weight, 2),
                    'target_weight': round(target_weight, 2),
                    'weight_difference': round(weight_diff, 2),
                    'value_difference': round(value_diff, 2),
                    'approximate_amount': f"${abs(int(value_diff))}"
                })
            else:
                rebalancing_actions.append({
                    'symbol': symbol,
                    'name': holding.get('name', symbol),
                    'action': 'sell',
                    'current_weight': round(current_weight, 2),
                    'target_weight': round(target_weight, 2),
                    'weight_difference': round(weight_diff, 2),
                    'value_difference': round(value_diff, 2),
                    'approximate_amount': f"${abs(int(value_diff))}"
                })
    
    # Check for new positions in optimized portfolio
    for symbol, target_weight in optimized_weights.items():
        if symbol not in current_weights and target_weight > 0:
            value_to_buy = (target_weight / 100) * total_value
            rebalancing_actions.append({
                'symbol': symbol,
                'name': symbol,  # Don't have name for new positions
                'action': 'buy_new',
                'current_weight': 0,
                'target_weight': round(target_weight, 2),
                'weight_difference': round(target_weight, 2),
                'value_difference': round(value_to_buy, 2),
                'approximate_amount': f"${int(value_to_buy)}"
            })
    
    # Check for positions to eliminate
    for symbol, current_weight in current_weights.items():
        if symbol not in optimized_weights or optimized_weights.get(symbol, 0) == 0:
            value_to_sell = (current_weight / 100) * total_value
            holding = holdings_dict.get(symbol, {'symbol': symbol})
            rebalancing_actions.append({
                'symbol': symbol,
                'name': holding.get('name', symbol),
                'action': 'sell_all',
                'current_weight': round(current_weight, 2),
                'target_weight': 0,
                'weight_difference': -round(current_weight, 2),
                'value_difference': -round(value_to_sell, 2),
                'approximate_amount': f"${int(value_to_sell)}"
            })
    
    # Sort actions by absolute value difference (largest first)
    rebalancing_actions.sort(key=lambda x: abs(x.get('value_difference', 0)), reverse=True)
    
    return rebalancing_actions

def calculate_expected_metrics(returns, optimized_weights):
    """
    Calculate expected portfolio metrics based on historical data and optimized weights
    
    Args:
        returns: Historical returns DataFrame
        optimized_weights: Optimized portfolio weights
        
    Returns:
        Dictionary with expected metrics
    """
    # Convert percentage weights back to decimals
    weights = {k: v / 100 for k, v in optimized_weights.items()}
    
    # Convert weights to array that matches returns columns
    weight_array = np.zeros(len(returns.columns))
    for i, symbol in enumerate(returns.columns):
        weight_array[i] = weights.get(symbol, 0)
    
    # Calculate expected return (annualized)
    expected_return = np.sum(returns.mean() * weight_array) * 252
    
    # Calculate expected volatility (annualized)
    cov_matrix = returns.cov() * 252
    expected_volatility = np.sqrt(np.dot(weight_array.T, np.dot(cov_matrix, weight_array)))
    
    # Calculate expected Sharpe ratio (assuming risk-free rate of 0.02)
    risk_free_rate = 0.02
    expected_sharpe = (expected_return - risk_free_rate) / expected_volatility if expected_volatility > 0 else 0
    
    return {
        'expected_annual_return': round(expected_return * 100, 2),
        'expected_volatility': round(expected_volatility * 100, 2),
        'expected_sharpe_ratio': round(expected_sharpe, 2)
    }
