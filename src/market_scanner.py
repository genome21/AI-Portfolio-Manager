
import functions_framework
from flask import jsonify
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from concurrent.futures import ThreadPoolExecutor

@functions_framework.http
def market_volatility_scan(request):
    """
    Cloud Function that scans the market for volatility opportunities.
    This is the main entry point for the market scanning functionality.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON response with market overview and volatility opportunities
    """
    # Get the request JSON
    request_json = request.get_json(silent=True)
    
    # Set default parameters
    lookback_days = request_json.get('lookback_days', 10) if request_json else 10
    volatility_threshold = request_json.get('volatility_threshold', 25) if request_json else 25
    max_results = request_json.get('max_results', 15) if request_json else 15
    
    # Step 1: Analyze market ETFs to find volatile sectors
    market_etfs = {
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq 100',
        'DIA': 'Dow Jones',
        'IWM': 'Russell 2000',
        'XLK': 'Technology',
        'XLF': 'Financial',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLI': 'Industrial',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLB': 'Materials',
        'XLU': 'Utilities',
        'XLRE': 'Real Estate',
        'XLC': 'Communication Services'
    }
    
    etf_volatility = analyze_etfs(market_etfs, lookback_days)
    
    # Step 2: Identify the 3-5 most volatile sectors
    volatile_sectors = sorted(etf_volatility, key=lambda x: x['volatility'], reverse=True)[:5]
    
    # Step 3: For each volatile sector, get constituents or related stocks
    volatile_stocks = []
    
    for sector in volatile_sectors:
        sector_stocks = get_sector_volatile_stocks(
            sector['symbol'], 
            sector['name'], 
            lookback_days, 
            volatility_threshold
        )
        volatile_stocks.extend(sector_stocks)
    
    # Step 4: Add high-volume movers from overall market (not just from volatile sectors)
    market_movers = get_market_movers(lookback_days)
    volatile_stocks.extend(market_movers)
    
    # Remove duplicates
    seen_symbols = set()
    unique_volatile_stocks = []
    for stock in volatile_stocks:
        if stock['symbol'] not in seen_symbols:
            seen_symbols.add(stock['symbol'])
            unique_volatile_stocks.append(stock)
    
    # Sort by volatility (highest first) and limit results
    unique_volatile_stocks.sort(key=lambda x: x['volatility'], reverse=True)
    top_opportunities = unique_volatile_stocks[:max_results]
    
    # Step 5: Enrich with options and institutional data
    with ThreadPoolExecutor(max_workers=min(10, len(top_opportunities))) as executor:
        executor.map(enrich_stock_data, top_opportunities)
    
    # Include sector analysis in the response
    return jsonify({
        'market_overview': {
            'analysis_date': datetime.datetime.now().isoformat(),
            'volatile_sectors': volatile_sectors
        },
        'volatility_opportunities': top_opportunities,
        'opportunity_count': len(top_opportunities)
    })

def analyze_etfs(etf_dict, lookback_days):
    """
    Analyze ETFs to identify volatile sectors
    
    Args:
        etf_dict: Dictionary of ETF symbols and names
        lookback_days: Number of days to look back for analysis
        
    Returns:
        List of ETF analysis results
    """
    results = []
    
    def process_etf(symbol, name):
        try:
            etf = yf.Ticker(symbol)
            hist = etf.history(period=f"{lookback_days + 5}d")
            
            if len(hist) < lookback_days:
                return None
            
            # Calculate daily returns
            hist['daily_return'] = hist['Close'].pct_change()
            
            # Calculate volatility
            volatility = hist['daily_return'].std() * np.sqrt(252) * 100
            
            # Calculate recent momentum
            recent_momentum = (hist['Close'].iloc[-1] / hist['Close'].iloc[-lookback_days] - 1) * 100
            
            # Calculate average volume ratio (recent vs typical)
            recent_volume = hist['Volume'].iloc[-5:].mean()
            typical_volume = hist['Volume'].iloc[:-5].mean()
            volume_ratio = recent_volume / typical_volume if typical_volume > 0 else 1.0
            
            return {
                'symbol': symbol,
                'name': name,
                'volatility': round(volatility, 2),
                'momentum': round(recent_momentum, 2),
                'volume_ratio': round(volume_ratio, 2),
                'signal': get_signal(recent_momentum, volatility, volume_ratio)
            }
        except Exception as e:
            print(f"Error analyzing ETF {symbol}: {str(e)}")
            return None
    
    # Use threads to speed up data fetching
    with ThreadPoolExecutor(max_workers=min(10, len(etf_dict))) as executor:
        tasks = {executor.submit(process_etf, symbol, name): (symbol, name) 
                 for symbol, name in etf_dict.items()}
        
        for future in tasks:
            result = future.result()
            if result:
                results.append(result)
    
    return results

