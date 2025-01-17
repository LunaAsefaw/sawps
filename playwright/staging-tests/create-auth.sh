#!/usr/bin/env bash

echo "This script will write a new test to tests/deleteme.spec.ts"
echo "then delete it, leaving only the auth config."
echo ""
echo "When the playwright browser opens, log in to the site then exit."
echo "After recording your test, close the test browser."
echo "Recording auth token to auth.json"

# File exists and write permission granted to user
# show prompt
echo "Continue? y/n"
read ANSWER
case $ANSWER in 
  [yY] ) echo "Writing auth.json" ;;
  [nN] ) echo "Cancelled."; exit ;;
esac

source base-url.sh

echo "Choose OS"
echo "1. NixOS
2. Debian\Ubuntu"
read option
case $option in
  1   ) playwright \
          codegen \
          --target playwright-test \
          --save-storage=auth.json \
          -o tests/deleteme.spec.ts \
          $BASE_URL;;
  2   ) npx playwright \
          codegen \
          --target playwright-test \
          --save-storage=auth.json \
          -o tests/deleteme.spec.ts \
          $BASE_URL;;
esac

# We are only interested in sawps-auth.json
rm tests/deleteme.spec.ts

echo "Auth file creation completed."
echo "You can then run your tests by doing e.g.:"
echo "playwright test --project chromium"
