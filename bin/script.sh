#!/bin/sh
#~ sudo apt-get install python-flask
if [ "$#" -ne 3 ]
then
echo "Illegal number of parameters"
else
python ../src/clean.py $1
python ../src/configure.py $1
python ../src/server.py $3 $2
fi
