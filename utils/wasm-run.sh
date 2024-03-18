#!/usr/bin/env bash

##################################################################
## Script for running Wasm Juliet Test cases.
## Make this read stdout to determine if Wassy detected overflow.
##
##
## file: run_wasm.sh
##################################################################

# Some shortcuts for printf colorization.
RED='\033[0;31m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

SCRIPT_DIR=$(dirname $(realpath "$0"))

run_tests()
{
  local CWE_DIRECTORY="$1"
  local CWE="$2"
  local TEST_TYPE="$3"
  local TYPE_PATH="${CWE_DIRECTORY}/$CWE/${TEST_TYPE}"

  local PREV_CWD=$(pwd)
  cd "${CWE_DIRECTORY}" # change directory in case of test-produced output files

  echo "========== STARTING TEST ${TYPE_PATH} $(date) ==========" >> "${TYPE_PATH}.run"
  for TESTCASE in $(find $TYPE_PATH -name '*.js'); do
#   for TESTCASE in $(ls -1 "${TYPE_PATH}"); do
    # echo "[+] TESTCASE: $TESTCASE"

    # local TESTCASE_PATH="${TYPE_PATH}/${TESTCASE}"

    # if [ ! -z "${PRELOAD_PATH}" ]
    # then
    #   timeout "${TIMEOUT}" env LD_CHERI_PRELOAD="${PRELOAD_PATH}" "${TESTCASE_PATH}" < "${INPUT_FILE}"
    # else
    #   timeout "${TIMEOUT}" "${TESTCASE_PATH}" < "${INPUT_FILE}"
    # fi

    run_result=$(node $TESTCASE)

    # echo $? >> "$TYPE_PATH.run"
    echo "${run_result} $?" >> "$TYPE_PATH.run"

    # if [[ $? -eq 0 ]] ; then
    #     echo $? >> "$TYPE_PATH.run"
    # else
    #     echo "${run_result} $?" >> "$TYPE_PATH.run"
    # fi
  done

  cd "${PREV_CWD}"
}

# run_tests "${SCRIPT_DIR}/wasm_bin" "CWE121" "good"
# Just care about the "bad" ones for now, since that's what we test our canaries against.
run_tests "${SCRIPT_DIR}/wasm_bin" "CWE121" "bad"
