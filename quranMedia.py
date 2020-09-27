#!/usr/bin/python3

import os, subprocess, signal, time, requests, random
from sh import bluetoothctl
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta

def quranMedia(apiParams, devMap, stepDelay):

    while True:
        print('\n#########################################')
        print('Bismillah hir rahman nir rahim')
        print('#########################################\n')

        weekDay = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

        connectAgent(stepDelay, devMap['echo'])  # Reset adapter and connect speaker device to bluetooth agent
        prayerTimes  = getPrayerTimes(apiParams) # Fajr, Sunrise, beforeDhuhr, Dhuhr, Asr, Maghrib, afterMaghrib, Isha

        for day in range(2): # Play at the same timings for 2 days
            for prayerNumber, prayerTime in enumerate(prayerTimes):
                remainingTime  = getTimeUntilNextPrayer(datetime.now(), prayerTime)
                if remainingTime > 0:
                    print('...........................................')
                    print('Prayer number : ' + str(prayerNumber))
                    print('\nWaiting for time ' + str(prayerTime))
                    print('Remaining time ' + str(remainingTime) + ' seconds...')
                    time.sleep(remainingTime-10) # sleep until 10 seconds before next prayer time

                    alertFile = selectMedia(name='CountDown')
                    playMedia(alertFile)

                    if prayerNumber in [0,3,4,5,7]: # Play Azan five times a day
                        playAzan(prayerNumber)
                        print('******* Finished playing Azan.\n')
                        time.sleep(stepDelay)

                    if prayerNumber == 1: # Surah Fatihah, Yaseen and Baqrah after Fajr
                        for surah in ['Fatihah'] + [random.choice(['Yaseen','Baqrah'])]:
                            surahFile = selectMedia(name=surah)
                            playMedia(surahFile, playVolume=90)
                            print('******* Finished playing Surah ' + surah + '\n')
                            time.sleep(stepDelay)

                    if prayerNumber == 2:
                        dayOfWeek = datetime.today().weekday() # 4 means Friday
                        if dayOfWeek == 4: # Surah Ala, Jumuah and Kahf before Friday Dhuhr
                            for surah in ['Darood'] + [random.choice(['Ala','Jumuah','Qaf'])] + ['Kahf']:
                                surahFile = selectMedia(name=surah)
                                playMedia(surahFile)
                                print('******* Finished playing Surah ' + surah + '\n')
                                time.sleep(stepDelay)

                        else: # Surah Waqiah and Naba before regular Dhuhr
                             for surah in [random.choice(['Naba','Waqiah'])]:
                                surahFile = selectMedia(name=surah)
                                playMedia(surahFile)
                                print('******* Finished playing Surah ' + surah + '\n')
                                time.sleep(stepDelay)

                    if prayerNumber == 6: # Surah Mulk, Rahman and Ayat-al-Kursi after Maghrib
                        for surah in [random.choice(['Mulk','Rahman'])] + ['Ayat-al-Kursi']:
                            surahFile = selectMedia(name=surah)
                            playMedia(surahFile)
                            print('******* Finished playing Surah ' + surah + '\n')
                            time.sleep(stepDelay)

            print('//////////////////////////////////////////')
            print('Finished quranMedia for ' + weekDay[dayOfWeek])
            print('//////////////////////////////////////////\n')

            prayerTimes = [t + timedelta(days=1) for t in prayerTimes] # Increment prayerTimes date

def playAzan(prayerNumber):
    if prayerNumber == 0:
        azanFile = selectMedia(type='azan',name='fajrAzan') # Select Azan file
        playMedia(azanFile, playVolume=90)
    else:
        azanFile = selectMedia(type='azan',name='regularAzan')
        playMedia(azanFile)
    daroodAfterAzan = selectMedia(name='Darood')
    playMedia(daroodAfterAzan, playVolume=90)
    duaAfterAzan = selectMedia(type='azan',name='duaAfterAzan')
    playMedia(duaAfterAzan, playVolume=90)
    duaAfterAzanTranslation = selectMedia(type='azan',name='duaAfterAzanTranslation')
    playMedia(duaAfterAzanTranslation, playVolume=90)