def get_sector_volatile_stocks(sector_etf, sector_name, lookback_days, volatility_threshold):
    """
    Get volatile stocks from a specific sector
    
    Args:
        sector_etf: ETF symbol representing the sector
        sector_name: Name of the sector
        lookback_days: Number of days to look back for analysis
        volatility_threshold: Minimum volatility threshold
        
    Returns:
        List of volatile stocks in the sector
    """
    try:
        # For hackathon, use a simplified approach with Yahoo Finance top movers
        # In production, we'd use actual ETF constituent data
        
        # Get stocks that might be in this sector based on predefined lists
        sector_stocks = get_sector_stock_list(sector_etf)
        
        volatility_data = []
        
        def analyze_stock(symbol):
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=f"{lookback_days + 5}d")
                
                if len(hist) < lookback_days:
                    return None
                
                # Calculate daily returns
                hist['daily_return'] = hist['Close'].pct_change()
                
                # Calculate volatility
                volatility = hist['daily_return'].std() * np.sqrt(252) * 100
                
                if volatility < volatility_threshold:
                    return None
                
                # Calculate recent momentum
                recent_momentum = (hist['Close'].iloc[-1] / hist['Close'].iloc[-lookback_days] - 1) * 100
                
                # Get other data
                recent_price = hist['Close'].iloc[-1]
                avg_volume = hist['Volume'].mean()
                
                return {
                    'symbol': symbol,
                    'sector': sector_name,
                    'volatility': round(volatility, 2),
                    'momentum': round(recent_momentum, 2),
                    'price': round(recent_price, 2),
                    'volume': int(avg_volume),
                    'source': f"Volatile {sector_name} stock"
                }
            except Exception as e:
                print(f"Error analyzing stock {symbol}: {str(e)}")
                return None
        
        # Use threads to analyze multiple stocks
        with ThreadPoolExecutor(max_workers=min(10, len(sector_stocks))) as executor:
            results = list(executor.map(analyze_stock, sector_stocks))
        
        # Filter out None results
        return [r for r in results if r is not None]
    
    except Exception as e:
        print(f"Error getting sector stocks for {sector_etf}: {str(e)}")
        return []

def get_market_movers(lookback_days):
    """
    Get market-wide high volatility stocks regardless of sector
    
    Args:
        lookback_days: Number of days to look back for analysis
        
    Returns:
        List of market movers
    """
    try:
        # For hackathon, use Yahoo Finance most active stocks as a proxy
        # In production, we would use a comprehensive scanner
        
        # Define list of frequently volatile tickers across different market segments
        potential_movers = [
            # Technology growth names
            "NVDA", "AMD", "TSLA", "PLTR", "COIN", "MSTR", "RIOT", "MARA",
            # Biotech/Pharma with event-driven volatility
            "MRNA", "BNTX", "ARNA", "SAGE", "CRSP", "EDIT", "NTLA",
            # Retail trader favorites
            "GME", "AMC", "BB", "BBBY", "KOSS", "EXPR",
            # Energy and commodities
            "BOIL", "KOLD", "USO", "XOP", "GUSH", "DRIP",
            # Volatile small caps
            "UPST", "FUBO", "NKLA", "RIDE", "WKHS", "SUNW"
        ]
        
        volatility_data = []
        
        def analyze_mover(symbol):
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=f"{lookback_days + 5}d")
                
                if len(hist) < lookback_days:
                    return None
                
                # Calculate daily returns
                hist['daily_return'] = hist['Close'].pct_change()
                
                # Calculate volatility
                volatility = hist['daily_return'].std() * np.sqrt(252) * 100
                
                # Calculate volume surge
                recent_volume = hist['Volume'].iloc[-3:].mean()
                avg_volume = hist['Volume'].iloc[:-3].mean()
                volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Only include if volatile or has volume surge
                if volatility < 30 and volume_surge < 1.5:
                    return None
                
                # Calculate recent momentum
                recent_momentum = (hist['Close'].iloc[-1] / hist['Close'].iloc[-lookback_days] - 1) * 100
                
                # Get recent price
                recent_price = hist['Close'].iloc[-1]
                
                return {
                    'symbol': symbol,
                    'sector': 'Market Mover',  # Would get actual sector in production
                    'volatility': round(volatility, 2),
                    'momentum': round(recent_momentum, 2),
                    'price': round(recent_price, 2),
                    'volume_surge': round(volume_surge, 2),
                    'volume': int(recent_volume),
                    'source': 'High Volatility Stock'
                }
            except Exception as e:
                print(f"Error analyzing mover {symbol}: {str(e)}")
                return None
        
        # Use threads to analyze multiple stocks
        with ThreadPoolExecutor(max_workers=min(10, len(potential_movers))) as executor:
            results = list(executor.map(analyze_mover, potential_movers))
        
        # Filter out None results
        return [r for r in results if r is not None]
    
    except Exception as e:
        print(f"Error getting market movers: {str(e)}")
        return []

