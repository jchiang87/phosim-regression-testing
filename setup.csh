#!/bin/csh
#
# Set the PYTHONPATH to include this install directory. This setup script
# can be sourced from any directory.
#
set sourced=($_)
set inst_dir=`/usr/bin/dirname $sourced[2]`
set inst_dir=`cd ${inst_dir}; pwd -P`
setenv PYTHONPATH ${inst_dir}/python:${PYTHONPATH}
setenv PATH ${inst_dir}/python:${PATH}

