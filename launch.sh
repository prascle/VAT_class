#!/usr/bin/env bash

CONDA_ROOT=$(realpath "$(dirname $(which conda))/..")
. ${CONDA_ROOT}/etc/profile.d/conda.sh                                       # required to have access to conda commands in a shell script

conda activate astro6
export LANG='C'
pyside6-uic main.ui > ui_mainwindow.py

./mainGui.py
