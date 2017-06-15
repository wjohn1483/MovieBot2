#!/bin/bash

# bash make_list.sh <video_path> <ouput_list_path>
usage() { echo "Usage: $0 -i <video_path> -o <output_list_path(with or without filename)>" 1>&2; exit 1; }
while getopts ":i:o:" argv
do
	case $argv in
	i)
		file_path=$OPTARG
		;;
	o)
		output_path=$OPTARG
		;;
	*)
		usage
		exit
		;;
	esac
done

cd $file_path
ls | sed "s:^:`pwd`/:" > ./output.list
cd -
mv $file_path/output.list $output_path