def enrich_stock_data(stock_data):
    """
    Add options and institutional data to stock
    
    Args:
        stock_data: Dictionary containing stock data
        
    Returns:
        Enriched stock data dictionary
    """
    try:
        # Get options data
        symbol = stock_data['symbol']
        stock_data['options_data'] = get_options_data(symbol)
        
        # Add simulated institutional data
        stock_data['institutional_indicator'] = simulate_institutional_indicator(
            stock_data['volatility'], 
            stock_data['momentum'],
            stock_data.get('volume_surge', 1.0),
            stock_data['options_data']
        )
        
        # Generate strategy recommendations
        stock_data['strategies'] = recommend_strategies(stock_data)
        
        return stock_data
    except Exception as e:
        print(f"Error enriching data for {stock_data['symbol']}: {str(e)}")
        return stock_data

def get_signal(momentum, volatility, volume_ratio):
    """
    Determine trading signal based on metrics
    
    Args:
        momentum: Price momentum percentage
        volatility: Annualized volatility percentage
        volume_ratio: Ratio of recent volume to typical volume
        
    Returns:
        Signal string
    """
    signal = "neutral"
    
    if momentum > 5 and volume_ratio > 1.2:
        signal = "bullish"
    elif momentum < -5 and volume_ratio > 1.2:
        signal = "bearish"
    
    # If very high volatility, label as volatile regardless of direction
    if volatility > 35:
        signal = f"volatile_{signal}"
    
    return signal

