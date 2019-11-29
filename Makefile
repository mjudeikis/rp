rp:
	go build -ldflags "-X main.gitCommit=$(shell git rev-parse --short HEAD)$(shell [[ $$(git status --porcelain) = "" ]] || echo -dirty)" ./cmd/rp

clean:
	rm -f rp

image:
	go get github.com/openshift/imagebuilder/cmd/imagebuilder
	imagebuilder -f Dockerfile -t rp:latest .

test:
	go generate ./...
	go build ./...

	gofmt -s -w cmd hack pkg
	go run ./vendor/golang.org/x/tools/cmd/goimports -w -local=github.com/jim-minter/rp cmd hack pkg
	go run ./hack/validate-imports/validate-imports.go cmd hack pkg
	@[ -z "$$(ls pkg/util/*.go 2>/dev/null)" ] || (echo error: go files are not allowed in pkg/util, use a subpackage; exit 1)
	@[ -z "$$(find -name "*:*")" ] || (echo error: filenames with colons are not allowed on Windows, please rename; exit 1)

	go vet ./...
	go test ./...

generate-sdk:
	podman run --privileged -it -v $GOPATH:/go --entrypoint autorest \
    azuresdk/autorest /go/src/github.com/jim-minter/rp/rest-api-spec/redhatopenshift/resource-manager/readme.md \
    --go --go-sdks-folder=/go/src/github.com/jim-minter/rp/pkg/sdk/ --multiapi \
    --use=@microsoft.azure/autorest.go@~2.1.137 --use-onever --verbose

.PHONY: clean generate-sdk image rp test


