# Deployment track — deploy ADK agents to Google Cloud

Hands-on: deploy `weather_agent/` to **Vertex AI Agent Engine**.

See the main [README](../README.md#deployment-deployment) for:

- Agent Engine vs Cloud Run comparison
- Deploy commands
- Local vs cloud session persistence

## Quick deploy (Agent Engine)

```bash
pip install 'google-cloud-aiplatform[adk,agent_engines]>=1.111'

cp deployment/weather_agent/.env.example deployment/weather_agent/.env
# Edit .env — GOOGLE_CLOUD_PROJECT, GOOGLE_API_KEY

export GOOGLE_CLOUD_PROJECT=your-project-id
export BUCKET_NAME=adk-staging-$(date +%s)
gsutil mb -p $GOOGLE_CLOUD_PROJECT -l us-central1 gs://$BUCKET_NAME

adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  --staging_bucket=gs://$BUCKET_NAME \
  --display_name="Weather Agent" \
  deployment/weather_agent
```

Save the resource name from the output, then test:

```bash
# Add to .env: REASONING_ENGINE_RESOURCE=projects/.../reasoningEngines/...
python deployment/weather_agent/test_deployed_agent.py
```

## Cloud Run (alternative)

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  --service_name=weather-agent \
  --with_ui \
  deployment/weather_agent
```
