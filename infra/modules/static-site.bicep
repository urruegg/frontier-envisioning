// Azure Static Web App for the showcase, with the sign-in client settings as app settings.
@description('Name of the static web app')
param name string

@description('Region of the static web app')
param location string

@allowed([
  'Free'
  'Standard'
])
param skuName string = 'Standard'

param tags object = {}

@description('Client id of the sign-in app registration; empty leaves the app settings out')
param authClientId string = ''

@secure()
param authClientSecret string = ''

resource site 'Microsoft.Web/staticSites@2025-03-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuName
  }
  properties: {
    provider: 'Custom'
    stagingEnvironmentPolicy: 'Disabled'
    allowConfigFileUpdates: true
  }
}

// Read by staticwebapp.config.json (clientIdSettingName / clientSecretSettingName)
resource appSettings 'Microsoft.Web/staticSites/config@2025-03-01' = if (!empty(authClientId)) {
  parent: site
  name: 'appsettings'
  properties: {
    AAD_CLIENT_ID: authClientId
    AAD_CLIENT_SECRET: authClientSecret
  }
}

output name string = site.name
output url string = 'https://${site.properties.defaultHostname}'
