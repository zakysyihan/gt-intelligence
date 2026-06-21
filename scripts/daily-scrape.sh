#!/bin/bash
# GT Intelligence — Daily scrape + pipeline
# Runs at 06:00 WIB daily via cron
# Log to /home/ubuntu/gt-intelligence/logs/pipeline.log

cd /home/ubuntu/gt-intelligence
mkdir -p logs
echo "$(date) — Pipeline started" >> logs/pipeline.log
python3 -m src.pipeline.run_pipeline >> logs/pipeline.log 2>&1
echo "$(date) — Pipeline finished" >> logs/pipeline.log
