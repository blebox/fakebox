#!/usr/bin/env bash

function device() {
  module=$1
  port=$2

  echo "port[$port]: $module"
  flask --app devices.$module run --port $port --reload &
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

while true; do
  sleep 0.1
done
