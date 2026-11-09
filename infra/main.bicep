// Frontier Envisioning showcase: a resource group and an Azure Static Web App with Microsoft Entra sign-in.
// Deployed with the Azure Developer CLI (azd provision); parameters come from the azd environment.
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the azd environment; used in resource names and tags')
param environmentName string

@minLength(1)
@description('Region of the resource group')
param location string

@description('Region of the static web app (Static Web Apps is offered in a few regions)')
@allowed([
  'westeurope'
  'eastus2'
  'centralus'
  'westus2'
  'eastasia'
])
param staticWebAppLocation string = 'westeurope'

@description('Static Web Apps plan: Standard is needed for sign-in restricted to one Microsoft Entra tenant')
@allowed([
  'Free'
  'Standard'
])
param skuName string = 'Standard'

@description('Client id of the Microsoft Entra app registration used for sign-in; empty leaves the sign-in settings out')
param authClientId string = ''

@secure()
@description('Client secret of the sign-in app registration (from the azd environment, never committed)')
param authClientSecret string = ''

@description('Additional tags for every resource')
param tags object = {}

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var allTags = union(tags, {
  'azd-env-name': environmentName
  workload: 'frontier-envisioning-showcase'
})

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: allTags
}

module site 'modules/static-site.bicep' = {
  name: 'showcase-site'
  scope: rg
  params: {
    name: 'stapp-${resourceToken}'
    location: staticWebAppLocation
    skuName: skuName
    tags: union(allTags, { 'azd-service-name': 'site' })
    authClientId: authClientId
    authClientSecret: authClientSecret
  }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output SITE_NAME string = site.outputs.name
output SITE_URL string = site.outputs.url