def get_sector_stock_list(sector_etf):
    """
    Get a list of stocks that might be in this sector
    
    Args:
        sector_etf: ETF symbol representing the sector
        
    Returns:
        List of stock symbols in the sector
    """
    # For hackathon, use predefined lists
    # In production, we'd get actual ETF constituents
    
    sector_stocks = {
        'XLK': ["AAPL", "MSFT", "NVDA", "AMD", "INTC", "IBM", "ORCL", "CRM", "CSCO", "ADBE", "PYPL", "NFLX", "V", "MA", "SQ"],
        'XLF': ["JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "V", "MA", "PYPL", "BLK", "SCHW", "COF", "AIG"],
        'XLE': ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "KMI", "OXY", "MPC", "HAL", "DVN", "MRO"],
        'XLV': ["JNJ", "PFE", "MRK", "ABBV", "LLY", "AMGN", "BMY", "UNH", "CVS", "GILD", "BIIB", "REGN", "MRNA", "VRTX"],
        'XLI': ["HON", "UNP", "UPS", "CAT", "DE", "ETN", "LMT", "RTX", "BA", "GE", "MMM", "FDX", "CSX", "NOC"],
        'XLP': ["PG", "KO", "PEP", "WMT", "COST", "PM", "MO", "EL", "CL", "KMB", "KHC", "SYY", "KR", "HSY"],
        'XLY': ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "BKNG", "EBAY", "GM", "F", "BBY", "DIS"],
        'XLB': ["LIN", "APD", "SHW", "FCX", "NEM", "DOW", "DD", "ECL", "PPG", "NUE", "VMC", "MLM", "CF", "MOS"],
        'XLU': ["NEE", "DUK", "SO", "D", "AEP", "XEL", "SRE", "ED", "PEG", "EXC", "WEC", "ES", "AEE", "CMS"],
        'XLRE': ["AMT", "CCI", "PLD", "PSA", "EQIX", "O", "DLR", "SPG", "WELL", "VTR", "AVB", "EQR", "MAA", "ESS"],
        'XLC': ["META", "GOOGL", "GOOG", "NFLX", "TMUS", "VZ", "CMCSA", "T", "CHTR", "ATVI", "EA", "TTWO", "MTCH", "DISH"]
    }
    
    # Return stocks for the specific sector or a default list
    return sector_stocks.get(sector_etf, ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA", "JPM", "JNJ", "XOM"])

def get_options_data(symbol):
    """
    Get options data from Yahoo Finance
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dictionary with options data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get options expiration dates
        expirations = ticker.options
        
        if not expirations:
            return {
                'available': False,
                'message': 'No options data available'
            }
        
        # Get options for the nearest expiration
        nearest_expiry = expirations[0]
        options = ticker.option_chain(nearest_expiry)
        
        # Calculate put/call ratio
        call_volume = options.calls['volume'].sum()
        put_volume = options.puts['volume'].sum()
        put_call_ratio = put_volume / call_volume if call_volume > 0 else 0
        
        # Calculate average implied volatility
        call_iv = options.calls['impliedVolatility'].mean()
        put_iv = options.puts['impliedVolatility'].mean()
        avg_iv = (call_iv + put_iv) / 2
        
        return {
            'available': True,
            'expiration_date': nearest_expiry,
            'put_call_ratio': round(put_call_ratio, 2),
            'implied_volatility': round(avg_iv * 100, 2),  # Convert to percentage
            'total_call_volume': int(call_volume),
            'total_put_volume': int(put_volume)
        }
    except Exception as e:
        print(f"Error getting options data for {symbol}: {str(e)}")
        return {
            'available': False,
            'message': 'Error retrieving options data'
        }

def simulate_institutional_indicator(volatility, momentum, volume_surge, options_data):
    """
    Simulate institutional activity indicator
    
    Args:
        volatility: Annualized volatility percentage
        momentum: Price momentum percentage
        volume_surge: Ratio of recent volume to typical volume
        options_data: Dictionary with options data
        
    Returns:
        Dictionary with institutional indicator data
    """
    sentiment = 'neutral'
    strength = 5  # 1-10 scale
    
    # Adjust based on momentum
    if momentum > 10:
        sentiment = 'bullish'
        strength += 2
    elif momentum < -10:
        sentiment = 'bearish'
        strength += 2
    
    # Adjust based on volume surge
    if volume_surge > 2.0:
        strength += 1
    
    # Adjust based on options data if available
    if options_data['available']:
        # High put/call ratio suggests bearish sentiment
        if options_data['put_call_ratio'] > 1.5:
            sentiment = 'bearish'
            strength += 1
        # Low put/call ratio suggests bullish sentiment
        elif options_data['put_call_ratio'] < 0.5:
            sentiment = 'bullish'
            strength += 1
        
        # High implied volatility suggests stronger institutional interest
        if options_data['implied_volatility'] > 50:
            strength += 1
    
    # Cap strength at 10
    strength = min(10, strength)
    
    return {
        'sentiment': sentiment,
        'strength': strength,
        'description': f"Simulated institutional activity indicator shows {sentiment} sentiment with strength {strength}/10"
    }

def recommend_strategies(stock_data):
    """
    Generate strategy recommendations based on stock metrics
    
    Args:
        stock_data: Dictionary containing stock data
        
    Returns:
        List of strategy recommendations
    """
    strategies = []
    
    # Extract data for easier referencing
    symbol = stock_data['symbol']
    volatility = stock_data['volatility']
    momentum = stock_data['momentum']
    options_available = stock_data['options_data']['available']
    
    # High volatility strategies
    if volatility > 40:
        if options_available:
            strategies.append({
                'type': 'iron_condor',
                'description': f"Consider an iron condor options strategy for {symbol} to capitalize on high volatility",
                'risk_level': 'moderate'
            })
    
    # Momentum-based strategies
    if momentum > 10:
        if options_available:
            strategies.append({
                'type': 'bull_call_spread',
                'description': f"Consider a bull call spread for {symbol} based on positive momentum",
                'risk_level': 'moderate'
            })
        else:
            strategies.append({
                'type': 'momentum_long',
                'description': f"Consider a long position in {symbol} with trailing stop loss",
                'risk_level': 'high'
            })
    elif momentum < -10:
        if options_available:
            strategies.append({
                'type': 'bear_put_spread',
                'description': f"Consider a bear put spread for {symbol} based on negative momentum",
                'risk_level': 'moderate'
            })
    
    # Highly volatile with neutral momentum
    if volatility > 35 and abs(momentum) < 5:
        if options_available:
            strategies.append({
                'type': 'straddle',
                'description': f"Consider a straddle options strategy for {symbol} to capitalize on potential breakout",
                'risk_level': 'high'
            })
    
    # If no specific strategies identified, add a general recommendation
    if not strategies:
        strategies.append({
            'type': 'wait_and_watch',
            'description': f"Monitor {symbol} for clearer signals before taking a position",
            'risk_level': 'low'
        })
    
    return strategies
