#/bin/bash

etag=$1
vnsf_id=$2

curl -H "If-Match: ${etag}" -X DELETE http://127.0.0.1:5000/vnsfs/${vnsf_id}
