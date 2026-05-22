#!/bin/sh
set -e

echo "Waiting for MySQL..."

until mysql -h mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1"; do
  sleep 2
done

echo "Running migrations..."
flask db upgrade