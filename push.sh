#!/usr/bin/env bash

image=$1 &&
architecture=$2 &&

if [ -z "$architecture" ]; then
  docker push "svanosselaer/via-node-${image}" --all-tags
else
  docker push "svanosselaer/via-node-${image}:${architecture}"
fi
