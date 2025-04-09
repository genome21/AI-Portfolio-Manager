"""
Framework Usage Examples

This module provides examples of how to use the AI Agent Framework for building
agents that can be integrated with Google's Agent Builder and DialogFlow.
"""

import functions_framework
from flask import jsonify, Request
import logging

from .agent_api import AgentAPI, validate_parameters, create_error_response, create_success_response
from .mock_data import (
    generate_stock_data, 
    generate_sector_data, 
    generate_portfolio_data,
    generate_investment_strategy,
    generate_market_analysis,
    generate_educational_content
)


def create_portfolio_manager_api():
    """
    Create an example Portfolio Manager API based on the AI Portfolio Manager example.
    
    Returns:
        AgentAPI instance configured with portfolio management handlers
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create the API
    api = AgentAPI("portfolio_manager")
    
    # Define handler for volatility opportunities
    def volatility_opportunities(request: Request):
        """
        Get current volatility opportunities.
        """
        try:
            # Get the latest market analysis with mock data
            analysis = generate_market_analysis()
            
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
            return create_error_response(f"Error retrieving volatility opportunities: {str(e)}", 500)
    
    # Define handler for sector analysis
    def sector_analysis(request: Request):
        """
        Get sector analysis.
        """
        try:
            # Generate mock market analysis
            analysis = generate_market_analysis()
            
            # Extract just the sector data
            sector_data = analysis.get('market_overview', {}).get('volatile_sectors', [])
            
            # Generate sector insights
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
            
            # Return sector analysis
            return jsonify({
                'sector_analysis': {
                    'timestamp': analysis.get('analysis_date'),
                    'sectors': sector_data,
                    'insights': insights
                }
            })
        
        except Exception as e:
            return create_error_response(f"Error retrieving sector analysis: {str(e)}", 500)
    
    # Define handler for analyzing a symbol
    def analyze_symbol(request: Request):
        """
        Analyze a specific stock symbol.
        """
        # Get the request JSON or query params
        symbol = None
        
        if request.method == 'GET':
            symbol = request.args.get('symbol')
        elif request.is_json:
            request_data = request.get_json()
            symbol = request_data.get('symbol')
        
        if not symbol:
            return create_error_response("Missing symbol parameter", 400)
        
        # Convert to uppercase
        symbol = symbol.upper()
        
        try:
            # Generate mock stock data
            stock_data = generate_stock_data(symbol)
            return jsonify(stock_data)
        
        except Exception as e:
            return create_error_response(f"Error analyzing symbol {symbol}: {str(e)}", 500)
    
    # Define handler for portfolio analysis
    def portfolio_analyzer(request: Request):
        """
        Analyze an investment portfolio.
        """
        # Check if request is JSON
        if not request.is_json:
            return create_error_response("Request must be JSON", 400)
        
        try:
            request_data = request.get_json()
            
            # Check if request contains needed parameters
            if 'holdings' not in request_data:
                return create_error_response("Missing holdings parameter", 400)
            
            holdings = request_data['holdings']
            risk_profile = request_data.get('risk_profile', 'moderate')
            
            # For demo purposes, if no holdings are provided, generate mock data
            if len(holdings) == 0:
                holdings = generate_portfolio_data(10)
            
            # Calculate portfolio metrics
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
            
            # Return analysis results
            return jsonify({
                'portfolio_value': total_value,
                'asset_allocation': asset_allocation,
                'risk_metrics': risk_metrics,
                'diversification': diversification,
                'recommendations': recommendations
            })
        
        except Exception as e:
            return create_error_response(f"Portfolio analysis error: {str(e)}", 500)
    
    # Define handler for generating investment strategies
    def generate_investment_strategy(request: Request):
        """
        Generate a personalized investment strategy.
        """
        # Check that request is JSON
        if not request.is_json:
            return create_error_response("Request must be JSON", 400)
        
        request_data = request.get_json()
        
        # Validate required parameters
        if 'investor_profile' not in request_data:
            return create_error_response("Missing investor profile", 400)
        
        try:
            investor_profile = request_data['investor_profile']
            
            # Extract key investor parameters
            risk_tolerance = investor_profile.get('risk_tolerance', 'moderate')
            investment_horizon = investor_profile.get('investment_horizon', 'medium')
            investment_goals = investor_profile.get('investment_goals', [])
            
            # Generate investment strategy
            strategy = generate_investment_strategy(
                risk_tolerance, 
                investment_horizon, 
                investment_goals
            )
            
            return jsonify({
                'investment_strategy': strategy
            })
        
        except Exception as e:
            return create_error_response(f"Strategy generation error: {str(e)}", 500)
    
    # Define handler for educational content
    def educational_content(request: Request):
        """
        Retrieve educational investing content.
        """
        # Get query parameters
        topic = request.args.get('topic', '').lower()
        level = request.args.get('level', 'beginner').lower()
        
        # Generate mock educational content
        content = generate_educational_content(topic, level)
        
        return jsonify(content)
    
    # Register handlers
    api.register_handler('volatility_opportunities', volatility_opportunities)
    api.register_handler('sector_analysis', sector_analysis)
    api.register_handler('analyze_symbol', analyze_symbol)
    api.register_handler('portfolio_analyzer', portfolio_analyzer)
    api.register_handler('generate_investment_strategy', generate_investment_strategy)
    api.register_handler('educational_content', educational_content)
    
    return api


# Create a Cloud Function entry point using the example API
def create_cloud_function():
    """
    Create a Cloud Function entry point for the Portfolio Manager API.
    
    Returns:
        Cloud Function entry point function
    """
    api = create_portfolio_manager_api()
    
    @functions_framework.http
    def portfolio_manager_api(request):
        """
        Cloud Function entry point for the Portfolio Manager API.
        """
        return api.handle_request(request)
    
    return portfolio_manager_api


# For demonstration/testing
if __name__ == "__main__":
    from flask import Flask, request
    
    # Create Flask app for local testing
    app = Flask(__name__)
    
    # Create API
    api = create_portfolio_manager_api()
    
    # Define route
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def api_route(path):
        return api.handle_request(request)
    
    # Default route
    @app.route('/', methods=['GET', 'POST'])
    def default_route():
        return api.handle_request(request)
    
    # Run the app
    print("Starting API server at http://localhost:8080/")
    app.run(host='0.0.0.0', port=8080)
