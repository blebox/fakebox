#!/usr/bin/env bash

usage() {
  echo "Usage: $0 [-h][--help][-k FILTER]"
  echo "  -h | --help     Display this help message"
  echo "  -k FILTER       Filter devices by name"
}

while getopts ":hk:" opt; do
  case ${opt} in
    h)
      usage
      HELPMODE=1
      ;;
    k)
      MODULE_FILTER=$OPTARG
      ;;
    \?)
      echo "Invalid option: $OPTARG" 1>&2
      usage
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." 1>&2
      usage
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

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
  # abort running things in helpmode
  if [[ ! -z ${HELPMODE} ]]; then
    return
  fi

  flask --app devices.$module run --port $port $extra | grep -v "This is a development server" & # who cares

  if command -v dns-sd &> /dev/null; then
    dns-sd -P $module _bbxsrv local. $port localhost 127.0.0.1 &
  fi
}
# --- switchbox family
device switchboxd_20190808        5001 --reload
device switchboxd_20200229        5002 --reload
device switchboxd_20200831        5003 --reload
device switchbox_20180604         5011 --reload
device switchbox_20190808         5012 --reload
device switchbox_20200229         5013 --reload
device switchbox_20200831         5014 --reload
device switchbox_20220114         5015 --reload
# --- floodsensor family
device floodsensor_20200831       5021 --reload
device floodsensor_20210413       5022 --reload
# --- windrainsensor family
device windrainsensor_20200831    5031 --reload
device windrainsensor_20210413    5032 --reload
# --- lightbox family
MODE=1 device wlightbox_20200229  5041 --reload  # RGBW
MODE=2 device wlightbox_20200229  5042 --reload  # RGB
MODE=3 device wlightbox_20200229  5043 --reload  # MONO
MODE=4 device wlightbox_20200229  5044 --reload  # RGBorW
MODE=5 device wlightbox_20200229  5045 --reload  # CT
MODE=6 device wlightbox_20200229  5046 --reload  # CTx2
MODE=7 device wlightbox_20200229  5047 --reload  # RGBWW
# --- multisensor family
device multisensor_20220114       5051 --reload
device multisensor_20230606       5052 --reload
# --- smartmeter family (multisensor flavour)
device smartmeter_20230606        5061 --reload
# --- shutterbox family
MODE=1 VARIANT=segmented  device shutterbox_20190911 5151
MODE=2 VARIANT=nocalib    device shutterbox_20190911 5152
MODE=3 VARIANT=tilt       device shutterbox_20190911 5153
MODE=4 VARIANT=window     device shutterbox_20190911 5155
MODE=5 VARIANT=material   device shutterbox_20190911 5156
MODE=6 VARIANT=awning     device shutterbox_20190911 5157
MODE=7 VARIANT=screen     device shutterbox_20190911 5158
MODE=8 VARIANT=curtain    device shutterbox_20190911 5159
# --- gatebox family
MODE=0 VARIANT=step-by-step device gatebox_20230102 5161
MODE=1 VARIANT=only-open    device gatebox_20230102 5162
MODE=2 VARIANT=open-close   device gatebox_20230102 5163

# --- faulty devices ---
FAULTY=1 MODE=3 VARIANT=tilt-faulty device shutterbox_20190911 5953

if [[ -z "${HELPMODE}" ]]; then
  trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
  while true; do
    sleep 0.1
  done
fi
