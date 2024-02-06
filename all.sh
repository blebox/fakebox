#!/usr/bin/env bash

function device() {
  local module=$1
  local port=$2

  echo "port[$port]: $module"
  flask --app devices.$module run --port $port --reload | grep -v "This is a development server" & # who cares

  if command -v dns-sd &> /dev/null; then
    dns-sd -P $module _bbxsrv local. $port localhost 127.0.0.1 &
  fi
}

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# ---
device switchboxd_20190808 5001
device switchboxd_20200229 5002
device switchboxd_20200831 5003
# ---
device switchbox_20180604 5011
device switchbox_20190808 5012
device switchbox_20200229 5013
device switchbox_20200831 5014
device switchbox_20220114 5015
# ---
device floodsensor_20200831 5021
device floodsensor_20210413 5022
# ---
device windrainsensor_20200831 5031
device windrainsensor_20210413 5032

while true; do
  sleep 0.1
done
