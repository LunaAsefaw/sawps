#!/usr/bin/env bash

echo "This script will run the tests defined in tests/"
echo "Before running the tests you need to create the auth config using this command:"
echo ""
echo "./create-auth.sh"

echo "Choose OS"
echo "1. NixOS
2. Debian\Ubuntu"
read option
case $option in
  1   ) playwright \
          test \
          --ui \
          --project chromium;;
  2   ) npx playwright \
          test \
          --ui \
          --project chromium;;
esac

echo "--done--"