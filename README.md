# r2p2py

Installation
============

Required packages are listed in requirements.txt

```console
python3 -m pip install git+https://github.com/rhayman/r2p2py.git -U
```

Usage
=====

Once installed you can import into an IPython session like so:

```python
from r2p2py.logfile_parser import LogFileParser
fname = "/home/robin/Downloads/20220212-204627.txt"
logfile = LogFileParser(fname)
```

The above will load the file and process it so that there is one position for each timestamp (ie duplicates are removed). You can get hold of the position data like so:

```python
x = logfile.getX()
z = logfile.getZ()
theta = logfile.getTheta()
pos_times = logfile.getPosTimes()
```

You can also get a kind of summary of the data that might be more useful for working with by doing:

```python
df = logfile.make_dataframe()
```

This will return a pandas dataframe (see Caveats below).

Animation
=========

See point 3 in Caveats below first.

There is a script called animate_trial.py that will also get installed, but it's probably easiest to just copy that and save it somewhere easier to access. Once you've done that you need to make the script executable (on Linux anyway) like so:

```console
chmod +x animate_trial.py
```

The file can now be called from the command line and has a few options to play around with:

```console
python3 ./animate_trial.py --f "/home/robin/Downloads/20220212-204627.txt" --s 100 --length 30 --save
```

The above command includes all the options available. The only required one is the filename provided after the --f option. --s is the start time to start the animation from in seconds (defaults to 0), --length is the total amount of time (from the start time) to animate for (in trial time, default duration is 300 seconds), --save is if you want to save the result. It's best to not use this until you know what it is you want to save. If you provide the --save option (no arguments) the file is saved to disk as an mp4: in the above example, where the logfile is called:

```console
/home/robin/Downloads/20220212-204627.txt
```

the mp4 file will be called:

```console
/home/robin/Downloads/20220212-204627.mp4
```


Caveats
=======

1. theta is supposedly in degrees but the value for the rotary encoder units that make up one full revolution (called ROTARY_ENCODER_UNITS_PER_TURN in logfile_parser.py) is almost definitely wrong right now.

2. pos_times in the above example is in the format of a datetime (from python module datetime). This makes time math easier but can take a bit of getting used to. In the call to getPosTimes() above the resulting datetimes are 'raw' in that they reflect the values in the actual logfile. In contrast, for animating the results, I've used pandas (https://pandas.pydata.org/docs/index.html) to organise the data, and here the time data is zeroed so that the first time stamp is 0.

3. The animation stuff will require that ffmpeg is installed.