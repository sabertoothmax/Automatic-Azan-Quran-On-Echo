# Automatic-Azan-Quran-On-Echo

This code is a more customizable alternative to an Alexa Skill or Google Home App. 

It is used to play Azan and Quran automatically at the correct times on Amazon Echo, Google Home or other wireless speaker over bluetooth.

This code requires a Raspberry Pi or similar single-board computer (SBC) to run on. The current implementation is tested to work on Raspberry Pi. 

You may also need dongles for bluetooth and wifi, in case your version of the SBC does not already have these modules. 

Total cost for hardware is roughly $65 [$40 for Echo + $25 for Pi]. If you buy these on e-Bay, you may be able to get everything for under $40.

The code allows one to connect to a wireless speaker over bluetooth and stream azan and quran from multiple artists. 

More specifically, code does the following:

1. Connects speaker to Raspberry Pi via bluetooth
2. Finds prayer times based on the specified zip code and country location (using an API call to islamicfinder.us)
3. Automatically plays Azan followed by Darood-e-Sharif and Dua After Azan five times a day: Fajr, Dhuhr, Asr, Maghrib and Isha
4. At sunrise, plays Surah Fatihah followed by Surah Baqrah or Yaseen (randomly chosen each day)
5. Fajr Azan and Surah's at sunrise are played at slightly lower volume than normal
6. Every day, an hour before Dhuhr, plays one of Surah Naba or Waqiah (randomly chosen)
7. Every day, half-an-hour after Maghrib, plays Atay-al-Kursi and one of Surah Mulk or Rahman (randomly chosen)
8. Every Friday, plays Darood-e-Sharif, Surah Kahf, and one of Surah Ala, Jumuah or Qaf (randomly chosen)
9. You can control length of each surah by placing shorter duration mp3 files in the directories
10. You can add recitations from multiple artists to the same directory. One of the files will be chosen at random and played each time
11. Automatically reconnects and continues playing everytime the speaker gets disconnected or the Raspberry Pi runs into issues.

You can customize it further if you want. Please feel free to contribute. 

This is a needed functionality for many families. If you like this project, please share it widely among your frieds and communities.

Below are set up and running instructions. Run the following commands in a linux terminal (Notes are added as a guideline):

Step 1: Install relevant libraries
-------------------------------------------------
sudo pip3 install os subprocess requests random

sudo pip3 install sh datetime signal time
 
sudo apt install mplayer alsa-utils

Step 2: Test for sound
-------------------------------------------------
sudo modprobe snd-bcm2835  [Note: loads the sound driver]

sudo lsmod | grep 2835     [Note: check if driver is loaded]
 
aplay /usr/share/sounds/alsa/Front_Center.wav  [Note: play test sound]

Step 3: Install pulse audio and bluetooth tools
-------------------------------------------------
sudo apt install blueman

sudo apt install pulseaudio

sudo apt install pavucontrol paprefs

Step 4: Connect to speaker over bluetooth
-------------------------------------------------
Place speaker in discovery mode by:

saying "Alexa turn on bluetooth discovery" or from the App settings

Enter the following commands on a terminal (terminal prompt will change to bluetoothctl after the first command):

bluetoothctl

list                  [Note: to see list of your adapters]

select ADAPTERMAC     [Note: select default adapter]
 
scan on               [Note: start scanning]

pair SPEAKERMAC       [Note: pair with speaker]
 
trust SPEAKERMAC      [Note: trust speaker]
 
connect SPEAKERMAC    [Note: connect to speake; this may fail but ignore errors and restart the raspberry pi]

Use blueman GUI or volume control GUI to verify if the bluetooth device is connected nd audio is routed to it correctly.

Once connected, go to a different terminal and try

mplayer /usr/share/sounds/alsa/Front_Center.wav  [Note: run some test file and make sure it is playing through speaker]

aplay /usr/share/sounds/alsa/Front_Center.wav [Note: Test installation. Front_Center.wav is an existing file; no need to provide a new mp3 file]

Create a file called /etc/machine-info and add write in it:

PRETTY_HOSTNAME=adapter1 [Note: adapter1 is just a name that you can pick in place of the default bluetooth device name in bluetoothctl. You can write name here]

Step 5: Configure audio connections
-------------------------------------------------
sudo nano /boot/config.txt

Comment out the following line in config.txt by adding a # before the statement (optional to turn off default audio device). As in, change the following line

dtparam=audio=on

to the following:

#dtparam=audio=on

Tell the default bluetooth service to not load the module. To do this, edit /etc/pulse/default.pa and comment out these lines by putting # characters in front of them:

 #.ifexists module-bluetooth-discover.so
 
 #load-module module-bluetooth-discover
 
 #.endif

Configure the bluetooth module to be loaded after X11. To do this, edit /usr/bin/start-pulseaudio-x11 and add two lines:

  if [ x"$DISPLAY" != x ] ; then
  
  ...
  
  <Add these lines below>:
 
  /usr/bin/pactl load-module module-bluetooth-discover
  
  /usr/bin/pactl load-module module-switch-on-connect
  
  fi

Restart pulseaudio and bluetooth by either rebooting the Raspberry Pi or using the following commands:

pulseaudio -k

start-pulseaudio-x11

sudo service bluetooth restart

Go to a different terminal and try

mplayer /usr/share/sounds/alsa/Front_Center.wav  [Note: run some test file and make sure it is playing through speaker]

aplay /usr/share/sounds/alsa/Front_Center.wav [Note: Test installation. Front_Center.wav is an existing file; no need to provide a new mp3 file]

Step 6: Set up autorun and auto restarts
-------------------------------------------------
To autorun script on raspberrry pi startup make quranMedia.py to be executable by typing the following on a terminal:

chmod +x quranMedia.py
 
Create an autostart file and update it by typing the following commands in a terminal:

mkdir ~/.config/lxsessions/LXDE

cp /etc/xdg/lxsession/LXDE/autostart ~/.config/lxsession/LXDE/autostart

sudo nano ~/.config/lxsession/LXDE/autostart

Add a line at the end of this file as follows:

@lxterminal --command="full-path-to-quranMedia.py"

Below are the example contents of autostart file

@lxpanel --profile LXDE

@pcmanfm --desktop --profile LXDE

@xscreensaver -no-splash

@lxterminal --command="/home/pi/Documents/quranMedia/quranMedia.py"     [Note: add this line]

Step 7: Add media - Azan and Quran files
-------------------------------------------------

Go to Youtube, search for relevant azan and quran videos. Convert them to MP3 using something like: https://www.easymp3converter.com/. 

Cut the audio files to the desired recitation duration using something like https://mp3cut.net/

Fix gains of all audio files in directory using something like: http://mp3gain.sourceforge.net/

Adjusting gain will ensure that all files play with same volume level

Put the corrected-mp3 files in corresponding directories at PATH Where PATH is the structure provided in the azan and quran directories

Step 8: Update code quranMedia.py
-------------------------------------------------

Make the following changes in main:

line 192: Delay time between different steps. It is set to 3 seconds by default. You can increase it in case you run into errors but don't use anything less than 3.

line 193: Update the MAC addresses of your speaker devices

line 196: Update the country and zip code for which you want to find prayer times

Make the following changes in the selectMedia function:

line 176: Update path of the media files. As in, change /media/pi/Data to the full path of the location where the mp3 files are located on your Raspberry Pi. You could place it on a USB drive that is plugged in to the Raspberry Pi.
