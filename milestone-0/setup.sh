#!/usr/bin/env bash
#
# CS348 Project - Milestone 0 Setup Script
#

set -e

DB_NAME=cs-348
DB_USER=current-user
echo "Enter your MySQL password (leave blank if none):"
read -rs DB_PASS

MYSQL_CMD="mysql -u $DB_USER"
if [ -n "$DB_PASS" ]; then
  MYSQL_CMD="$MYSQL_CMD -p$DB_PASS"
fi

echo "Creating database '$DB_NAME'..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
echo "Database '$DB_NAME' created successfully!"
echo ""
echo "You can connect to it with:"
echo "  mysql -u $DB_USER -p $DB_NAME"