def connectAgent(stepDelay, devMac):
    connectionState = False
    print('Resetting adapter')
    resetAdapter(stepDelay)
    print('Connecting to speaker...')
    connectDevice(None, devMac, stepDelay)
    connectionState = checkConnectionState(devMac)
    print('Connection State: ' + str(connectionState))
    # If not able to connect, keep trying until a connection is established
    while not connectionState:
        print('Trying again')
        connectDevice(None, devMac, stepDelay)
        connectionState = checkConnectionState(devMac)
        print('Connection state: ' + str(connectionState))
        if connectionState: # Reset adapter and connect again
            print('Trying one last time')
            resetAdapter(stepDelay)
            connectDevice(None, devMac, stepDelay)
            connectionState = checkConnectionState(devMac)
            print('Connection state: ' + str(connectionState))
    print('Successfully connected to speaker\n')

def checkConnectionState(devMac):
    connectionInfo  = bluetoothctl('info',devMac)
    connectionState = False if str(connectionInfo.stdout).split('Connected:')[1].split('\\n')[0].strip() == 'no' else True
    return connectionState

def getTimeUntilNextPrayer(time1, time2):
    duration = time2 - time1
    return int(duration.total_seconds())

def getPrayerTimes(apiParams):
    apiURL = 'http://www.islamicfinder.us/index.php/api/prayer_times'
    response = requests.get(apiURL, params=apiParams)
    if response.status_code == 200:
       prayerTimes = list(response.json()['results'].values())
    else:
        prayerTimes = ['5:34 %am%', '6:49 %am%', '12:50 %pm%', '4:14 %pm%', '6:51 %pm%', '8:30 %pm%']
        #prayerTimes = readFromFile

    prayerTimes24HourFormat = convertTo24HrFormat(prayerTimes) # has 6 vals: Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha
    beforeDhuhr  = prayerTimes24HourFormat[2] - timedelta(minutes=60) # 60 min before Dhuhr
    afterMaghrib = prayerTimes24HourFormat[4] + timedelta(minutes=30) # 30 min after Maghrib
    prayerTimes24HourFormat = prayerTimes24HourFormat[:2] + [beforeDhuhr] + prayerTimes24HourFormat[2:5] + [afterMaghrib] + [prayerTimes24HourFormat[5]]

    return prayerTimes24HourFormat

def convertTo24HrFormat(prayerTimes):
    prayerTimes24HourFormat = list()
    dateString = datetime.now().strftime('%d/%m/%y')

    for pTime in prayerTimes:
        timeString    = pTime.split(' ')[0]
        hourString    = timeString.split(':')[0]
        minutesString = timeString.split(':')[1]
        ampm          = pTime[-3:-1]

        if ampm == 'pm': # convert timeString to 24-hour format
            if hourString != '12':
                timeString = str(int(hourString)+12)+':'+minutesString
        else:
            if hourString == '12':
                timeString = '0'+':'+minutesString

        dateTimeString = dateString + ' ' + timeString
        prayerTimes24HourFormat.append(datetime.strptime(dateTimeString,'%d/%m/%y %H:%M'))
    return prayerTimes24HourFormat

def connectDevice(prevMAC, newMAC, stepDelay):
    if prevMAC is not None:
        bluetoothctl('disconnect', prevMAC)
        time.sleep(2*stepDelay)
    bluetoothctl('connect', newMAC)
    time.sleep(2*stepDelay)

def playMedia(mediaFile, playVolume=100, playTime=-1, block=True):
    p = subprocess.Popen(['mplayer', mediaFile, '-volume', str(playVolume)], shell=False)
    if playTime > 0:
        pid = p.pid
        time.sleep(playTime)
        os.kill(pid, signal.SIGINT)
        while p.poll():
            pass
    if block:
       p.communicate()

def selectMedia(type='quran',name='Fatihah'):
    mediaRoot  = '/media/pi/Data/' + type + '/'
    mediaDir   = mediaRoot + name
    mediaFiles = [f for f in listdir(mediaDir) if isfile(join(mediaDir, f))]
    mediaFile  = random.choice(mediaFiles)
    return join(mediaDir, mediaFile)

def resetAdapter(stepDelay):
    for i in range(2): # Reset two times to be sure
        os.system('pulseaudio -k')
        os.system('pulseaudio --start')
        os.system('start-pulseaudio-x11')
        time.sleep(stepDelay)
    os.system('sudo service bluetooth restart')
    time.sleep(stepDelay)

