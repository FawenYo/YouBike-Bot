#!/bin/sh

set -e

get_random_file_name() {
  number=$(shuf -i 1-1000000 -n 1)
  echo $number
}

# Set the IFS to comma
IFS=","

# Loop through the array and parse the values
for item in $CRON_JOBS; do
  # Trim leading and trailing whitespace
  item=$(echo "$item" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

  # Split the item into cmd and schedule using the pipe character
  cmd=$(echo "$item" | cut -d'|' -f1)
  schedule=$(echo "$item" | cut -d'|' -f2)


  # Trim leading and trailing whitespace from cmd and schedule
  cmd=$(echo "$cmd" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  schedule=$(echo "$schedule" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  echo "cmd: $cmd"
  echo "schedule: $schedule"

  while true; do
    number=$(get_random_file_name)
    FILE=/app/curl_$number.sh
    if [ -f "$FILE" ]; then
      echo "$FILE exists"
      continue
    else
      echo "$FILE does not exist"
      break
    fi
  done
  echo "$cmd" >> /app/curl_$number.sh
  chmod +x /app/curl_$number.sh
  echo "$schedule /app/curl_$number.sh" >> /var/spool/cron/crontabs/root
done

crond -l 2 -f
