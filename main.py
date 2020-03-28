#!/usr/bin/python3

import ffmpeg
import requests
import youtube_dl
import subprocess
import sys


ytdl_options = {
    'format': 'mp4',
    'outtmpl':'downloads/target.%(ext)s',
}

def download_video(youtube_url):
    # download video from URL
    with youtube_dl.YoutubeDL(ytdl_options) as ytdl:
        info = ytdl.extract_info(youtube_url, download=False)
        ytdl.download([youtube_url,])
        video_title = info.get('title', None)
        return video_title



def trim(input_path, output_path, start, end):
    input_stream = ffmpeg.input(input_path)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[1], output_path)
    output.run()

def timestamp_parser(timestring):
    # format 000000-000030_000100-000145_ ....
    timestamps = [ [f'{x[:2]}:{x[2:4]}:{x[4:]}' for x in x.split('-')] for x in timestring.split('_')]
    return list(timestamps)

if __name__ == '__main__':
    # first, accept arguments
    arguments = sys.argv[1:]
    url = arguments[0]
    timestamps = timestamp_parser(arguments[1])

    raw_title =  download_video(url.strip())
    downloaded_path = 'downloads/target.mp4'
    print(downloaded_path)

    infile = ffmpeg.input(downloaded_path)
    # begin ffmpeg command block

    # test chopping up different parts
    for i in range(1, len(timestamps)+1):
        trim(downloaded_path, f'{i}.mp4', timestamps[i-1][0], timestamps[i-1][1])

    # concatenation
    mp4file_paths = [f'{x+1}.mp4' for x in range(len(timestamps))] #+ ['outtro.mp4']
    sep = '|'

    # create intermediate files
    mergecommand = ["mencoder", "-forceidx", "-ovc", "copy", "-oac", "pcm", "-o", 'trailer.mp4'] + mp4file_paths
    subprocess.call(mergecommand)
