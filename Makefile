
.PHONY: rp
rp:
	go build -ldflags "-X main.gitCommit=$(shell git rev-parse --short HEAD)$(shell [[ $$(git status --porcelain) = "" ]] || echo -dirty)" ./cmd/rp

.PHONY: clean
clean:
	rm -f rp

.PHONY: generate
generate:
	go generate ./...

.PHONY: image
image:
	go get github.com/openshift/imagebuilder/cmd/imagebuilder
	imagebuilder -f Dockerfile -t rp:latest .

.PHONY: test
test: generate
	go test ./...

.PHONY: secrets
secrets:
	@rm -rf secrets
	@mkdir secrets
	@oc extract -n azure secret/v4-secrets-azure --to=secrets >/dev/null
