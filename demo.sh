#!/bin/bash
./fsst --docker --dir demo-schema-parts --tag fluree-0.15.7
./fsst --docker --dir experiments --target user_ok --tag fluree-0.15.7
./fsst --docker --dir experiments --target user_not_ok --tag fluree-0.15.7
./fsst --docker --dir experiments --target user_both --tag fluree-0.15.7
./fsst --docker --dir experiments --target auth_ok --tag fluree-0.15.7
./fsst --docker --dir experiments --target auth_not_ok --tag fluree-0.15.7
./fsst --docker --dir experiments --target auth_both --tag fluree-0.15.7
