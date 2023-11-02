#!/usr/bin/env bash

echo "This script will write a new test to tests/deleteme.ts"
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

playwright \
  codegen \
  --target python \
  --save-storage=auth.json \
  -o tests/deleteme.ts \
  https://sawps.sta.do.kartoza.com

# We are only interested in auth.json
rm tests/deleteme.ts

echo "Auth file creation completed."
echo "You can then run your tests by doing e.g.:"
echo "pytest tests/filename.ts"
