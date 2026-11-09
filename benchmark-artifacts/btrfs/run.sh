#!/bin/sh
set -eu
truncate -s 512M /tmp/benchmark-btrfs.img
mkfs.btrfs -q -f /tmp/benchmark-btrfs.img
mkdir -p /mnt/benchmark
mount -o loop,noatime /tmp/benchmark-btrfs.img /mnt/benchmark
trap 'umount /mnt/benchmark' EXIT
python3 /bench/benchmark.py
