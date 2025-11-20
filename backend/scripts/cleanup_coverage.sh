#!/bin/bash
# cleanup_coverage.sh
# Script to forcibly remove coverage files in Docker container

echo "強制的にカバレッジファイルを削除しています..."
docker exec -u root todo_backend bash -c "rm -rf /app/htmlcov && mkdir -p /app/htmlcov && chown -R todouser:todouser /app/htmlcov"
echo "完了しました"
