#!/bin/bash

usage() { echo "Usage: $0 -i <video_file> -o <feat_dir> -f <frame>" 1>&2; exit 1; }

while getopts ":i:o:f:" arg; do
	case "${arg}" in
		i)
			video_file=${OPTARG}
			;;
		o)
			feat_dir=${OPTARG}
			;;
		f)
			frame=${OPTARG}
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND-1))

if [ -z "${video_file}" ] || [ -z "${feat_dir}" ] || [ -z "${frame}" ]; then
	usage
fi

video_name=$(echo $(basename $video_file) | cut -d '.' -f 1)
log=$feat_dir/log

## check if vgg caffe model exists
#if [ ! -e "./material/models/vgg/VGG_ILSVRC_19_layers.caffemodel" ]; then
#	#cd ./material/models/vgg
#	wget -c --no-check-certificate -P ./material/models/vgg/ https://speech.ee.ntu.edu.tw/~zyi870701/MTK_project/VGG_ILSVRC_19_layers.caffemodel
#	#cd ../../../
#fi
#
## check if feat directory exists
#if [ ! -d "$feat_dir" ]; then
#	mkdir $feat_dir
#fi
#
## extract vgg feats
#echo "Extract vgg feats..."
#python utility/preprocessing.py $video_file $feat_dir $frame >> $log 2>&1
#
## extract audio
#echo "Extract audio from video..."
#ffmpeg -y -i $video_file -ar 48000 -acodec pcm_s16le -ac 2 $feat_dir/$video_name.wav >> $log 2>&1

# extract mfcc feats
echo "Extract mfcc feats..."
echo "$video_name $feat_dir/$video_name.wav" >> tmp.scp
compute-mfcc-feats --sample-frequency=44100 --channel=0 scp:tmp.scp ark,t,scp:$feat_dir/$video_name.mfcc.ark,$feat_dir/$video_name.mfcc.scp >> $log 2>&1
rm tmp.scp

# extract audio word2vec
echo "Extract audio word2vec feats..."
python utility/sa.py $feat_dir/$video_name.mfcc.scp $feat_dir $frame >> $log 2>&1
