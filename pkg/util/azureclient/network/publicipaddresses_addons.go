package network

import (
	"context"

	"github.com/Azure/azure-sdk-for-go/services/network/mgmt/2019-07-01/network"
)

// PublicIPAddressesClientAddons contains addons for PublicIPAddressesClient
type PublicIPAddressesClientAddons interface {
	DeleteAndWait(ctx context.Context, resourceGroupName string, publicIPAddressName string) (err error)
}

func (c *publicIPAddressesClient) DeleteAndWait(ctx context.Context, resourceGroupName string, publicIPAddressName string) error {
	future, err := c.Delete(ctx, resourceGroupName, publicIPAddressName)
	if err != nil {
		return err
	}

	return future.WaitForCompletionRef(ctx, c.PublicIPAddressesClient.Client)
}

func (c *publicIPAddressesClient) List(ctx context.Context, resourceGroupName string) (ips []network.PublicIPAddress, err error) {
	page, err := c.PublicIPAddressesClient.List(ctx, resourceGroupName)
	if err != nil {
		return nil, err
	}

	for page.NotDone() {
		ips = append(ips, page.Values()...)

		err = page.Next()
		if err != nil {
			return nil, err
		}
	}

	return ips, nil
}
