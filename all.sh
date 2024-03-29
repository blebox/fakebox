#!/usr/bin/env bash

usage() {
  echo "Usage: $0 [-h][--help][-k FILTER]"
  echo "  -h | --help     Display this help message"
  echo "  -k FILTER       Filter devices by name"
    echo "Available Devices:"
  echo "------------------"
  echo "switchboxd_20190808 (port: 5001)"
  echo "switchboxd_20200229 (port: 5002)"
  echo "switchboxd_20200831 (port: 5003)"
  echo "switchbox_20180604 (port: 5011)"
  echo "switchbox_20190808 (port: 5012)"
  echo "switchbox_20200229 (port: 5013)"
  echo "switchbox_20200831 (port: 5014)"
  echo "switchbox_20220114 (port: 5015)"
  echo "floodsensor_20200831 (port: 5021)"
  echo "floodsensor_20210413 (port: 5022)"
  echo "windrainsensor_20200831 (port: 5031)"
  echo "windrainsensor_20210413 (port: 5032)"
  echo "wlightbox_20200229 (port: 5041)"
  echo "shutterbox_20190911 (port: 5051 to 5059)"
  echo "gatebox_20230102 (port: 5061 to 5063)"
  echo "shutterbox_20190911 (port: 5953)"
  echo "------------------"
  exit 1
}

while getopts ":hk:" opt; do
  case ${opt} in
    h)
      usage
      ;;
    k)
      MODULE_FILTER=$OPTARG
      ;;
    \?)
      echo "Invalid option: $OPTARG" 1>&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." 1>&2
      usage
      ;;
  esac
done
shift $((OPTIND -1))

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
  display_available_devices
  exit 0
fi

while [[ $# -gt 0 ]]; do
  echo "Too many arguments: ${@}"
  usage
done

function device() {
  local module=$1
  local port=$2
  local extra=$3

  # Skip processing if module filter is specified and there's no match
  if [[ -n $MODULE_FILTER ]] && ! (echo "$module" | grep -q "$MODULE_FILTER"); then
    return
  fi

  echo "port[$port]: $module"
  flask --app devices.$module run --port $port $extra | grep -v "This is a development server" & # who cares

  if command -v dns-sd &> /dev/null; then
    dns-sd -P $module _bbxsrv local. $port localhost 127.0.0.1 &
  fi
}
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
# ---
device switchboxd_20190808 5001 --reload
device switchboxd_20200229 5002 --reload
device switchboxd_20200831 5003 --reload
# ---
device switchbox_20180604 5011 --reload
device switchbox_20190808 5012 --reload
device switchbox_20200229 5013 --reload
device switchbox_20200831 5014 --reload
device switchbox_20220114 5015 --reload
# ---
device floodsensor_20200831 5021 --reload
device floodsensor_20210413 5022 --reload
# ---
device windrainsensor_20200831 5031 --reload
device windrainsensor_20210413 5032 --reload
# ---
device wlightbox_20200229 5041 --reload
# ---
MODE=1 VARIANT=segmented            device shutterbox_20190911 5051
MODE=2 VARIANT=nocalib              device shutterbox_20190911 5052
MODE=3 VARIANT=tilt                 device shutterbox_20190911 5053
MODE=4 VARIANT=window               device shutterbox_20190911 5055
MODE=5 VARIANT=material             device shutterbox_20190911 5056
MODE=6 VARIANT=awning               device shutterbox_20190911 5057
MODE=7 VARIANT=screen               device shutterbox_20190911 5058
MODE=8 VARIANT=curtain              device shutterbox_20190911 5059
# ---
MODE=0 VARIANT=step-by-step   device gatebox_20230102 5061
MODE=1 VARIANT=only-open      device gatebox_20230102 5062
MODE=2 VARIANT=open-close     device gatebox_20230102 5063
# --- faulty devices ---
FAULTY=1 MODE=3 VARIANT=tilt-faulty device shutterbox_20190911 5953
while true; do
  sleep 0.1
done