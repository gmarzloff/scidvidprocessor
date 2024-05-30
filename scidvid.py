import assemblyai as aai
import ffmpeg

filename_no_ext         = "keypeele"
key_filename            = "private/assemblyai.key"
video_source_filename   = "media/" + filename_no_ext + ".mp4"
audio_output_filename   = "media/" + filename_no_ext + "_audio.mp3"
captions_output         = "media/" + filename_no_ext + "_captions.srt"
video_with_subs_filename= "media/" + filename_no_ext + "_withsubs.mp4"
qrcode_filename         = "media/QRcode_youtube.png"

"""
# extract audio content to new file
(
    ffmpeg
    .input(video_source_filename)
    .output(audio_output_filename)
    .run()
)

# upload audio to AssemblyAI and save captions to .srt
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
"""

# QR Code setup proper dimensions
# TODO

# burn captions onto video file
video_qrcode_layer = ffmpeg.input(qrcode_filename)
video_stream = ffmpeg.input(video_source_filename).video.filter('subtitles',captions_output)
overlaid_QRcode = ffmpeg.overlay(video_stream,video_qrcode_layer, x=1620, y=0)
audio_stream = ffmpeg.input(video_source_filename).audio

output_final = ffmpeg.output(overlaid_QRcode, audio_stream, video_with_subs_filename)
output_final.overwrite_output().run()