if __name__ == '__main__':
    stepDelay = 3 # seconds
    devMap = {'home' : 'D4:F5:47:CF:65:CB',
              'echo' : '74:58:F3:46:00:B4'}

    apiParams = {'country': 'US', 'zipcode' : '98052'}
    quranMedia(apiParams, devMap, stepDelay)

# Install relevant libraries as follows:
# sudo pip3 install os subprocess signal time requests random
# sudo pip3 install sh datetime
# 
# sudo apt install mplayer
# sudo apt install alsa-utils
# sudo modprobe snd-bcm2835 --> load sound driver
# sudo lsmod | grep 2835 --> check if driver is loaded
# 
# aplay /usr/share/sounds/alsa/Front_Center.wav --> test installation
#
# sudo nano /boot/config.txt
# comment out the following line:
# dtparam=audio=on --> optional, to turn off default audio
#
# sudo apt install blueman
# sudo apt install pulseaudio
# sudo apt install pavucontrol paprefs
#
# Place speaker in discovery mode:
# say "Alexa turn on bluetooth discovery" or from App
# 
# Connect to bluetooth and verify that it works:
# bluetoothctl 
# list --> to see list of your adapters
# select ADAPTERMAC --> select default adapter
# scan on --> start scanning
# pair SPEAKERMAC --> pair with speaker
# trust SPEAKERMAC --> trust speaker
# connect SPEAKERMAC --> connect to speaker (this may fail but ignore errors)
#
# Use blueman or volume control to verify if the bluetooth device is connected
# and audio is routed to it correctly.
#
# Once connected, go to a different terminal and try
# mplayer test.mp3 --> run test file and make sure it is playing through speaker or
# aplay /usr/share/sounds/alsa/Front_Center.wav --> test installation
#
# Tell the default bluetooth service to not load the module. 
# To do this, edit /etc/pulse/default.pa and comment out these 
# lines by putting # characters in front of them:
#
# .ifexists module-bluetooth-discover.so
# load-module module-bluetooth-discover
# .endif
#
# Configure the module to be loaded after X11. To do this, 
# edit /usr/bin/start-pulseaudio-x11
# and add two lines:
#
# if [ x"$DISPLAY" != x ] ; then
    # ...

    # Add these lines:
#    /usr/bin/pactl load-module module-bluetooth-discover
#    /usr/bin/pactl load-module module-switch-on-connect
# fi
#
# Restart pulseaudio and bluetooth.
# Either reboot your machine or use the following commands:
#
# pulseaudio -k
# start-pulseaudio-x11
# sudo service bluetooth restart
#
# go to a different terminal and try
# mplayer test.mp3 --> run test file and make sure it is playing through speaker or
# aplay /usr/share/sounds/alsa/Front_Center.wav --> test installation
#
# Create a file called /etc/machine-info and add write in it:
# PRETTY_HOSTNAME=adapter1
#
# To autorun script on raspberrry pi startup
#
# Make quranMedia.py as an executable
#
# For example,
# chmod +x /home/pi/Documents/quranMedia/quranMedia.py
# 
# mkdir ~/.config/lxsessions/LXDE
# cp /etc/xdg/lxsession/LXDE/autostart ~/.config/lxsession/LXDE/autostart
# sudo nano ~/.config/lxsession/LXDE/autostart
#
# add a line at the end of this file as follows:
#
# @lxterminal --command="full-path-to-quranMedia.py"
#
# For example, 
#
# @lxpanel --profile LXDE
# @pcmanfm --desktop --profile LXDE
# @xscreensaver -no-splash
# @lxterminal --command="/home/pi/Documents/quranMedia/quranMedia.py" --> add this line
#
# Go to Youtube, search for azan and quran videos. Convert them to MP3 using 
# something like: https://www.easymp3converter.com/. Fix gains of all 
# audio files in directory using something like: http://mp3gain.sourceforge.net/
# Adjusting gain will ensure that all files play with same volume level
#
# Put the fixed-mp3 files in corresponding directories at /media/pi/Data/PATH
# Where PATH is the structure provided in the download
# 
