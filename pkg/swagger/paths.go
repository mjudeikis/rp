package swagger

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
)

// populateParameters populates a parameters block.  Always expect an
// subscriptionId and apiVersion; the rest is dependent on specificity:
// n==0 list across provider
// n==1 list across subscription
// n==2 list across resource group
// n==3 action on resource not expecting input payload
// n==4 action on resource expecting input payload
func populateParameters(n int, typ, friendlyName string) (s []interface{}) {
	s = []interface{}{
		Reference{
			Ref: "#/parameters/ApiVersionParameter",
		},
	}

	if n > 0 {
		s = append(s, Reference{
			Ref: "#/parameters/SubscriptionIdParameter",
		})
	}

	if n > 1 {
		s = append(s, Parameter{
			Name:        "resourceGroupName",
			In:          "path",
			Description: "The name of the resource group.",
			Required:    true,
			Type:        "string",
		})
	}

	if n > 2 {
		s = append(s, Parameter{
			Name:        "resourceName",
			In:          "path",
			Description: "The name of the " + friendlyName + " resource.",
			Required:    true,
			Type:        "string",
		})
	}

	if n > 3 {
		s = append(s, Parameter{
			Name:        "parameters",
			In:          "body",
			Description: "The " + friendlyName + " resource.",
			Required:    true,
			Schema: &Schema{
				Ref: "#/definitions/" + typ,
			},
		})
	}

	return
}

// populateResponses populates a responses block.  Always include the default
// error response.
func populateResponses(typ string, isDelete bool, statusCodes ...int) (responses map[string]interface{}) {
	responses = map[string]interface{}{
		"default": Response{
			Description: "Error response describing why the operation failed.  If the resource doesn't exist, 404 (Not Found) is returned.  If any of the input parameters is wrong, 400 (Bad Request) is returned.",
			Schema: &Schema{
				Ref: "#/definitions/CloudError",
			},
		},
	}

	for _, statusCode := range statusCodes {
		r := Response{
			Description: http.StatusText(statusCode),
		}
		if !isDelete {
			switch statusCode {
			case http.StatusOK, http.StatusCreated:
				r.Schema = &Schema{
					Ref: "#/definitions/" + typ,
				}
			}
		}
		responses[strconv.FormatInt(int64(statusCode), 10)] = r
	}

	return
}

// populateExamples populates a examples block.
// It will not validate if example file exist
func populateExamples(operationID, summary string) (example map[string]map[string]string) {
	exampleFile := fmt.Sprintf("./examples/%s.json", operationID)
	example = map[string]map[string]string{
		summary: map[string]string{
			"$ref": exampleFile,
		},
	}

	return example
}

