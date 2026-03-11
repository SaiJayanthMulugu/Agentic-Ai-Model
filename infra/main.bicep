@description('Main Bicep template for MAS platform infrastructure')

param location string = resourceGroup().location
param environment string = 'dev'
param masPlatformName string = 'mas-platform'

// Key Vault
module keyVault 'keyvault.bicep' = {
  name: 'keyVault'
  params: {
    location: location
    environment: environment
    masPlatformName: masPlatformName
  }
}

// Storage Account
module storage 'storage.bicep' = {
  name: 'storage'
  params: {
    location: location
    environment: environment
    masPlatformName: masPlatformName
  }
}

// Databricks Workspace
module databricks 'databricks.bicep' = {
  name: 'databricks'
  params: {
    location: location
    environment: environment
    masPlatformName: masPlatformName
  }
}

output keyVaultName string = keyVault.outputs.keyVaultName
output storageAccountName string = storage.outputs.storageAccountName
output databricksWorkspaceUrl string = databricks.outputs.workspaceUrl

