#!/usr/bin/env bash

echo "This script will write a new test to tests/deleteme.spec.ts"
echo "then delete it, leaving only the auth config."
echo ""
echo "When the playwright browser opens, log in to the site then exit."
echo "After recording your test, close the test browser."
echo "Recording auth token to sawps-auth.json"

# File exists and write permission granted to user
# show prompt
echo "Continue? y/n"
read ANSWER
case $ANSWER in 
  [yY] ) echo "Writing sawps-auth.json" ;;
  [nN] ) echo "Cancelled."; exit ;;
esac

npx playwright \
  codegen \
  --save-storage=tests/.auth/sawps-auth.json \
  -o tests/deleteme.spec.ts \
  http://sawps.sta.do.kartoza.com

# We are only interested in sawps-auth.json
rm tests/deleteme.spec.ts

echo "Auth file creation completed."
echo "You can then run your tests by doing e.g.:"
echo "npx playwright test tests/filename.spec.ts"
