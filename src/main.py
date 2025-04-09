import functions_framework
from flask import jsonify, Request

# Import agent_api module for the handler implementations
import agent_api

@functions_framework.http
def portfolio_manager_api(request):
    """
    Main entry point for the Portfolio Manager API.
    Routes requests to the appropriate handler based on the path.
    """
    # Get the path from the request
    path = request.path.strip('/')
    
    # Route to the appropriate handler based on path
    if path == 'volatility_opportunities':
        return agent_api.volatility_opportunities(request)
    elif path == 'sector_analysis':
        return agent_api.sector_analysis(request)
    elif path == 'analyze_symbol':
        return agent_api.handle_analyze_symbol(request)
    elif path == 'portfolio_analyzer':
        return agent_api.portfolio_analyzer(request)
    elif path == 'generate_investment_strategy':
        return agent_api.generate_investment_strategy(request)
    elif path == 'execute_portfolio_action':
        return agent_api.execute_portfolio_action(request)
    elif path == 'educational_content':
        return agent_api.educational_content(request)
    else:
        # Default response for root path or unknown paths
        return jsonify({
            'name': 'AI Portfolio Manager API',
            'version': '1.0.0',
            'endpoints': [
                '/volatility_opportunities',
                '/sector_analysis',
                '/analyze_symbol',
                '/portfolio_analyzer',
                '/generate_investment_strategy',
                '/execute_portfolio_action',
                '/educational_content'
            ]
        })
