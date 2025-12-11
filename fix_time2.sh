#!/bin/bash

DURATION="5s"
# We add 0.012 seconds (12ms) to compensate for script processing time.
OFFSET="0.032" 

echo "Capturing data..."

# 1. Capture the data
DATA=$(timeout $DURATION ros2 topic echo /utlidar/scan)

if [ -z "$DATA" ]; then
    echo "Error: No data captured."
    exit 1
fi

# 2. Extract Timestamp
# We grep for sec/nanosec, ignoring 'header' or other fields if possible
RAW_SEC=$(echo "$DATA" | grep "sec:" | grep -v "nanosec" | tail -n 1 | awk '{print $2}')
RAW_NANO=$(echo "$DATA" | grep "nanosec:" | tail -n 1 | awk '{print $2}')

SEC=${RAW_SEC//[^0-9]/}
NANO=${RAW_NANO//[^0-9]/}

if [ -z "$SEC" ] || [ -z "$NANO" ]; then
    echo "Error: Could not parse timestamp."
    exit 1
fi

# 3. Calculate New Time with Offset using Python (Handles the math easily)
# We combine Sec + Nano, add the Offset, and print the new time.
NEW_TIME=$(python3 -c "print('%.9f' % ($SEC + $NANO/1000000000.0 + $OFFSET))")

echo "--------------------------------"
echo "Original Lidar: $SEC.$NANO"
echo "Adjusted Time:  $NEW_TIME (Added ${OFFSET}s lag comp)"
echo "--------------------------------"

# 4. Apply the time
sudo date -s "@$NEW_TIME"

echo "Sync Complete."
