#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# Console client for AbletonOSC.
# Takes OSC commands and parameters, and prints the return value.
#--------------------------------------------------------------------------------

import re
import sys
import argparse

try:
    import readline
except:
    if sys.platform == "win32":
        print("On Windows, run-console.py requires pyreadline3: pip install pyreadline3")
    else:
        raise

from client import AbletonOSCClient

class LiveAPICompleter:
    def __init__(self, commands):
        self.commands = commands

    def complete(self, text, state):
        results =  [x for x in self.commands if x.startswith(text)] + [None]
        return results[state]

MACROS = ["MUTE_ALL"]
words = ["live", "song", "track", "clip", "device", "parameter", "parameters"]
completer = LiveAPICompleter(words + MACROS)
readline.set_completer(completer.complete)


def _mute_all(client_, MUTE=1):

    # smoke test
    if not client_.query("/live/test"):
       raise Exception("Check Ableton Live is running")

    # yuck... one dimensional tuple
    num_of_tracks = client_.query("/live/song/get/num_tracks")[0]
    for track_id in range(int(num_of_tracks)):
        # MUTE = 1 to mute
        client_.send_message('/live/track/set/mute', [track_id, MUTE])
    if MUTE:
       print("Muted All Tracks")
    else:
       print("Unmuted All Tracks")

def main(args):
    client = AbletonOSCClient(args.hostname, args.port)
    if args.verbose:
        client.verbose = True
    client.send_message("/live/api/reload")

    readline.parse_and_bind('tab: complete')
    print("AbletonOSC command console")
    print("Usage: /live/osc/command [params]")

    while True:
        try:
            command_str = input(">>> ")
        except EOFError:
            print()
            break

        if command_str == "MUTE_ALL":
           _mute_all(client)
           continue
        if command_str == "UNMUTE_ALL":
           _mute_all(client, MUTE=0)
           continue

        command, *params_str = command_str.split(" ")
        params = []
        for part in params_str:
            try:
                part = int(part)
            except ValueError:
                try:
                    part = float(part)
                except ValueError:
                    pass
            params.append(part)
        try:
            print(client.query(command, params))
        except RuntimeError:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Console client for AbletonOSC. Takes OSC commands and parameters, and prints the return value.")
    parser.add_argument("--hostname", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=str, default=11000)
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode: prints all OSC messages")
    args = parser.parse_args()
    main(args)
