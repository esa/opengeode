#!/bin/bash
apt update || exit 1
apt install -y make python3 python3-pip sudo || exit 1
make dependencies || exit 1
make install || exit 1
make pytest || exit 1
make test-ada || exit 1
exit 0
