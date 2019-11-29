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
	podman run --privileged -it -v $GOPATH:/go --entrypoint autorest \
    azuresdk/autorest /go/src/github.com/jim-minter/rp/rest-api-spec/redhatopenshift/resource-manager/readme.md \
    --go --go-sdks-folder=/go/src/github.com/jim-minter/rp/pkg/sdk/ --multiapi \
    --use=@microsoft.azure/autorest.go@~2.1.137 --use-onever --verbose

.PHONY: clean generate generate-sdk image rp test


