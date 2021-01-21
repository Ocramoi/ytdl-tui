#!/usr/bin/env python3

import curses
import sys

try:
    import youtube_dl
except ImportError:
    print("To use the downlaoder, first install `youtube_dl` (sudo pip3 install youtube_dl)")
    exit(1)


HELPER = f"Usage: {__file__} <YouTube video URL>"  # Usage string
V_OPS = ["360p", "480p", "HD", "FHD", "QHD", "4K"]  # Video quality options
A_OPS = ["Worst", "Best"]  # Audio quality options


def cleanupExit(exitCode: int) -> None:
    """ Exists code and ends curses window """
    curses.endwin()
    exit(exitCode)


def clamp(val: float, minimum: float, maximum: float) -> float:
    """ Clamps value to range """
    ret = max(minimum, val)
    ret = min(maximum, ret)
    return ret


def setupScr() -> "curses._CursesWindow":
    """ Creates and sets up curses window """
    scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    scr.keypad(True)
    curses.curs_set(0)
    return scr


def centerLine(line: str, scr: "curses._CurseWindow"):
    """ Print line centered """
    scr.addstr(("{:^%d}" % scr.getmaxyx()[1]).format(line))


def printOps(scr: "curses._CursesWindow",
             vUrl: str, ops: [int, int], curLine: int):
    """ Refresh screen based on current options """
    scr.erase()
    vQuality, aQuality = ops
    height, width = scr.getmaxyx()
    scr.addstr(width*"-", curses.A_BOLD)
    centerLine("Video URL: " + vUrl, scr)
    scr.addch("\n")

    scr.addstr("Video quality: ")
    for i in range(len(V_OPS)):
        if vQuality != i:
            scr.addstr(f"{V_OPS[i]}\t")
        elif curLine != 0:
            scr.addstr(f"{V_OPS[i]}\t", curses.A_BLINK)
        else:
            scr.addstr(f"{V_OPS[i]}", curses.A_STANDOUT)
            scr.addch("\t")
    scr.addch('\n')

    scr.addstr("Audio quality: ")
    for i in range(len(A_OPS)):
        if aQuality != i:
            scr.addstr(f"{A_OPS[i]}\t")
        elif curLine != 1:
            scr.addstr(f"{A_OPS[i]}\t", curses.A_BLINK)
        else:
            scr.addstr(f"{A_OPS[i]}", curses.A_STANDOUT)
            scr.addch("\t")
    scr.addch('\n')

    centerLine("Download [d/y] | Quit [q/n]", scr)
    scr.addstr(width*"-", curses.A_BOLD)
    scr.refresh()


def main():
    if (len(sys.argv) != 2):  # Requires video URL as only input
        print(HELPER)
        exit(1)
    videoUrl = sys.argv[1]
    scr = setupScr()
    cL = 0
    quts = [0, 0]
    printOps(scr, videoUrl, quts, cL)
    while True:  # Basic interface
        inp = scr.getch()

        maxLR = 0
        if (cL == 0):
            maxLR = len(V_OPS)
        else:
            maxLR = len(A_OPS)

        if (inp == curses.KEY_UP):
            cL = clamp(cL - 1, 0, 1)
        elif (inp == curses.KEY_DOWN):
            cL = clamp(cL + 1, 0, 1)
        elif (inp == curses.KEY_LEFT):
            quts[cL] = clamp(quts[cL] - 1, 0, maxLR)
        elif (inp == curses.KEY_RIGHT):
            quts[cL] = clamp(quts[cL] + 1, 0, maxLR)
        elif (inp == ord('q') or inp == ord('Q') or
              inp == ord('n') or inp == ord('N')):
            cleanupExit(0)
        elif (inp == ord('d') or inp == ord('D') or
              inp == ord('y') or inp == ord('Y')):
            break

        printOps(scr, videoUrl, quts, cL)

    # Format string with video and audio quality
    formatStr = "[height<="
    if (quts[0] == 0):
        formatStr += "480"
    elif (quts[0] == 1):
        formatStr += "720"
    elif (quts[0] == 2):
        formatStr += "1080"
    elif (quts[0] == 3):
        formatStr += "1440"
    elif (quts[0] == 4):
        formatStr += "4320"
    elif (quts[0] == 5):
        formatStr += "6480"
    formatStr += "]/bestvideo+"

    if (quts[1] == 0):
        formatStr += "worstaudio"
    else:
        formatStr += "bestaudio"

    curses.endwin()
    ydl_format = {  # ytdl option dict
        "format": formatStr,
        "merge-output-format": "mp4"
    }
    with youtube_dl.YoutubeDL(ydl_format) as ydl:  # Effectively downloads video
        ydl.download([videoUrl])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cleanupExit(1)
