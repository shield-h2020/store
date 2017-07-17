#/bin/bash

package=${1//\'/\'}

curl -X POST -F "package=@$package" http://127.0.0.1:5000/vnsfs/
