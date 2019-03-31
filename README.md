PyClock  
Python Alarm Clock using Kivy UIX

====================

Requirements: Raspian Stretch, python(seems to work in 2 & 3),libNFC, Kivy 1.10.1, pygame      
https://www.raspberrypi.org/downloads/  
libnfc - http://nfc-tools.org/index.php/Libnfc    
I use [these modules](https://www.amazon.com/HiLetgo-Communication-Arduino-Raspberry-Android/dp/B01I1J17LC/ref=sr_1_1_sspa?keywords=pn532&qid=1554041310&s=gateway&sr=8-1-spons&psc=1)    
Helpful Tips - http://wiki.sunfounder.cc/index.php?title=PN532_NFC_Module_for_Raspberry_Pi    
https://kivy.org/doc/stable/gettingstarted/installation.html  
https://www.pygame.org/wiki/GettingStarted  



***My example directory***  
*** /home/pi/Desktop/PyClock/ ***

***Character UID Values Examples***  
// Folder 1 = Captain America 	- x01\x01\x00D\x00\x07\x04>   
-- SigByte -                    - X04>    
// Folder 2 = Hulk 				- x01\x01\x00D\x00\x07\x04H  
-- SigByte -					- x04H   
// Folder 3 = Ultron 			- x01\x01\x00D\x00\x07\x04C (No Audio Files Yet)  
-- SigByte -					- x04C  
// Folder 4 = Baloo 			- x01\x01\x00D\x00\x07\x043 (No Audio Files Yet)  
-- SigByte -				    - x043  
// Folder 5 = Zeb Orrelios  	-   
-- SigByte -					-   
// Folder 6 = Green Goblin 		- x01\x01\x00D\x00\x07\x04(  (No Audio Files Yet)  
-- SigByte -					- x04(   




--Credits to dwalker0044 for the python/kivy base clock that got me started.
https://github.com/dwalker0044/KivyDigitalClock

-- Credits to Marvel Heroes for the OGG sound files. (Not sure on the legality on this one. :/ It's a free/dead game, and the files are readily available in the DL. 
I guess if this is an issue I'll just say to download the game and get the files yourself if you want those specific characters.)

-- Credits to Soundbible for default alarm sounds - http://soundbible.com/tags-alarm-clock.html





***################### TO ENABLE RASPBIAN STRETH TO WORK WITH MY SCREEN #################***

-- Add following 8 lines at the end of the file /both/config.txt in raspberry pi:   
max_usb_current=1  
hdmi_force_hotplug=1  
config_hdmi_boost=7  
hdmi_group=2  
hdmi_mode=1  
hdmi_mode=87  
hdmi_drive=1  
hdmi_cvt 1024 600 60 6 0 0 0  
***Driver for my screen, from https://www.amazon.com/gp/product/B07FDYXPT7/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1***

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