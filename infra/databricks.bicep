@description('Databricks workspace deployment')

param location string
param environment string
param masPlatformName string

var workspaceName = '${masPlatformName}-${environment}'

resource databricksWorkspace 'Microsoft.Databricks/workspaces@2023-02-01' = {
  name: workspaceName
  location: location
  sku: {
    name: 'premium'
  }
  properties: {
    managedResourceGroupId: resourceGroup().id
    parameters: {
      enableNoPublicIp: {
        value: false
      }
    }
  }
}

output workspaceUrl string = databricksWorkspace.properties.workspaceUrl
output workspaceId string = databricksWorkspace.id

