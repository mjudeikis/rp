# Azure Red Hat OpenShift azure-cli extension

## Install extension

From `aro-rp` repository:
```
make setup-cli
```

Using `azdev` tooling manually:
```
azdev extension repo add $GOPATH/src/github.com/jim-minter/rp
azdev extension add aro-preview
```

`azdev` tool only works when cli code is in root directory. It has behefits like
hotreload, linting, testing. If you doing major changes we recommend creating `azdev`
development setup, instead of local `aro-rp` one.

## Development RP

To run CLI commands for dev CLI you will need to set env `BASE_URL`
to `export BASE_URL=https://localhost:8443/`.

Disable ssl check for CLI:
`export AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1`

Manually register subscription to fakeRP. In production this will be done via
`ARM` endpoint.

```
curl -k -X PUT "https://localhost:8443/subscriptions/$AZURE_SUBSCRIPTION_ID?api-version=2.0" -H 'Content-Type: application/json' -d '{"state": "Registered", "properties": {"tenantId": "'"$AZURE_TENANT_ID"'"}}'
```

## Examples

Create a cluster when CLI created RH and VNET:
```
az aro create --resource-group resourcegroup -n clustername --location=eastus --client-id=$AZURE_CLIENT_ID --client-secret=$AZURE_CLIENT_SECRET
```

Create a cluster with BYO vnet rg:
```
az aro create --resource-group resourcegroup --vnet-resource-group-name clustername-vnet -n clustername-test --loc
ation=eastus --client-id=$AZURE_CLUSTER_CLIENT_ID --client-secret=$AZURE_CLUSTER_CLIENT_SECRET
```

List all clusters:
```
az aro list
```

Get cluster credentials:
```
az aro get-credentials -n clustername -g resourcegroup
```

Get single cluster:
```
az aro get -n clustername -g resourcegroup
```

Delete a cluster:
```
az aro delete -n clustername -g resourcegroup
```


## Vendoring new SDK

When vendoring dev version of aro cli, extend `AzureRedHatOpenShiftClientConfiguration`:
```
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if os.environ.get('BASE_URL') != "":
             base_url = os.environ.get('BASE_URL')
        if not base_url:
            base_url = 'https://management.azure.com'
```
