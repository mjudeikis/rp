package swagger

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestValidateVersion(t *testing.T) {
	tests := []struct {
		name      string
		expectErr error
		input     string
	}{
		{
			name:      "corrent preview version",
			expectErr: nil,
			input:     "2019-02-11-preview",
		},
		{
			name:      "correct ga version",
			expectErr: nil,
			input:     "2019-02-11",
		},
		{
			name:      "wrong short version",
			expectErr: fmt.Errorf("wrong version format v20190211"),
			input:     "v20190211",
		},
		{
			name:      "wrong long version",
			expectErr: fmt.Errorf("wrong version format 20190211-preview"),
			input:     "20190211-preview",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {

			err := ValidateVersion(test.input)
			if !assert.Equal(t, test.expectErr, err) {
				t.Errorf("%s: expected result:\n %v \ngot result:\n %v \n", test.name, test.expectErr, err)
			}

		})
	}

}

func TestLongVersion(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name:     "short version",
			input:    "v20190211preview",
			expected: "2019-02-11-preview",
		},
		{
			name:     "long version",
			input:    "v20190211",
			expected: "2019-02-11",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {

			short, err := longVersion(test.input)
			if err != nil {
				t.Error(err)
			}
			if !assert.Equal(t, test.expected, short) {
				t.Errorf("%s: expected result:\n %v \ngot result:\n %v \n", test.name, test.expected, short)
			}

		})
	}

}
