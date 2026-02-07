@description('Azure Key Vault deployment')

param location string
param environment string
param masPlatformName string

var keyVaultName = '${masPlatformName}-kv-${environment}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enableRbacAuthorization: true
  }
}

output keyVaultName string = keyVault.name

