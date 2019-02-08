from queue import LifoQueue as Queue
from threading import Thread
import cv2
import sys
from uuid import uuid4 as uuid
from time import time

# timeout for all threading queue operations
TIMEOUT=10
# shared state indicating if the video file processing has been finalised
TASK_DONE = False

# take a pair (frameIndex, frame) and return the index if the marker is found else None
def processTuple(t):
    i, frame = t
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    b,_ = cv2.findChessboardCorners(gray, (4,5), None)
    if b:
        return i
    else:
        return None

# function to run the threads which consume frames to generate a list of frame indexes
def consumerThread(q, to):
    while not (TASK_DONE and q.empty()):
        t = q.get(block=True, timeout=TIMEOUT)
        # res = frame index | None
        res = processTuple(t)
        # if we found something in the frame, put it in the queue
        if res is not None:
            to.put(res, block=True, timeout=TIMEOUT)
        
# function to run the thread which produces frames to be consumed
def frameProducer(to, cap, step=1):
    frameIndex = 0
    # jump to start of video
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
    b,frame = cap.read()
    # while we are reading valid frames
    while b:
        # put the frame to a queue
        to.put((frameIndex, frame), block=True, timeout=TIMEOUT)
        frameIndex += step
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
        b,frame = cap.read()

def getArgOrNone(i):
    value = None
    try:
        value = sys.argv[i]
    except:
        pass
    return value

if __name__ == "__main__":
    inFile = sys.argv[1]
    # read argument for threads count, else 4
    threadCount = int(getArgOrNone(2) or 4)
    # bounded frames queue so that we don't flood RAM
    frames = Queue(maxsize=50)
    # output queue is not bounded
    out = Queue()
    # open the input file as an OpenCV video capture
    cap = cv2.VideoCapture(inFile)
    # initialise and start consumer threads
    threads = [Thread(group=None, target=consumerThread,args=(frames, out)) for t in range(threadCount)]
    for t in threads:
        t.start()
    # get time for logging
    start = time()
    # run the producer to give consumers something to do
    frameProducer(frames, cap, 20)
    # once we are done producing, flag this and wait for consumers to finish
    TASK_DONE = True
    for t in threads:
        t.join()
    # now write our frame indexes as millisecond times to stdout
    while not out.empty():
        frameIndex = out.get()
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
        timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        print(timeStamp)
    # mark end
    end = time()
    runId = uuid()[:8]
    # write log to unique-id file
    with f as open("processing.{}.log".format(runId), "w"):
        f.write("Finised execution processing {} with {} threads\n\n".format(inFile, threadCount))
        # log time taken for housekeeping
        f.write("Time elapsed: {}\n".format(str(end - start)))


