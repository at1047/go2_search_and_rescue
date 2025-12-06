#!/bin/bash

DURATION="5s"
echo "Capturing data for $DURATION..."

# 1. Capture data
DATA=$(timeout $DURATION ros2 topic echo /utlidar/scan)

if [ -z "$DATA" ]; then
    echo "Error: No data captured."
    exit 1
fi

# 2. Extract Timestamp SAFELY
# grep -v "nanosec" ensures we don't accidentally grab the nanoseconds line for the seconds variable
RAW_SEC=$(echo "$DATA" | grep "sec:" | grep -v "nanosec" | tail -n 1 | awk '{print $2}')
RAW_NANO=$(echo "$DATA" | grep "nanosec:" | tail -n 1 | awk '{print $2}')

# Clean up numbers
SEC=${RAW_SEC//[^0-9]/}
NANO=${RAW_NANO//[^0-9]/}

# 3. Validation
if [ -z "$SEC" ] || [ -z "$NANO" ]; then
    echo "Error: Could not parse timestamp."
    exit 1
fi

# 4. SAFETY CHECK: Is the year reasonable?
# 1700000000 is roughly the year 2024. If SEC is lower, the LiDAR is providing "Time since boot", not "Real World Time".
if [ "$SEC" -lt 1764989415 ]; then
    echo "------------------------------------------------"
    echo "DANGER: The LiDAR returned a timestamp from the past!"
    echo "LiDAR Value: $SEC seconds (This is roughly year $(date -d @$SEC +%Y))"
    echo "------------------------------------------------"
    echo "This means the LiDAR is counting 'Time since power-on', not 'Real World Time'."
    echo "Aborting sync to prevent messing up your system clock."
    echo "------------------------------------------------"
    exit 1
fi

# 5. Format and Apply
FORMATTED_NANO=$(printf "%09d" $NANO)
NEW_TIME="@$SEC.$FORMATTED_NANO"

echo "--------------------------------"
echo "Valid Timestamp Found:"
echo "Seconds:     $SEC"
echo "Nanoseconds: $FORMATTED_NANO"
echo "Target Time: $(date -d @$SEC)"
echo "--------------------------------"

echo "Updating system clock..."
sudo date -s "$NEW_TIME"
echo "Sync Complete."
