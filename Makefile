rp:
	go build -ldflags "-X main.gitCommit=$(shell git rev-parse --short HEAD)$(shell [[ $$(git status --porcelain) = "" ]] || echo -dirty)" ./cmd/rp

clean:
	rm -f rp

generate:
	go generate ./...

image:
	go get github.com/openshift/imagebuilder/cmd/imagebuilder
	imagebuilder -f Dockerfile -t rp:latest .

test: generate
	go test ./...

generate-sdk:
	# Due to orering https://github.com/Azure/autorest.go/blob/3f9bdd60fd7a7c8740bbe3ec986f583f7ffa5fbd/src/Model/CodeModelGo.cs#L120-L141
	# package FQDN are either hardcoded to azure sdk or set wrong. For this we do
	# replace in the end
	podman run --privileged --workdir=/go/src -it -v $(GOPATH):/go --entrypoint autorest \
    azuresdk/autorest ./github.com/jim-minter/rp/rest-api-spec/redhatopenshift/resource-manager/readme.md \
    --go --go-sdks-folder=./github.com/jim-minter/rp/pkg/sdk --multiapi \
    --use=@microsoft.azure/autorest.go@~2.1.137 --use-onever --verbose
	# HACK to align pkg imports when running in non default repository
	find . -type f -name "*.go" -exec sed -i 's/go\/src\/github.com/github.com/g' {} +


.PHONY: clean generate generate-sdk image rp test

