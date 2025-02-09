package database

import (
	"context"
	"crypto/tls"
	"net/http"
	"time"

	uuid "github.com/satori/go.uuid"
	"github.com/ugorji/go/codec"

	"github.com/jim-minter/rp/pkg/api"
	"github.com/jim-minter/rp/pkg/database/cosmosdb"
	"github.com/jim-minter/rp/pkg/env"
)

// Database represents a database
type Database struct {
	OpenShiftClusters OpenShiftClusters
	Subscriptions     Subscriptions
}

// NewDatabase returns a new Database
func NewDatabase(ctx context.Context, env env.Interface, uuid uuid.UUID, dbid string) (db *Database, err error) {
	databaseAccount, masterKey := env.CosmosDB(ctx)

	h := &codec.JsonHandle{
		BasicHandle: codec.BasicHandle{
			DecodeOptions: codec.DecodeOptions{
				ErrorIfNoField: true,
			},
		},
	}

	err = api.AddExtensions(&h.BasicHandle)
	if err != nil {
		return nil, err
	}

	c := &http.Client{
		Transport: &http.Transport{
			// disable HTTP/2 for now: https://github.com/golang/go/issues/36026
			TLSNextProto: map[string]func(string, *tls.Conn) http.RoundTripper{},
		},
		Timeout: 30 * time.Second,
	}

	dbc, err := cosmosdb.NewDatabaseClient(c, h, databaseAccount, masterKey)
	if err != nil {
		return nil, err
	}

	db = &Database{}

	db.OpenShiftClusters, err = NewOpenShiftClusters(ctx, uuid, dbc, dbid, "OpenShiftClusters")
	if err != nil {
		return nil, err
	}

	db.Subscriptions, err = NewSubscriptions(ctx, uuid, dbc, dbid, "Subscriptions")
	if err != nil {
		return nil, err
	}

	return db, nil
}
