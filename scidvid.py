import assemblyai as aai
import ffmpeg
import PIL 
from PIL import Image
import os
import sys

key_filename = "private/assemblyai.key"

class Video:
    def __init__(self, _filename_base="") -> None:
        self.update_filenames(_filename_base)
    
    def update_filenames(self, _newbase:str = ""):
        self.filename_base           = _newbase
        self.media_folder                 = "media/"
        self.video_source_filename   = self.media_folder + _newbase + "/" + _newbase + ".mp4"
        self.audio_output_filename   = self.media_folder + _newbase + "/" + _newbase + "_audio.m4a"
        self.captions_output         = self.media_folder + _newbase + "/" + _newbase + "_captions.srt"
        self.video_with_subs_filename= self.media_folder + _newbase + "/" + _newbase + "_withsubs.mp4"
        self.qrcode_filename         = self.media_folder + _newbase + "/" + _newbase + "_qrcode.png"

    # download youtube file (this one requires audio and video separately)
    # https://ytdl.hamsterlabs.de/

    # QR Code generator 
    # https://www.the-qrcode-generator.com/

    def extract_audio(self):
        print("\nExtracting Audio\n")
        (
            ffmpeg
            .input(self.video_source_filename)
            .output(self.audio_output_filename)
            .run()
        )

    def generate_captions(self):
        # upload audio to AssemblyAI and save captions to .srt
        print("Note: the VA proxy blocks using SSL to interact with AssemblyAI. \n \
            Switch to a wifi hotspot to work with the API.")
        
        keyfile = open(key_filename, "r")
        aai.settings.api_key = keyfile.readlines()[0].strip('\n')
        keyfile.close()

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(self.audio_output_filename)

        srt_content = transcript.export_subtitles_srt()
        srtfile = open(self.captions_output, "w")
        srtfile.write(srt_content)
        srtfile.close()
        print("srt saved at " + self.captions_output)

    # burn captions onto video file
    def burn_overlays(self, include_qrcode=True):
        print("\nBurning mp4 file using video, audio, and QR code layers.\n")
        # audio_stream = ffmpeg.input(video_source_filename).audio # Uncomment if video already has audio
        audio_stream = ffmpeg.input(self.audio_output_filename).audio # Use this if the audio file is separate
        video_stream = ffmpeg.input(self.video_source_filename).video.filter('subtitles',self.captions_output)

        if include_qrcode:
            qr_w, qr_h = PIL.Image.open(video.qrcode_filename).size
            vid_w, vid_h = self.get_video_size()
            padding = 50 # to avoid being cutoff on the TV border 
            video_qrcode_layer = ffmpeg.input(self.qrcode_filename)      
            overlaid_QRcode = ffmpeg.overlay(video_stream,video_qrcode_layer, x=vid_w-qr_w-padding, y=padding)
            output_final = ffmpeg.output(overlaid_QRcode, audio_stream, self.video_with_subs_filename)
            output_final.overwrite_output().run()

        else:
            output_final = ffmpeg.output(video_stream, audio_stream, self.video_with_subs_filename)
            output_final.overwrite_output().run()

        
    def get_video_size(self):
        # can simplify this with ffprobe, todo later
        temp_frame_filename     =  self.media_folder + self.filename_base + "/" + "videoframe.png"
        (
            ffmpeg.input(self.video_source_filename, ss="00:00:01")
            .output(temp_frame_filename, vframes=1, update='true')
            .run()
        )
        videoframe = PIL.Image.open(temp_frame_filename)
        s = videoframe.size
        videoframe = ""
        os.remove(temp_frame_filename)
        return s

   
    
if len(sys.argv)>2:
    video = Video(sys.argv[1])

    match sys.argv[2]:
        case "audio":
            video.extract_audio()
        case "captions":
            video.generate_captions()
        case "burn":
            video.burn_overlays()

else: 
    print("Error, missing file prefix or command. e.g. python scidvid.py arttherapy [audio|captions|burn]" )


