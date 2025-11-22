#!/usr/bin/env bash

image=$1

docker manifest rm "svanosselaer/via-node-${image}:latest" 2>/dev/null || true

docker manifest create \
  "svanosselaer/via-node-${image}:latest" \
  --amend "svanosselaer/via-node-${image}:amd64" \
  --amend "svanosselaer/via-node-${image}:arm64" &&
docker manifest push "svanosselaer/via-node-${image}:latest"
