
import functions_framework
from flask import jsonify
import json
import datetime

@functions_framework.http
def generate_strategy(request):
    """
    Cloud Function to generate trading strategies based on stock data and investor profile.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON with strategy recommendations
    """
    # Get the request JSON
    request_json = request.get_json(silent=True)
    
    # Check if request contains needed parameters
    if not request_json or 'symbol' not in request_json:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    symbol = request_json['symbol']
    
    # Optional parameters
    risk_profile = request_json.get('risk_profile', 'moderate')  # conservative, moderate, aggressive
    investment_horizon = request_json.get('investment_horizon', 'medium')  # short, medium, long
    stock_data = request_json.get('stock_data', None)
    
    # If stock data wasn't provided, we'd normally fetch it
    # For the hackathon, we'll assume it's provided to avoid duplicate API calls
    if not stock_data:
        return jsonify({'error': 'Stock data required'}), 400
    
    # Generate strategies based on stock data and investor profile
    strategies = generate_strategies(symbol, stock_data, risk_profile, investment_horizon)
    
    return jsonify({
        'symbol': symbol,
        'risk_profile': risk_profile,
        'investment_horizon': investment_horizon,
        'strategies': strategies,
        'generation_timestamp': datetime.datetime.now().isoformat()
    })

def generate_strategies(symbol, stock_data, risk_profile, investment_horizon):
    """
    Generate personalized investment strategies
    
    Args:
        symbol: Stock ticker symbol
        stock_data: Dictionary with stock analysis data
        risk_profile: Investor risk profile (conservative, moderate, aggressive)
        investment_horizon: Investment time horizon (short, medium, long)
        
    Returns:
        List of strategy recommendations
    """
    strategies = []
    
    # Extract key metrics
    volatility = stock_data.get('volatility', 0)
    momentum = stock_data.get('momentum', 0)
    
    # Check if options data is available
    options_available = False
    if 'options_data' in stock_data and stock_data['options_data'].get('available', False):
        options_available = True
        options_data = stock_data['options_data']
    
    # Get institutional sentiment if available
    institutional_sentiment = 'neutral'
    if 'institutional_indicator' in stock_data:
        institutional_sentiment = stock_data['institutional_indicator'].get('sentiment', 'neutral')
    
    # Adjust strategy selection based on risk profile
    risk_multiplier = {
        'conservative': 0.5,
        'moderate': 1.0,
        'aggressive': 1.5
    }[risk_profile]
    
    # Adjust based on time horizon
    horizon_factor = {
        'short': 0.7,
        'medium': 1.0,
        'long': 1.3
    }[investment_horizon]
    
    # Base strategies with risk scores (1-10)
    base_strategies = [
        # Long stock strategies
        {
            'type': 'long_position',
            'description': f"Buy {symbol} shares and hold",
            'risk_level': 4 * risk_multiplier,
            'time_horizon': 'any',
            'conditions': {'momentum_min': 0}
        },
        {
            'type': 'buy_dips',
            'description': f"Gradually buy {symbol} on price dips",
            'risk_level': 3 * risk_multiplier,
            'time_horizon': 'medium',
            'conditions': {'momentum_min': -15, 'momentum_max': 0, 'volatility_min': 20}
        },
        {
            'type': 'momentum_swing',
            'description': f"Buy {symbol} with upward momentum and trailing stop",
            'risk_level': 6 * risk_multiplier,
            'time_horizon': 'short',
            'conditions': {'momentum_min': 8, 'volatility_min': 25}
        },
        
        # Options strategies
        {
            'type': 'covered_call',
            'description': f"Buy {symbol} shares and sell covered calls for income",
            'risk_level': 3 * risk_multiplier,
            'time_horizon': 'medium',
            'conditions': {'options': True, 'momentum_min': -5, 'momentum_max': 10}
        },
        {
            'type': 'bull_call_spread',
            'description': f"Bull call spread on {symbol} to profit from moderate upside",
            'risk_level': 5 * risk_multiplier,
            'time_horizon': 'short',
            'conditions': {'options': True, 'momentum_min': 5}
        },
        {
            'type': 'bear_put_spread',
            'description': f"Bear put spread on {symbol} to profit from moderate downside",
            'risk_level': 5 * risk_multiplier,
            'time_horizon': 'short',
            'conditions': {'options': True, 'momentum_max': -5}
        },
        {
            'type': 'iron_condor',
            'description': f"Iron condor on {symbol} to profit from sideways movement",
            'risk_level': 6 * risk_multiplier,
            'time_horizon': 'short',
            'conditions': {'options': True, 'volatility_min': 30, 'momentum_min': -7, 'momentum_max': 7}
        },
        {
            'type': 'protective_put',
            'description': f"Buy {symbol} shares with protective puts for downside protection",
            'risk_level': 4 * risk_multiplier,
            'time_horizon': 'medium',
            'conditions': {'options': True, 'momentum_min': 0}
        },
        {
            'type': 'straddle',
            'description': f"Long straddle on {symbol} to profit from big move in either direction",
            'risk_level': 7 * risk_multiplier,
            'time_horizon': 'short',
            'conditions': {'options': True, 'volatility_min': 35, 'momentum_min': -5, 'momentum_max': 5}
        },
        
        # Conservative strategies
        {
            'type': 'dollar_cost_averaging',
            'description': f"Regularly buy {symbol} in fixed dollar amounts regardless of price",
            'risk_level': 2 * risk_multiplier,
            'time_horizon': 'long',
            'conditions': {'volatility_max': 40}
        },
        {
            'type': 'wait_and_watch',
            'description': f"Monitor {symbol} for better entry points",
            'risk_level': 1 * risk_multiplier,
            'time_horizon': 'any',
            'conditions': {}  # Always available as fallback
        }
    ]
    
    # Filter strategies based on conditions and investor profile
    appropriate_strategies = []
    
    for strategy in base_strategies:
        # Skip options strategies if options aren't available
        if strategy['conditions'].get('options', False) and not options_available:
            continue
        
        # Check momentum conditions
        if 'momentum_min' in strategy['conditions'] and momentum < strategy['conditions']['momentum_min']:
            continue
        if 'momentum_max' in strategy['conditions'] and momentum > strategy['conditions']['momentum_max']:
            continue
        
        # Check volatility conditions
        if 'volatility_min' in strategy['conditions'] and volatility < strategy['conditions']['volatility_min']:
            continue
        if 'volatility_max' in strategy['conditions'] and volatility > strategy['conditions']['volatility_max']:
            continue
        
        # Check time horizon compatibility
        if strategy['time_horizon'] != 'any' and strategy['time_horizon'] != investment_horizon:
            # Allow medium strategies for long-term investors and short strategies for medium-term
            if not (strategy['time_horizon'] == 'medium' and investment_horizon == 'long') and \
               not (strategy['time_horizon'] == 'short' and investment_horizon == 'medium' and risk_profile == 'aggressive'):
                continue
        
        # Calculate effective risk level
        effective_risk = strategy['risk_level'] * horizon_factor
        
        # Conservative investors only get low-risk strategies
        if risk_profile == 'conservative' and effective_risk > 5:
            continue
        
        # Moderate investors avoid the highest risk strategies
        if risk_profile == 'moderate' and effective_risk > 8:
            continue
        
        # Add institutional sentiment context
        strategy_with_context = strategy.copy()
        
        # Adjust description based on institutional sentiment
        if institutional_sentiment == 'bullish' and 'bull' in strategy['type']:
            strategy_with_context['description'] += " (aligned with bullish institutional sentiment)"
            strategy_with_context['institutional_alignment'] = 'aligned'
        elif institutional_sentiment == 'bearish' and 'bear' in strategy['type']:
            strategy_with_context['description'] += " (aligned with bearish institutional sentiment)"
            strategy_with_context['institutional_alignment'] = 'aligned'
        elif institutional_sentiment == 'bullish' and 'bear' in strategy['type']:
            strategy_with_context['description'] += " (contrary to bullish institutional sentiment)"
            strategy_with_context['institutional_alignment'] = 'contrary'
        elif institutional_sentiment == 'bearish' and 'bull' in strategy['type']:
            strategy_with_context['description'] += " (contrary to bearish institutional sentiment)"
            strategy_with_context['institutional_alignment'] = 'contrary'
        else:
            strategy_with_context['institutional_alignment'] = 'neutral'
        
        # Add effective risk score
        strategy_with_context['effective_risk_score'] = round(effective_risk, 1)
        
        # Remove internal condition data before returning
        if 'conditions' in strategy_with_context:
            del strategy_with_context['conditions']
        
        appropriate_strategies.append(strategy_with_context)
    
    # Ensure at least one strategy is returned (wait and watch as fallback)
    if not appropriate_strategies:
        appropriate_strategies.append({
            'type': 'wait_and_watch',
            'description': f"Current market conditions for {symbol} don't align well with your investment profile. Consider monitoring for better opportunities.",
            'risk_level': 1,
            'effective_risk_score': 1,
            'institutional_alignment': 'neutral'
        })
    
    # Sort strategies by effective risk (lowest first for conservative, highest first for aggressive)
    if risk_profile == 'aggressive':
        appropriate_strategies.sort(key=lambda x: x['effective_risk_score'], reverse=True)
    else:
        appropriate_strategies.sort(key=lambda x: x['effective_risk_score'])
    
    # Generate detailed implementation steps for each strategy
    for strategy in appropriate_strategies:
        strategy['implementation_steps'] = generate_implementation_steps(strategy['type'], symbol, stock_data)
    
    return appropriate_strategies