// populateTopLevelPaths populates the paths for a top level ARM resource
func populateTopLevelPaths(resourceProviderNamespace, resourceType, friendlyName string) (ps Paths) {
	ps = Paths{}

	// GET - List in subscription
	pathItem := &PathItem{
		Get: &Operation{
			Tags:        []string{strings.Title(resourceType) + "s"},
			Summary:     "Lists " + friendlyName + "s in the specified subscription.",
			Description: "Lists " + friendlyName + "s in the specified subscription.  The operation returns properties of each " + friendlyName + ".",
			OperationID: strings.Title(resourceType) + "s_List",
			Parameters:  populateParameters(1, strings.Title(resourceType), friendlyName),
			Responses:   populateResponses(strings.Title(resourceType)+"List", false, http.StatusOK),
		},
	}
	pathItem.Get.Examples = populateExamples(pathItem.Get.OperationID, pathItem.Get.Summary)
	ps["/subscriptions/{subscriptionId}/providers/"+resourceProviderNamespace+"/"+resourceType+"s"] = pathItem

	// GET - List in subscription and resourcegroup
	pathItem = &PathItem{
		Get: &Operation{
			Tags:        []string{strings.Title(resourceType) + "s"},
			Summary:     "Lists " + friendlyName + "s in the specified subscription and resource group.",
			Description: "Lists " + friendlyName + "s in the specified subscription and resource group.  The operation returns properties of each " + friendlyName + ".",
			OperationID: strings.Title(resourceType) + "s_ListByResourceGroup",
			Parameters:  populateParameters(2, strings.Title(resourceType), friendlyName),
			Responses:   populateResponses(strings.Title(resourceType)+"List", false, http.StatusOK),
		},
	}
	pathItem.Get.Examples = populateExamples(pathItem.Get.OperationID, pathItem.Get.Summary)
	ps["/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/"+resourceProviderNamespace+"/"+resourceType+"s"] = pathItem

	// All operations within subscription, resourceGroup, name
	pathItem = &PathItem{
		Get: &Operation{
			Tags:        []string{strings.Title(resourceType) + "s"},
			Summary:     "Gets a " + friendlyName + " with the specified subscription, resource group and resource name.",
			Description: "Gets a " + friendlyName + " with the specified subscription, resource group and resource name.  The operation returns properties of a " + friendlyName + ".",
			OperationID: strings.Title(resourceType) + "s_Get",
			Parameters:  populateParameters(3, strings.Title(resourceType), friendlyName),
			Responses:   populateResponses(strings.Title(resourceType), false, http.StatusOK),
		},
		Put: &Operation{
			Tags:                 []string{strings.Title(resourceType) + "s"},
			Summary:              "Creates or updates a " + friendlyName + " with the specified subscription, resource group and resource name.",
			Description:          "Creates or updates a " + friendlyName + " with the specified subscription, resource group and resource name.  The operation returns properties of a " + friendlyName + ".",
			OperationID:          strings.Title(resourceType) + "s_Create",
			Parameters:           populateParameters(4, strings.Title(resourceType), friendlyName),
			Responses:            populateResponses(strings.Title(resourceType), false, http.StatusOK, http.StatusCreated),
			LongRunningOperation: true,
		},
		Delete: &Operation{
			Tags:                 []string{strings.Title(resourceType) + "s"},
			Summary:              "Deletes a " + friendlyName + " with the specified subscription, resource group and resource name.",
			Description:          "Deletes a " + friendlyName + " with the specified subscription, resource group and resource name.  The operation returns nothing.",
			OperationID:          strings.Title(resourceType) + "s_Delete",
			Parameters:           populateParameters(3, strings.Title(resourceType), friendlyName),
			Responses:            populateResponses(strings.Title(resourceType), true, http.StatusOK, http.StatusNoContent),
			LongRunningOperation: true,
		},
		Patch: &Operation{
			Tags:                 []string{strings.Title(resourceType) + "s"},
			Summary:              "Creates or updates a " + friendlyName + " with the specified subscription, resource group and resource name.",
			Description:          "Creates or updates a " + friendlyName + " with the specified subscription, resource group and resource name.  The operation returns properties of a " + friendlyName + ".",
			OperationID:          strings.Title(resourceType) + "s_Update",
			Parameters:           populateParameters(4, strings.Title(resourceType), friendlyName),
			Responses:            populateResponses(strings.Title(resourceType), false, http.StatusOK, http.StatusCreated),
			LongRunningOperation: true,
		},
	}

	pathItem.Get.Examples = populateExamples(pathItem.Get.OperationID, pathItem.Get.Summary)
	pathItem.Put.Examples = populateExamples(pathItem.Put.OperationID, pathItem.Put.Summary)
	pathItem.Delete.Examples = populateExamples(pathItem.Delete.OperationID, pathItem.Delete.Summary)
	pathItem.Patch.Examples = populateExamples(pathItem.Patch.OperationID, pathItem.Patch.Summary)
	ps["/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/"+resourceProviderNamespace+"/"+resourceType+"s/{resourceName}"] = pathItem

	return
}
