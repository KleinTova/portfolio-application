#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please provide the host address as an argument."
    exit 1
fi

HOST=$1
BASE_URL="http://$HOST:5000"
SUCCESS=0
FAILED=0

#comment

performRequest() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local expected_status="$4"
    local accept_header="$5"

    if [ "$method" == "POST" ] || [ "$method" == "PUT" ]; then
        form_data=$(echo "$data" | sed 's/[{}"]//g; s/,/\&/g; s/:/=/g')
        response=$(curl -v -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -H "Accept: $accept_header" \
            -d "$form_data")
    else
        response=$(curl -v -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Accept: $accept_header")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo "✅ $method $endpoint - Success"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌ $method $endpoint - Failed (Expected: $expected_status, Got: $status_code)"
        echo "Response body: $body"
        FAILED=$((FAILED + 1))
    fi
}

echo "Starting E2E tests for Event Planner API"

performRequest "GET" "/" "" "200" "text/html"

EVENT_DATA='{"name":"Test Event","date":"2023-09-01","location":"Test Location","description":"Test Description"}'
performRequest "POST" "/event/create" "$EVENT_DATA" "200" "application/json"

performRequest "GET" "/events" "" "200" "text/html"

# performRequest "GET" "/event/1" "" "200" "application/json"

# UPDATE_DATA='{"name":"Updated Event","date":"2023-09-02","location":"Updated Location","description":"Updated Description"}'
# performRequest "PUT" "/event/1" "$UPDATE_DATA" "200" "application/json"
# 
# performRequest "POST" "/event/delete/1" "" "200" "text/html"

performRequest "GET" "/metrics" "" "200" "text/plain"

echo "E2E tests completed"
echo "Successful tests: $SUCCESS"
echo "Failed tests: $FAILED"

if [ $FAILED -eq 0 ]; then
    echo "All tests passed successfully!"
    exit 0
else
    echo "Some tests failed. Please check the output above."
    exit 1
fi