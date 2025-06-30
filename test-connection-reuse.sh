#!/bin/bash

echo "Testing TCP connection reuse with proxy delay..."
echo "=============================================="
echo

echo "Test 1: Single curl with multiple URLs (connection reuse)"
echo "----------------------------------------------------------"
curl -w "Request 1 - connect: %{time_connect}s, start_transfer: %{time_starttransfer}s, total: %{time_total}s\nRequest 2 - connect: %{time_connect}s, start_transfer: %{time_starttransfer}s, total: %{time_total}s\n" \
     -o /dev/null -s \
     --keepalive-time 60 \
     -H "Connection: keep-alive" \
     'http://system:System123@localhost:18080/api/loginConfig' \
     'http://system:System123@localhost:18080/api/loginConfig'

echo
echo "Test 2: Separate curl commands (new connections)"
echo "------------------------------------------------"
curl -w "Request 1 - connect: %{time_connect}s, start_transfer: %{time_starttransfer}s, total: %{time_total}s\n" \
     -o /dev/null -s \
     --keepalive-time 60 \
     -H "Connection: keep-alive" \
     'http://system:System123@localhost:18080/api/loginConfig'

curl -w "Request 2 - connect: %{time_connect}s, start_transfer: %{time_starttransfer}s, total: %{time_total}s\n" \
     -o /dev/null -s \
     --keepalive-time 60 \
     -H "Connection: keep-alive" \
     'http://system:System123@localhost:18080/api/loginConfig'

echo
echo "Expected results:"
echo "- Test 1: First request ~2s delay, second request ~0.1s (connection reused)"
echo "- Test 2: Both requests ~2s delay (new connections each time)"