# Customer Service Agent Example

This example demonstrates how to build a customer service agent using the GCP AI Agent Framework. The agent handles common customer inquiries like order status, returns, and product information.

## Features

- Greeting and welcome messages with quick reply buttons
- Order status lookup by order ID
- Return request handling
- Product information lookup
- Human agent escalation
- Fallback handling for unrecognized queries

## Architecture

This example uses the following components:

- **DialogFlow**: For natural language understanding and conversation flow
- **Cloud Functions**: For webhook fulfillment
- **GCP AI Agent Framework**: For structuring the application and handling intents

The agent is structured as follows:

```
┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │
│  DialogFlow       │◄───►│  Cloud Function   │
│  Conversational   │     │  Webhook          │
│  Agent            │     │                   │
└───────────────────┘     └────────┬──────────┘
                                   │
                                   ▼
                          ┌───────────────────┐
                          │                   │
                          │  Intent Handlers  │
                          │  (Framework)      │
                          │                   │
                          └───────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account
- Installed dependencies:
  ```
  pip install -r requirements.txt
  ```

### Local Testing

To test the agent locally:

1. Run the provided main.py script:
   ```
   python main.py
   ```

2. This starts a local webhook server at http://localhost:8080/webhook

3. Use a tool like [ngrok](https://ngrok.com/) to expose your local server:
   ```
   ngrok http 8080
   ```

4. Use the provided ngrok URL in your DialogFlow agent's fulfillment settings.

### Deployment to Google Cloud

To deploy to Google Cloud Functions:

1. Set up your Google Cloud project:
   ```
   gcloud config set project your-project-id
   ```

2. Deploy the cloud function:
   ```
   gcloud functions deploy customer_service_webhook \
       --runtime python39 \
       --trigger-http \
       --allow-unauthenticated
   ```

3. Use the provided function URL in your DialogFlow agent's fulfillment settings.

## DialogFlow Agent Setup

This example requires a DialogFlow agent with the following intents:

- **greeting**: Welcome and introduction
- **order_status**: Check status of an order (parameter: order_id)
- **return_item**: Start a return process (parameter: order_id)
- **product_info**: Get information about a product (parameter: product)
- **human_agent**: Request to speak with a human agent
- **fallback**: Default fallback intent

You can import the provided `dialogflow_agent.zip` into DialogFlow Console to set up the agent automatically.

## Example Conversations

### Order Status Check
```
User: I want to check my order status
Agent: I'd be happy to check the status of your order. Could you please provide your order number?
User: 12345
Agent: I found your order #12345. It's currently in transit and should arrive by Friday. Would you like to receive tracking information?
```

### Return Request
```
User: I need to return an item
Agent: I can help you with a return. Could you please provide the order number for the item you want to return?
User: 67890
Agent: I found your order #67890. You can return items from this order within 30 days of delivery. Would you like me to start the return process or explain our return policy?
```

## Extending the Example

You can extend this example by:

1. Adding more intent handlers for additional customer service scenarios
2. Integrating with real backend systems for order lookup and product information
3. Adding authentication for secure order access
4. Implementing multi-turn conversations for complex scenarios
5. Adding analytics to track user satisfaction and agent performance

## License

This example is provided as part of the GCP AI Agent Framework and is available under the same license terms.
