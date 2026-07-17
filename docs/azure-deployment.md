# Azure Deployment Guide

## 1. Provision resources
```bash
az group create -n finai-rg -l eastus
az acr create -n finaiacr -g finai-rg --sku Basic --admin-enabled true
az postgres flexible-server create -g finai-rg -n finai-pg --sku-name Standard_B1ms --tier Burstable
az redis create -g finai-rg -n finai-redis --sku Basic --vm-size c0
az cognitiveservices account create -n finai-openai -g finai-rg --kind OpenAI --sku S0 -l eastus
az search service create -n finai-search -g finai-rg --sku basic
```

## 2. Deploy Azure OpenAI models
In Azure AI Foundry, create deployments: `gpt-4o` (chat) and `text-embedding-3-large` (embeddings). Note the endpoint + key.

## 3. Build & push images
```bash
az acr login -n finaiacr
docker build -t finaiacr.azurecr.io/finai-backend:latest backend
docker build -t finaiacr.azurecr.io/finai-frontend:latest frontend
docker push finaiacr.azurecr.io/finai-backend:latest
docker push finaiacr.azurecr.io/finai-frontend:latest
```

## 4. App Services
```bash
az appservice plan create -g finai-rg -n finai-plan --is-linux --sku P1v3
az webapp create -g finai-rg -p finai-plan -n finai-api \
  --deployment-container-image-name finaiacr.azurecr.io/finai-backend:latest
az webapp create -g finai-rg -p finai-plan -n finai-app \
  --deployment-container-image-name finaiacr.azurecr.io/finai-frontend:latest
az webapp config appsettings set -g finai-rg -n finai-api --settings \
  DATABASE_URL="postgresql+psycopg://..." REDIS_URL="rediss://..." \
  AZURE_OPENAI_ENDPOINT="..." AZURE_OPENAI_API_KEY="..." \
  VECTOR_STORE=azure_search AZURE_SEARCH_ENDPOINT="..." AZURE_SEARCH_API_KEY="..." \
  SECRET_KEY="$(openssl rand -hex 32)" WEBSITES_PORT=8000
```
Run the Celery worker either as a second Web App with startup command
`celery -A app.services.worker.celery_app worker -l info`, or as an Azure Container App job.

## 5. CI/CD secrets (GitHub → Settings → Secrets)
`ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`, `AZURE_CREDENTIALS`
(`az ad sp create-for-rbac --sdk-auth`), `AZURE_WEBAPP_BACKEND`.

## 6. Hardening checklist
- Store secrets in Azure Key Vault, reference via App Service Key Vault references
- Enable Managed Identity for ACR pull + Key Vault access
- Front the app with Azure Front Door + WAF; force HTTPS
- Enable Application Insights (`APPLICATIONINSIGHTS_CONNECTION_STRING`)
- Configure PostgreSQL firewall to allow only App Service outbound IPs
