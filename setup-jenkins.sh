#!/bin/bash

ARG=$1

if [[ ${ARG} == "install-depends" ]]; then
  virtualenv env -p python3
  . env/bin/activate
  make install-depends
elif [[ ${ARG} == "migrate" ]]; then
  . env/bin/activate
  make migrate
else
  echo "Unsupported argument ${ARG}, please see usage below"
  echo "./setup-jenkins.sh install-depends"
  echo "./setup-jenkins.sh migrate"
fi