def generate_implementation_steps(strategy_type, symbol, stock_data):
    """
    Generate detailed implementation steps for a specific strategy
    
    Args:
        strategy_type: Type of strategy
        symbol: Stock ticker symbol
        stock_data: Dictionary with stock analysis data
        
    Returns:
        List of implementation steps
    """
    price = stock_data.get('price', 100)  # Default if not provided
    
    # Strategy-specific implementation steps
    implementations = {
        'long_position': [
            f"Research {symbol} fundamentals and recent news",
            f"Determine position size based on your risk management rules",
            f"Place a limit order slightly below current price (${price - (price * 0.01):.2f})",
            "Consider setting a stop loss 5-10% below purchase price",
            "Monitor earnings announcements and major news events"
        ],
        'buy_dips': [
            f"Set price alert for {symbol} at support levels",
            "Prepare 3-4 equal-sized buy orders",
            "Execute first buy order when price dips 3-5%",
            "Add to position with subsequent orders on further dips of 3-5%",
            "Set trailing stop loss once full position is established"
        ],
        'momentum_swing': [
            f"Confirm {symbol} uptrend using moving averages (20-day above 50-day)",
            "Enter on pullback to support or moving average",
            "Set tight stop loss at recent swing low",
            "Take partial profits at 1:1 risk-reward ratio",
            "Trail stop loss for remaining position"
        ],
        'covered_call': [
            f"Buy 100 shares of {symbol} at market price",
            f"Sell 1 call option contract with strike price 5-10% above current price",
            "Choose expiration 30-45 days away",
            "If stock stays below strike price at expiration, keep premium and repeat",
            "If stock rises above strike, prepare to have shares called away or roll option"
        ],
        'bull_call_spread': [
            f"Buy {symbol} call option at or slightly in-the-money",
            "Sell call option at higher strike price (same expiration)",
            "Choose expiration 30-60 days out",
            f"Maximum risk is the net premium paid",
            "Maximum profit achieved if stock closes above higher strike at expiration"
        ],
        'bear_put_spread': [
            f"Buy {symbol} put option at or slightly in-the-money",
            "Sell put option at lower strike price (same expiration)",
            "Choose expiration 30-60 days out",
            f"Maximum risk is the net premium paid",
            "Maximum profit achieved if stock closes below lower strike at expiration"
        ],
        'iron_condor': [
            f"Sell out-of-the-money put on {symbol} (lower strike)",
            f"Buy further out-of-the-money put (lowest strike)",
            f"Sell out-of-the-money call (upper strike)",
            f"Buy further out-of-the-money call (highest strike)",
            "Choose same expiration for all options (30-45 days)",
            "Profit if stock stays between lower and upper strikes at expiration"
        ],
        'protective_put': [
            f"Buy 100 shares of {symbol} at market price",
            f"Buy 1 put option contract with strike near current price",
            "Choose expiration 3-6 months away",
            "This limits downside risk to the put strike price minus premium paid",
            "Rolling puts forward as they approach expiration maintains protection"
        ],
        'straddle': [
            f"Buy {symbol} call option at-the-money",
            f"Buy {symbol} put option at-the-money (same strike and expiration)",
            "Choose expiration 30-60 days out",
            "Profit if stock moves significantly in either direction",
            "Consider closing position if implied volatility spikes, even if stock hasn't moved much"
        ],
        'dollar_cost_averaging': [
            f"Determine total position size for {symbol}",
            "Divide into equal portions (e.g., 12 monthly or 52 weekly buys)",
            "Set up automatic purchases at regular intervals",
            "Continue regardless of price movements",
            "Review strategy annually or after significant market changes"
        ],
        'wait_and_watch': [
            f"Set price alerts for {symbol} at key technical levels",
            "Monitor for changes in institutional sentiment",
            "Watch for unusual options activity",
            "Look for volatility compression before breakouts",
            "Set calendar reminder to re-evaluate in 2-4 weeks"
        ]
    }
    
    # Return steps for the specific strategy or generic steps if not found
    return implementations.get(strategy_type, [
        "Research the company thoroughly",
        "Monitor price action for entry signals",
        "Determine position size based on risk tolerance",
        "Set clear exit criteria before entering",
        "Document your strategy and rationale"
    ])
