import assemblyai as aai
import ffmpeg
import PIL 
from PIL import Image
import os
import sys

filename_no_ext         = "arttherapy"
key_filename            = "private/assemblyai.key"
video_source_filename   = "media/" + filename_no_ext + "/" + filename_no_ext + ".mp4"
audio_output_filename   = "media/" + filename_no_ext + "/" + filename_no_ext + "_audio.m4a"
captions_output         = "media/" + filename_no_ext + "/" + filename_no_ext + "_captions.srt"
video_with_subs_filename= "media/" + filename_no_ext + "/" + filename_no_ext + "_withsubs.mp4"
qrcode_filename         = "media/" + filename_no_ext + "/" + filename_no_ext + "_qrcode.png"

# download youtube file (this one requires audio and video separately)
# https://ytdl.hamsterlabs.de/

# QR Code generator 
# https://www.the-qrcode-generator.com/

def extract_audio():
    (
        ffmpeg
        .input(video_source_filename)
        .output(audio_output_filename)
        .run()
    )

def generate_captions():
    # upload audio to AssemblyAI and save captions to .srt
    print("Note: the VA proxy blocks using SSL to interact with AssemblyAI. \n \
        Switch to a wifi hotspot to work with the API.")
    
    keyfile = open(key_filename, "r")
    aai.settings.api_key = keyfile.readlines()[0].strip('\n')
    keyfile.close()

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_output_filename)

    srt_content = transcript.export_subtitles_srt()
    srtfile = open(captions_output, "w")
    srtfile.write(srt_content)
    srtfile.close()
    print("srt saved at " + captions_output)


def get_video_size():
    # can simplify this with ffprobe, todo later
    temp_frame_filename     = "media/videoframe.png"
    (
        ffmpeg.input(video_source_filename, ss="00:00:01")
        .output(temp_frame_filename, vframes=1)
        .run()
    )
    videoframe = PIL.Image.open(temp_frame_filename)
    s = videoframe.size
    videoframe = ""
    os.remove(temp_frame_filename)
    return s

# burn captions onto video file
def burn_overlays(include_qrcode=True):
    # audio_stream = ffmpeg.input(video_source_filename).audio # Uncomment if video already has audio
    audio_stream = ffmpeg.input(audio_output_filename).audio # Use this if the audio file is separate
    video_stream = ffmpeg.input(video_source_filename).video.filter('subtitles',captions_output)

    if include_qrcode:
        qr_w, qr_h = PIL.Image.open(qrcode_filename).size
        vid_w, vid_h = get_video_size()
        padding = 50 # to avoid being cutoff on the TV border 
        video_qrcode_layer = ffmpeg.input(qrcode_filename)      
        overlaid_QRcode = ffmpeg.overlay(video_stream,video_qrcode_layer, x=vid_w-qr_w-padding, y=padding)
        output_final = ffmpeg.output(overlaid_QRcode, audio_stream, video_with_subs_filename)
        output_final.overwrite_output().run()

    else:
        output_final = ffmpeg.output(video_stream, audio_stream, video_with_subs_filename)
        output_final.overwrite_output().run()

if len(sys.argv)>2:
    filename_no_ext = sys.argv[1]
    match sys.argv[2]:
        case "audio":
            extract_audio()
        case "captions":
            generate_captions()
        case "burn":
            burn_overlays()
else: 
    print("Error, missing file prefix or command. e.g. python scidvid.py arttherapy [audio|captions|burn]" )


