import sys
from math import floor
from subprocess import call

FFMPEG_PATH = "D:\\Alpha\\Port\\ffmpeg-audacity\\ffmpeg.exe"

def ffmpegRun(flags):
    argList = []
    [ argList.extend([k,v]) for k,v in flags.items() ]
    print("ffmpeg " + " ".join(argList))
    call([FFMPEG_PATH] + argList)

def setInput(flags, f):
    flags["-i"] = f
    return flags

def setStartTime(flags, time):
    flags["-ss"] = time
    return flags

def setDuration(flags, time):
    flags["-t"] = time
    return flags

def setOutputName(flags, name):
    flags["-sn"] = name
    return flags

def setCodecs(flags, audio, video):
    flags["-vcodec"] = video
    flags["-acodec"] = audio
    return flags

def timefmt(mils):
    secs = floor(mils/1000)
    return str(secs) + "." + str(mils%1000)

def makeTrims(f, i, fr, to):
    duration = to - fr
    timeFrom = timefmt(fr)
    timeDuration = timefmt(duration)
    flags = {}
    setInput(flags, f)
    setCodecs(flags, "libvo_aacenc", "copy")
    setStartTime(flags, timeFrom)
    setDuration(flags, timeDuration)
    setOutputName(flags, makeName(f, "cut-" + str(i)))
    ffmpegRun(flags)


def trimEnd(f, fr):
    flags = {}
    setInput(flags, f)
    setCodecs(flags, "libvo_aacenc", "copy")
    setStartTime(flags, timefmt(fr))
    setOutputName(flags, makeName(f, "cutent"))
    ffmpegRun(flags)

def makeName(f, ins):
    fs = f.split(".")
    fs.insert(-1, ins)
    return ".".join(fs)

if __name__ == "__main__":
    times = [0]
    lines = sys.stdin.readlines()
    inFile = sys.argv[1]
    print("Input = " + inFile)
    times = times + lines
    times = list(map(lambda x: int(float(x)), times))

    timePairs = zip(times, times[1:])
    for ii,pp in enumerate(timePairs):
        fr = pp[0]
        to = pp[1]
        makeTrims(inFile, ii, fr, to)
    trimEnd(inFile, times[-1])