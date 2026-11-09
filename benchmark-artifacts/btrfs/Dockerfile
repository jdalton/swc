FROM debian:bookworm-slim
RUN apt-get update -qq && apt-get install -y -qq python3 btrfs-progs btrfs-compsize nodejs >/tmp/install.log 2>&1 && apt-get clean
