#!/bin/bash
apt update || exit 1
apt install -y make libegl1-mesa libxkbcommon0 libdbus-1-3 python3 python3-pip sudo wget || exit 1
make dependencies || exit 1
make install || exit 1
make test-ada || exit 1
make pytest || exit 0  # the Qt test fails with a segfault in the travis VM due to Pyside version mismatch
exit 0
