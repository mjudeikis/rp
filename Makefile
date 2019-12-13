COMMIT = $(shell git rev-parse --short HEAD)$(shell [[ $$(git status --porcelain) = "" ]] || echo -dirty)

rp: generate
	go build -ldflags "-X main.gitCommit=$(COMMIT)" ./cmd/rp

clean:
	rm -f rp

client: generate
	rm -rf azure-python-sdk pkg/client
	mkdir azure-python-sdk pkg/client
	sha256sum swagger/redhatopenshift/resource-manager/Microsoft.RedHatOpenShift/preview/2019-12-31-preview/redhatopenshift.json >.sha256sum

	sudo docker run \
		-v $(PWD)/pkg/client:/github.com/jim-minter/rp/pkg/client \
		-v $(PWD)/swagger:/swagger \
		azuresdk/autorest \
		--go \
		--namespace=redhatopenshift \
		--input-file=/swagger/redhatopenshift/resource-manager/Microsoft.RedHatOpenShift/preview/2019-12-31-preview/redhatopenshift.json \
		--output-folder=/github.com/jim-minter/rp/pkg/client/services/preview/redhatopenshift/mgmt/2019-12-31-preview/redhatopenshift

	sudo docker run \
		-v $(PWD)/azure-python-sdk:/azure-python-sdk \
		-v $(PWD)/swagger:/swagger \
		azuresdk/autorest \
		--use=@microsoft.azure/autorest.python@4.0.70 \
		--python \
		--azure-arm \
		--input-file=/swagger/redhatopenshift/resource-manager/Microsoft.RedHatOpenShift/preview/2019-12-31-preview/redhatopenshift.json \
		--output-folder=/azure-python-sdk/2019-12-31-preview

	sudo chown -R $(USER):$(USER) azure-python-sdk pkg/client

	go run ./vendor/golang.org/x/tools/cmd/goimports -w -local=github.com/jim-minter/rp pkg/client

generate:
	go generate ./...

image: rp
	docker build -t arosvc.azurecr.io/rp:$(COMMIT) .

secrets:
	rm -rf secrets
	mkdir secrets
	oc extract -n azure secret/aro-v4-dev --to=secrets

secrets-update:
	oc create secret generic aro-v4-dev --from-file=secrets --dry-run -o yaml | oc apply -f -

test: generate
	go build ./...

	gofmt -s -w cmd hack pkg
	go run ./vendor/golang.org/x/tools/cmd/goimports -w -local=github.com/jim-minter/rp cmd hack pkg
	go run ./hack/validate-imports/validate-imports.go cmd hack pkg
	@[ -z "$$(ls pkg/util/*.go 2>/dev/null)" ] || (echo error: go files are not allowed in pkg/util, use a subpackage; exit 1)
	@[ -z "$$(find -name "*:*")" ] || (echo error: filenames with colons are not allowed on Windows, please rename; exit 1)
	@sha256sum --quiet -c .sha256sum || (echo error: client library is stale, please run make client; exit 1)

	go vet ./...
	go test ./...

setup-py-env:
	python3 -m venv pyenv && source pyenv/bin/activate && pip install azdev

setup-cli:
	@[ -f "pyenv/bin/activate" ] || (echo error: python env is not found. Run "make setup-py-env"; exit 1)
	@[ ! -z "${BASE_URL}" ] || (echo info: BASE_URL is not set. Will use global ARM endpoint)
	( \
       source pyenv/bin/activate; \
	   cd az-cli/src/aro-preview/ && python ./setup.py bdist_wheel ; \
	   az extension remove -n aro-preview ; \
	   az extension add --source $$(echo dist/*) -y ; \
    )

.PHONY: rp clean client generate image secrets secrets-update setup-cli setup-py-env test
