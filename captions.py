# `pip install assemblyai` (Windows)

import assemblyai as aai

class Captioner:

    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.audiofile = ""
        self.transcript_text = ""
        aai.settings.api_key = open("private/assemblyai.key", "r").readlines()[0].close()

    def extract_audio(self, audio_file):
        print("Extracting Audio")
        self.inputfile
        self.audiofile = audio_file


    def generate_captions(self, outputfile):   
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(self)
        # transcript = transcriber.transcribe("./my-local-audio-file.wav")
        self.transcript_text = transcript.text
        
        outputfile
        return transcript.text