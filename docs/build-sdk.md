# Dev golang SDK build

This document explains how to generate SDK version

## GoLang

1. Clone `azure-rest-api-spec` and azure-sdk-for-go git repositories

   ```
   git clone https://github.com/Azure/azure-rest-api-specs
   git clone https://github.com/Azure/azure-sdk-for-go
   ```

1. Run code generation

    ```
    podman run --privileged -it -v $GOPATH:/go --entrypoint autorest \
    azuresdk/autorest /go/src/github.com/Azure/azure-rest-api-specs-pr/specification/redhatopenshift/resource-manager/readme.md \
    --go --go-sdk-folder=/go/src/github.com/Azure/azure-sdk-for-go/ --multiapi \
    --use=@microsoft.azure/autorest.go@~2.1.137 --use-onever --verbose
    ```

1. Go SDK will be generate inside `azure-sdk-for-go` project

## Useful links

* https://github.com/Azure/adx-documentation-pr/wiki/SDK-generation

* https://github.com/Azure/adx-documentation-pr
