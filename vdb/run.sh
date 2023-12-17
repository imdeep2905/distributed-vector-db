#!/bin/bash
export REPLICA_INDEX=$(echo "$( v="$( nslookup "$( hostname -i )" | head -n 1 )"; v="${v##* = }"; v="${v%%.*}"; v="${v##*-}"; v="${v##*_}"; echo "$v" )")
python app.py