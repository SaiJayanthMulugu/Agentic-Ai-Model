#!/bin/bash

# Deployment script for MAS platform infrastructure

set -e

RESOURCE_GROUP="mas-platform-rg"
LOCATION="eastus"
ENVIRONMENT="dev"

echo "Deploying MAS platform infrastructure..."

# Create resource group if it doesn't exist
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters location=$LOCATION environment=$ENVIRONMENT

echo "Deployment complete!"
echo "Key Vault: $(az deployment group show --resource-group $RESOURCE_GROUP --name main --query properties.outputs.keyVaultName.value -o tsv)"
echo "Storage Account: $(az deployment group show --resource-group $RESOURCE_GROUP --name main --query properties.outputs.storageAccountName.value -o tsv)"

