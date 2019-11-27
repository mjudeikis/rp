package main

import (
	"bufio"
	"context"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/google/go-github/github"
	"golang.org/x/oauth2"
)

const goModFile = "go.mod"

type scraper struct {
	*github.Client
}

func main() {
	if err := run(); err != nil {
		panic(err)
	}
}

func run() error {
	ctx := context.Background()
	var cli *http.Client
	token := os.Getenv("GITHUB_TOKEN")
	cli = oauth2.NewClient(ctx, oauth2.StaticTokenSource(&oauth2.Token{AccessToken: token}))

	scrape := scraper{
		Client: github.NewClient(cli),
	}

	file, err := os.Open(goModFile)
	if err != nil {
		return err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	enterGenerated := false
	//var replaceBlock []string
	var tag string
	for scanner.Scan() {
		record := scanner.Text()
		if strings.Contains(record, "#tag") {
			args := strings.Split(record, ":")
			tag = args[(len(args) - 1)]
			fmt.Printf("tag:%s\n", tag)
			enterGenerated = true
		}

		if enterGenerated {
			if strings.HasSuffix(record, ")") {
				enterGenerated = false
			}

			// Resolve tag to gomod version
			if strings.Contains(record, "=>") {
				scrape.resolveGoModVersion(record, tag)
			}

		}
	}
	if err := scanner.Err(); err != nil {
		return err
	}
	return nil
}

func (s *scraper) resolveGoModVersion(record, tag string) (string, error) {
	fmt.Println(record)
	args := strings.Split(record, " ")
	gitRepo := args[2]
	repoShort := strings.ReplaceAll(gitRepo, "github.com/openshift/", "")
	branch, _, err := s.Repositories.GetBranch(context.Background(), "openshift", repoShort, tag)
	if err != nil {
		fmt.Println("error %s", err.Error())
		return "", err
	}
	sha := *branch.Commit.SHA
	version := fmt.Sprintf("v0.0.0-20190211120101-%s", sha[:12])

	newRecord := fmt.Sprintf("%s => %s %s", args[0], args[2], version)
	fmt.Println(newRecord)

	return "", nil

}
