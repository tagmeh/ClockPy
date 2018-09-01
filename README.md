PyClock  
Python Alarm Clock using Kivy UIX

====================

Requirements: Raspian Stretch, python(seems to work in 2 & 3), Kivy 1.10.1, pygame, py532lib  
https://www.raspberrypi.org/downloads/  
https://kivy.org/doc/stable/gettingstarted/installation.html  
https://www.pygame.org/wiki/GettingStarted  
https://github.com/HubCityLabs/py532lib


***My Personal Character UID Values***  
// Folder 1 = Captain America 	- x01\x01\x00D\x00\x07\x04>   
-- SigByte -                    - X04>    
// Folder 2 = Hulk 				- x01\x01\x00D\x00\x07\x04H  
-- SigByte -					- x04H   
// Folder 3 = Ultron 			- x01\x01\x00D\x00\x07\x04C  
-- SigByte -					- x04C  
// Folder 4 = Baloo 			- x01\x01\x00D\x00\x07\x043  
-- SigByte -				    - x043  
// Folder 5 = Zeb Orrelios  	-   
-- SigByte -					-   
// Folder 6 = Green Goblin 		- x01\x01\x00D\x00\x07\x04(  
-- SigByte -					- x04(   



--Credits to dwalker0044 for the python/kivy base clock that got me started.
https://github.com/dwalker0044/KivyDigitalClock

-- Credits to Marvel Heroes for the OGG sound files. (can someone check the legality on this for me? :/ It's a free game, and the files are readily available in the DL. 
I guess if this is an issue I'll just say to download the game and get the files yourself if you want those specific characters.)

-- Credits to Soundbible for default alarm sounds - http://soundbible.com/tags-alarm-clock.html





***################### TO ENABLE RASPBIAN STRETH TO WORK WITH MY SCREEN #################***
https://www.amazon.com/gp/product/B07FDYXPT7/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1  
-- Add following 8 lines at the end of the file /both/config.txt in raspberry pi:   
max_usb_current=1  
hdmi_force_hotplug=1  
config_hdmi_boost=7  
hdmi_group=2  
hdmi_mode=1  
hdmi_mode=87  
hdmi_drive=1  
hdmi_cvt 1024 600 60 6 0 0 0  

***################### TO ENABLE TOUCH IN KIVY #################***

Do this over SSH. It's way easier than typing in Raspbian CLI  
kivy installs at /usr/local/lib/python2.7/dist-packages/kivy  
Follow guide at https://github.com/mrichardson23/rpi-kivy-screen   
or http://mattrichardson.com/kivy-gpio-raspberry-pi-touch/index.html if you prefer white on black


sudo rm -rf LCD-show  
sudo git clone https://github.com/goodtft/LCD-show.git  
sudo chmod -R 755 LCD-show  
cd LCD-show/  
sudo ./MPI5001-show

If touchscreen doesn't work right away. Be sure to use a USB cable that supports data, and try different USB ports.

***################### TO FORCE PI AUDIO OUT OF 3.5MM PORT WHILE USING HDMI #################***  
https://raspberrypi.stackexchange.com/questions/68127/how-to-change-audio-output-device-for-python  
1) Get a list of your sound cards using  
``` python   
aplay -l  
```   
2) Create/edit the system-wide alsa configuration file at /etc/asound.conf, e.g. with sudo nano /etc/asound.conf  
3) Into this file, paste   
```python   
pcm.!default {  
    type hw  
    card 0  
}  

ctl.!default {
    type hw           
    card 0
}
```