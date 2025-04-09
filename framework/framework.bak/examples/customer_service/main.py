"""
Customer Service Agent Example

This example demonstrates how to build a customer service agent using the GCP AI Agent Framework.
The agent handles common customer inquiries like order status, returns, and product information.

To run this example:
1. Install the framework and dependencies
2. Deploy the agent to Google Cloud Functions
3. Set up a DialogFlow agent with the appropriate intents
4. Configure the DialogFlow agent to use the deployed webhook

For detailed instructions, see the README.md file.
"""

import functions_framework
from flask import jsonify

# Import the framework components
from framework.core import WebhookHandler, Intent, IntentHandler, AgentRequest, AgentResponse
from framework.tools import create_card_response, create_suggestion_chips

# Create a webhook handler
webhook = WebhookHandler("customer_service")


# Define intent handlers
class GreetingHandler(IntentHandler):
    """Handles greeting intents."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle greeting intent."""
        return AgentResponse(
            fulfillment_text="Hello! I'm your customer service assistant. How can I help you today?",
            payload={
                "richContent": [[{
                    "type": "chips",
                    "options": [
                        {"text": "Check order status"},
                        {"text": "Return an item"},
                        {"text": "Product information"},
                        {"text": "Speak to a human"}
                    ]
                }]]
            }
        )


class OrderStatusHandler(IntentHandler):
    """Handles order status inquiries."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle order status intent."""
        # Extract order ID parameter
        order_id = self.extract_parameter(request.parameters, 'order_id', required=False)
        
        if not order_id:
            # No order ID provided, ask for it
            return AgentResponse(
                fulfillment_text="I'd be happy to check the status of your order. Could you please provide your order number?",
                output_contexts=[
                    webhook.agent.create_context(request.session_id, "awaiting_order_id", 5)
                ]
            )
        
        # In a real implementation, we would call an order API here
        # For this example, we'll just return a mock response
        return AgentResponse(
            fulfillment_text=f"I found your order #{order_id}. It's currently in transit and should arrive by Friday. Would you like to receive tracking information?",
            payload={
                "richContent": [[
                    {
                        "type": "info",
                        "title": f"Order #{order_id}",
                        "subtitle": "In Transit - Arriving Friday",
                        "text": "Your order was shipped on Monday via UPS Ground. It's currently in transit and expected to arrive by Friday."
                    },
                    {
                        "type": "chips",
                        "options": [
                            {"text": "Send tracking info"},
                            {"text": "No thanks"}
                        ]
                    }
                ]]
            }
        )


class ReturnItemHandler(IntentHandler):
    """Handles item return requests."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle return item intent."""
        # Extract order ID parameter
        order_id = self.extract_parameter(request.parameters, 'order_id', required=False)
        
        if not order_id:
            # No order ID provided, ask for it
            return AgentResponse(
                fulfillment_text="I can help you with a return. Could you please provide the order number for the item you want to return?",
                output_contexts=[
                    webhook.agent.create_context(request.session_id, "awaiting_return_order_id", 5)
                ]
            )
        
        # In a real implementation, we would validate the order ID and get order details
        return AgentResponse(
            fulfillment_text=f"I found your order #{order_id}. You can return items from this order within 30 days of delivery. Would you like me to start the return process or explain our return policy?",
            payload={
                "richContent": [[
                    {
                        "type": "info",
                        "title": "Return Options",
                        "text": "You can return items for a full refund within 30 days of delivery, or store credit within 60 days."
                    },
                    {
                        "type": "chips",
                        "options": [
                            {"text": "Start return process"},
                            {"text": "Explain return policy"},
                            {"text": "I changed my mind"}
                        ]
                    }
                ]]
            }
        )


class ProductInfoHandler(IntentHandler):
    """Handles product information inquiries."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle product information intent."""
        # Extract product parameter
        product = self.extract_parameter(request.parameters, 'product', required=False)
        
        if not product:
            # No product provided, ask for it
            return AgentResponse(
                fulfillment_text="I'd be happy to provide product information. What product are you interested in?",
                output_contexts=[
                    webhook.agent.create_context(request.session_id, "awaiting_product", 5)
                ]
            )
        
        # In a real implementation, we would query a product database
        # For this example, we'll just return mock information
        return AgentResponse(
            fulfillment_text=f"Here's information about our {product}. It comes in 3 colors and is currently on sale for $49.99. Would you like to see more details or add it to your cart?",
            payload={
                "richContent": [[
                    {
                        "type": "image",
                        "rawUrl": "https://example.com/images/placeholder.jpg",
                        "accessibilityText": f"Image of {product}"
                    },
                    {
                        "type": "info",
                        "title": product.title(),
                        "subtitle": "$49.99 (10% off)",
                        "text": "Available in Red, Blue, and Black. Free shipping on orders over $35."
                    },
                    {
                        "type": "chips",
                        "options": [
                            {"text": "View details"},
                            {"text": "Add to cart"},
                            {"text": "Check availability"}
                        ]
                    }
                ]]
            }
        )


class HumanAgentHandler(IntentHandler):
    """Handles requests to speak to a human agent."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle human agent request intent."""
        return AgentResponse(
            fulfillment_text="I understand that you'd like to speak with a human agent. I'm connecting you now. An agent will be with you shortly. In the meantime, could you please specify what your issue is about?",
            payload={
                "richContent": [[
                    {
                        "type": "info",
                        "title": "Connecting to Human Agent",
                        "subtitle": "Estimated wait time: 2-3 minutes",
                        "text": "Please select a topic to help us route your request to the right department."
                    },
                    {
                        "type": "chips",
                        "options": [
                            {"text": "Billing Question"},
                            {"text": "Technical Support"},
                            {"text": "Order Issue"},
                            {"text": "Other"}
                        ]
                    }
                ]]
            }
        )


class FallbackHandler(IntentHandler):
    """Handles fallback intent when no other intent matches."""
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle fallback intent."""
        return AgentResponse(
            fulfillment_text="I'm sorry, I didn't understand that. How can I help you today?",
            payload={
                "richContent": [[
                    {
                        "type": "chips",
                        "options": [
                            {"text": "Check order status"},
                            {"text": "Return an item"},
                            {"text": "Product information"},
                            {"text": "Speak to a human"}
                        ]
                    }
                ]]
            }
        )


# Register intent handlers
webhook.register_handler(GreetingHandler("greeting"))
webhook.register_handler(OrderStatusHandler("order_status"))
webhook.register_handler(ReturnItemHandler("return_item"))
webhook.register_handler(ProductInfoHandler("product_info"))
webhook.register_handler(HumanAgentHandler("human_agent"))
webhook.register_handler(FallbackHandler("fallback"))


# Cloud Function entry point
@functions_framework.http
def customer_service_webhook(request):
    """
    Cloud Function entry point for the customer service webhook.
    
    Args:
        request: Flask request object
        
    Returns:
        Response for DialogFlow
    """
    return webhook.handle_request(request)


# For local testing
if __name__ == "__main__":
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route('/webhook', methods=['POST'])
    def webhook_endpoint():
        return customer_service_webhook(request)
    
    print("Starting local webhook server at http://localhost:8080/webhook")
    app.run(host='0.0.0.0', port=8080)
