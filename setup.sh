# Set the PYTHONPATH to include this install directory. This setup script
# can be sourced from any directory.
#
inst_dir=$( cd $(dirname $BASH_SOURCE); pwd -P )
export PYTHONPATH=${inst_dir}/python:${PYTHONPATH}
export PATH=${inst_dir}/python:${PATH}
