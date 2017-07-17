#/bin/bash

vnsf_id=$1

curl -H "Content-Type: application/json" -X GET http://127.0.0.1:5000/vnsfs/${vnsf_id}
