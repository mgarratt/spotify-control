# spotify-control

Originally written as Bash script, this has now been converted to Python. This
script makes all methods and properties available from Spotify via DBus easily
accessible

## Installation

Clone this repository and ensure that `spotify-control` is executable.

Requires python3.

## Usage

```
usage: spotify-control [options] [command] [args ...]

A script to control Spotify from the command line, requires Spotify to be
running. Use spotify-control -h to print usage.

positional arguments:
  command         The command to give to Spotify
  args            Argument sto pass with the Spotify command

optional arguments:
  -h, --help      show this help message and exit
  --version       show program's version number and exit
  --verbose, -v   increase log level
  --quiet, -q     decrease log level
  --logfile file  log to file instead of <stderr>

Use spotify-control print_commands for all available commands

```

## Caveat

Not all properties / methods available have been implemented by Spotify. See
[this post](https://community.spotify.com/t5/Desktop-Linux-Windows-Web-Player/Cannot-control-volume-using-MPRIS-D-bus/m-p/1465152/highlight/true#M167907)
on the Spotify Community
