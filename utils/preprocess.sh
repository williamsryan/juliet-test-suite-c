#!/usr/bin/env bash

##################################################################
## Script for moving all *relevant* JS files into dir with Wasm.
##
##
## file: preprocess.sh
##################################################################

# Some shortcuts for printf colorization.
RED='\033[0;31m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Parse command line arguments
INSTRUMENTED_DIR=$1
UNFILTERED_DIR=$2

# Check if directories exist
if [ ! -d "$INSTRUMENTED_DIR" ]; then
  printf "${RED}Error: $INSTRUMENTED_DIR does not exist${NC}\n"
  exit 1
fi

if [ ! -d "$UNFILTERED_DIR" ]; then
  printf "${RED}Error: $UNFILTERED_DIR does not exist${NC}\n"
  exit 1
fi

# Get list of files in instrumented directory
FILES=$(ls $INSTRUMENTED_DIR)

# For each file, check for corresponding .js file in unfiltered directory
for FILE in $FILES; do
  BASENAME=$(basename $FILE .wasm)
  JSFILE="$UNFILTERED_DIR/$BASENAME.js"
  if [ -f "$JSFILE" ]; then
    cp $JSFILE $INSTRUMENTED_DIR
  else
    printf "${CYAN}Warning: No corresponding .js file for $FILE in $UNFILTERED_DIR${NC}\n"
  fi
done