#!/bin/bash
initdb --auth=trust --username=$USERNAME -D db/
pg_ctl start -D db/ -o "-p 43353 -c unix_socket_directories=$PWD/db"
