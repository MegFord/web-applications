#!/bin/sh
for i in *.bz2;
do 
    7za e "$i" 
done
