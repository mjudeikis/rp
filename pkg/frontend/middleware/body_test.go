package middleware

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBody(t *testing.T) {
	assert := assert.New(t)

	tests := []struct {
		name   string
		url    string
		method string
		header map[string]string

		expectedCode int
	}{
		{
			name:   "Get request - No checking",
			url:    "/test",
			method: "GET",

			expectedCode: 200,
		},
		{
			name:   "Post request - un-supported media type",
			url:    "/test",
			method: "POST",
			header: map[string]string{
				"Content-Type": "test",
			},

			expectedCode: 415,
		},
		{
			name:   "Post request - supported media type",
			url:    "/test",
			method: "POST",
			header: map[string]string{
				"Content-Type": "application/json",
			},

			expectedCode: 200,
		},
		{
			name:   "Put request - supported media type",
			url:    "/test",
			method: "PUT",
			header: map[string]string{
				"Content-Type": "application/json",
			},

			expectedCode: 200,
		},
		{
			name:   "Patch request - supported media type",
			url:    "/test",
			method: "PATCH",
			header: map[string]string{
				"Content-Type": "application/json",
			},

			expectedCode: 200,
		},
	}

	ts := httptest.NewServer(Body(GetTestHandler()))
	defer ts.Close()
	client := http.Client{}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var u bytes.Buffer
			u.WriteString(string(ts.URL))
			u.WriteString(test.url)

			req, err := http.NewRequest(test.method, u.String(), bytes.NewBuffer([]byte("")))
			assert.NoError(err)

			headers := http.Header{}
			for n, h := range test.header {
				headers.Set(n, h)
			}
			req.Header = headers

			res, err := client.Do(req)
			assert.NoError(err)

			_, err = ioutil.ReadAll(res.Body)
			assert.NoError(err)
			assert.Equal(test.expectedCode, res.StatusCode)
		})

	}
}

func GetTestHandler() http.HandlerFunc {
	fn := func(rw http.ResponseWriter, req *http.Request) {
		rw.Write([]byte("ack"))
	}
	return http.HandlerFunc(fn)
}
