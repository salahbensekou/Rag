#!/usr/bin/env bash
set -e

CMD=$1

case "$CMD" in
  build)
    docker-compose build
    ;;
  up)
    docker-compose up -d
    ;;
  down)
    docker-compose down
    ;;
  ingest)
    docker-compose run --rm backend python -m app.ingest
    ;;
  logs)
    docker-compose logs -f
    ;;
  *)
    echo "Usage: ./docker.sh {build|up|down|ingest|logs}"
    exit 1
    ;;
esac
