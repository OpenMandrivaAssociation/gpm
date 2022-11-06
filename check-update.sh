#!/bin/sh
curl -L https://www.nico.schottelius.org/software/gpm/archives/ 2>/dev/null |grep .tar.lzma |sed -e 's,.*>gpm-,,;s,\.tar.*,,' |grep -v '1.99' |sort -V |tail -n1
