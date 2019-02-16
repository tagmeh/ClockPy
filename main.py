#!/bin/python

import os
os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
import time
import datetime
import random
import pygame   # Needs Pygame installed
import io
import sys
import builtins
import traceback
from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from py532lib.mifare import *
from quick2wire.i2c import *
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config

class DigitalClock(FloatLayout):
    display_time = StringProperty("00 : 00")
    alarm_saved = open('config.txt', 'r')
    doc_text = alarm_saved.read()
    alarm_time_hour = int(doc_text.split(" : ")[0])
    alarm_time_minute = int(doc_text.split(" : ")[1])
    alarm_time = StringProperty(str(alarm_time_hour).zfill(2) + " : " + str(alarm_time_minute).zfill(2))
    clock_view = StringProperty("1")
    settings_view = StringProperty("0")     # Variable for Kivy to use, Variables for Kivy need to be a string
    alarm_switch = NumericProperty(0)       # Alarm On/Off Switch
    is_alarming = NumericProperty(0)        # Track when Alarm is Active
    is_snoozing = NumericProperty(0)       # Track when in Snooze mode
    set_sunday = StringProperty("0")        # Track what days the alarm is set to activate
    set_monday = StringProperty("0")
    set_tuesday = StringProperty("0")
    set_wednesday = StringProperty("0")
    set_thursday = StringProperty("0")
    set_friday = StringProperty("0")
    set_saturday = StringProperty("0")
    nfc_read = ''   #Starting empty string for NFC tags
    nfc_cap = 'x04>' #returned ID Significant Byte for my Captain America figure
    nfc_cap2 = 'xb9' #returned ID Significant Byte for my Captain America figure's sticker
    nfc_hulk = 'x04H' #returned ID Significant Byte for my Hulk figure
    nfc_hulk2 = 'xcd'#returned ID Significant Byte for my Hulk figure's sticker
    file_played = False
    hr_setting = StringProperty("0")
    am_pm = ''
    rando = NumericProperty(0)
    section = NumericProperty(1)            # Section of audio files to use 1=1-7, 2=8-14, 3=15-21
    play_num = NumericProperty(0)
    audio_path = StringProperty("")
    audio_file = StringProperty("")
    colour = NumericProperty(0)
    curr_time = int
    curr_day_name = StringProperty('')
    alarm_event = ()
    Pn532_i2c().SAMconfigure()
    pygame.init()
    Mifare().set_max_retries(2)


    def update(self, dt=0):
        Clock.unschedule(self.update)    # attempt to fix memory leak - Attempt Successful :)
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()
        #print('Scheduling Update ', self.schedule_update())

    def schedule_update(self, dt=0):
        self.am_pm = time.strftime("%p")
        current_time = time.localtime()
        seconds = current_time[5]
        secs_to_next_minute = (60 - seconds)
        self.curr_time = datetime.datetime.now()
        self.curr_day_name = self.curr_time.strftime("%A")
        if ((self.display_time == self.alarm_time) #If alarm time is equal to current time
        and (self.alarm_switch == 1) # and alarm switch is ON
        and (self.is_alarming == 0)):  # and system is currently not in alarm
            if (str(datetime.datetime.today().isoweekday()) == "7" and self.set_sunday == '1' #checking current day of week against if it's enabled below
            or str(datetime.datetime.today().isoweekday()) == "1" and self.set_monday == '1'
            or str(datetime.datetime.today().isoweekday()) == "2" and self.set_tuesday == '1'
            or str(datetime.datetime.today().isoweekday()) == "3" and self.set_wednesday == '1'
            or str(datetime.datetime.today().isoweekday()) == "4" and self.set_thursday == '1'
            or str(datetime.datetime.today().isoweekday()) == "5" and self.set_friday == '1'
            or str(datetime.datetime.today().isoweekday()) == "6" and self.set_saturday == '1'):
                self.is_alarming = 1 #put system in alarm mode, this is probably reduntant by this point with as many unschedules and kills I have in the script
                #print("!!ALARM!!", self.curr_time)
                Clock.schedule_once(self.update, secs_to_next_minute) #update again in 1 minute
                self.alarm_loop()
                #print('schedule_alarm running')
        else:
            Clock.schedule_once(self.update, secs_to_next_minute) #Update again in 1 minute


    def alarm_loop(self, *args):
        Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
        self.alarm_event = Clock.schedule_interval(self.alarm_loop, 1)
        #print('alarm_loop running')
        self.is_snoozing = 0
        if self.file_played == False:
            self.nfc_list() #Check for NFC tag on alarm.
        if self.is_alarming == 1 and (self.alarm_switch == 1):
            if self.colour == 0:
                self.colour = 1
            else:
                self.colour = 0
            if pygame.mixer.get_busy() == False:  # Check that audio currently isn't running
                self.rando = random.randint(1, 7)   # Random number between 1 and 7, inclusive
                self.play_num = (self.rando) + (self.section) # My files are split into 3 sections, 1-7, 8-14, 15-21 based on natural progression of intensity
                if self.section == 0:   # Increment to next section every round
                    self.section = 7
                else:
                    if self.section == 7:
                        self.section = 14
                    else:
                        self.section = 0
                if (self.nfc_cap in str(self.nfc_read)  # Determine audio file path based on NFC read
                or self.nfc_cap2 in str(self.nfc_read)):  # Determine audio file path based on NFC read
                    self.audio_path = "/home/pi/Desktop/PyClock/Sounds/01-CaptainAmerica/"
                    self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                    #print("Audio File: Cap - " + str(self.audio_file))
                    sound_file = pygame.mixer.Sound(str(self.audio_file)) #Load sound file into Pygame
                    #print(pygame.mixer.Sound)
                    self.file_played = True
                    pygame.mixer.Sound.play(sound_file) # Play sound file
                else:
                    if (self.nfc_hulk in str(self.nfc_read) # Determine audio file path based on NFC read
                    or self.nfc_hulk2 in str(self.nfc_read)):# Determine audio file path based on NFC read
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/02-Hulk/"
                        self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                        #print("Audio File: HULK - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        #print(pygame.mixer.Sound)
                        self.file_played = True
                        pygame.mixer.Sound.play(sound_file)
                    else:
                        self.rando = random.randint(1, 2) # Default alarm sounds if no NFC tag is found that matches above
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/"
                        self.audio_file = (self.audio_path + str(self.rando) + ".wav")
                        #print("Audio File: Default - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        #print(pygame.mixer.Sound)
                        self.file_played = True
                        pygame.mixer.Sound.play(sound_file)
        else:
            self.is_alarming = 0 # Shouldn't need this, but doesn't hurt. Some redundant stuff from def switch_state
            Clock.unschedule(self.alarm_event)

    def snooze_func(self, *args):
        if ((self.is_alarming == 1)
        and (self.is_snoozing == 0)):
            #print('snooze button pressed')
            self.is_snoozing = 1
            Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
            self.alarm_event = Clock.schedule_once(self.alarm_loop, 300) # schedule new 5-minute Snooze timer
            self.colour = 0                         # Set background color to Black
            self.file_played = False                     # Reset NFC to try again for tag
            if pygame.mixer.get_busy() == True:     # If sounds is currently playing
                pygame.mixer.stop()                 # Stop currently playing sound

    def cancel_func(self, *args):
        if (self.is_alarming == 1):
            self.is_snoozing = 0
            self.is_alarming = 0
            Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
            self.colour = 0                         # Set background color to Black
            self.file_played = False                     # Reset NFC to try again for tag
            if pygame.mixer.get_busy() == True:     # If sounds is currently playing
                pygame.mixer.stop()                 # Stop currently playing sound

    def click_settings(self, *args):
        if args[1] == 'down':
            self.settings_view = "1" # See digitalclock.kv for buttons using this variable
            self.clock_view = "0"   # See digitalclock.kv for buttons using this variable
            #events = Clock.get_events()  # Grab currently scheduled events
            #print(events)  # Print out events to Console
            #self.schedule_update()  # Used for testing only - Comment out after - This can immediately trigger the alarm if set to current time
        else:
            self.settings_view = "0"
            self.clock_view = "1"
            config_file = open("config.txt", "w") # Open config.txt file in "Write" mode
            config_file.write(self.alarm_time)    # Write the current alarm time into the file. This can be read later after the app or system reboots.
            #events = Clock.get_events()             # Grab currently scheduled events
            #print(events)                           # Print out events to Console
            #self.schedule_update()  # Used for testing only - Comment out after

    def click_12hr(self, *args):
        if args[1] == 'down':
            self.hr_setting = "1"
            self.display_time = time.strftime("%I : %M")
            self.am_pm = time.strftime("%p")
        else:
            self.hr_setting = "0"
            self.display_time = time.strftime("%H : %M")

    def toggle_fullscreen(self, *args): #Used to test full screen view when developing on PC. Requires app restarted to take effect.
        if args[1] == 'down':
            Config.set('graphics', 'fullscreen', 'auto')  ####ENABLE FULLSCREEN#### 'auto'=fullscreen / '0'=not-fullscreen
            Config.set('graphics', 'window_state', 'maximized')  ###MAY NOT NEED THIS ONE###
            Config.write()
        else:
            Config.set('graphics', 'fullscreen', '0')  ####ENABLE FULLSCREEN#### 'auto'=fullscreen / '0'=not-fullscreen
            Config.set('graphics', 'window_state', 'normal')  ###MAY NOT NEED THIS ONE###
            Config.write()

    def switch_state(self, *args): # Arm/disarm alarm
        if args[1] == True:
            self.alarm_switch = 1
        else:
            self.alarm_switch = 0                   # Toggle switch mode to "Off"
            self.colour = 0                         # Set background to black
            self.is_alarming = 0                    # Put clock in not-alarming mode
            self.file_played = False                     # Reset NFC to try again for tag
            Clock.unschedule(self.schedule_alarm) #Unschedule all alarm events, whether they're running or not.
            Clock.unschedule(self.alarm_event)
            if pygame.mixer.get_busy() == True: #Cut off the audio.
                pygame.mixer.stop()

    def hour10_up(self): # I realized later when trying to add other features that I should've done everything in minutes and divide it out to get hours
        if self.settings_view == "1":
            if self.alarm_time_hour <= (14):
                self.alarm_time_hour = self.alarm_time_hour + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2) #zfill used for padding single digits numbers with a zero
            else:
                pass

    def hour1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (22):
                self.alarm_time_hour = self.alarm_time_hour + 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_hour = 0
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

    def min10_up(self):
        if self.settings_view == "1":
            if self.alarm_time_minute <= (49):
                self.alarm_time_minute = self.alarm_time_minute + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def min1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_minute <= (58):
                self.alarm_time_minute = self.alarm_time_minute + 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_minute = 0
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

    def hour10_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_hour >= (10):
                self.alarm_time_hour = self.alarm_time_hour - 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def hour1_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_hour >= (1):
                self.alarm_time_hour = self.alarm_time_hour - 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_hour = 23
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

    def min10_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_minute >= (10):
                self.alarm_time_minute = self.alarm_time_minute - 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def min1_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_minute >= (1):
                self.alarm_time_minute = self.alarm_time_minute - 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_minute = 59
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

    def press_sunday(self, *args):
        if self.set_sunday == '0' and self.settings_view == "1":
            self.set_sunday = '1'
        else:
            if self.set_sunday == '1' and self.settings_view == "1":
                self.set_sunday = '0'

    def press_monday(self, *args):
        if self.set_monday == '0' and self.settings_view == "1":
            self.set_monday = '1'
        else:
            if self.set_monday == '1' and self.settings_view == "1":
                self.set_monday = '0'

    def press_tuesday(self, *args):
        if self.set_tuesday == '0' and self.settings_view == "1":
            self.set_tuesday = '1'
        else:
            if self.set_tuesday == '1' and self.settings_view == "1":
                self.set_tuesday = '0'

    def press_wednesday(self, *args):
        if self.set_wednesday == '0' and self.settings_view == "1":
            self.set_wednesday = '1'
        else:
            if self.set_wednesday == '1' and self.settings_view == "1":
                self.set_wednesday = '0'

    def press_thursday(self, *args):
        if self.set_thursday == '0' and self.settings_view == "1":
            self.set_thursday = '1'
        else:
            if self.set_thursday == '1' and self.settings_view == "1":
                self.set_thursday = '0'

    def press_friday(self, *args):
        if self.set_friday == '0' and self.settings_view == "1":
            self.set_friday = '1'
        else:
            if self.set_friday == '1' and self.settings_view == "1":
                self.set_friday = '0'

    def press_saturday(self, *args):
        if self.set_saturday == '0' and self.settings_view == "1":
            self.set_saturday = '1'
        else:
            if self.set_saturday == '1' and self.settings_view == "1":
                self.set_saturday = '0'


    def nfc_list(self):
        """Grab the entire output of the NFC mobule from the I2C channel."""
        self.nfc_read = Mifare().scan_field()
        '''if self.nfc_read:
            print('Tag Found')
            print('nfc_read = ' + str(self.nfc_read))
        else:
            print('no tag found')
            print('nfc_read = ' + str(self.nfc_read))
        print(self.curr_time)'''


class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':

    DigitalClockApp().run()
