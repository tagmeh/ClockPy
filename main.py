#!/bin/python

import os
os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
import time
#import os
#import datetime
import random
import pygame   # Needs Pygame installed
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
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
    settings_view = StringProperty("0")
    alarm_switch = NumericProperty(0)       # Alarm On/Off Switch
    alarm_active = NumericProperty(0)       # Initial Alarm Call
    is_alarming = NumericProperty(0)        # Alarm Loop
    nfc_read = ''   #Starting empty string for NFC tags
    nfc_cap = '136, 4, 62, 58, 136' #returned ID for my Captain America figure
    nfc_hulk = '136, 4, 72, 63, 251' #returned ID for my Hulk figure
    rando = NumericProperty(0)
    section = NumericProperty(1)            # Section of audio files to use 1=1-7, 2=8-14, 3=15-21
    play_num = NumericProperty(0)
    audio_path = StringProperty("")
    audio_file = StringProperty("")
    colour = NumericProperty(0)
    alarm_event = ()
    snooze = ()
    pygame.init()

    def update(self, dt=0):
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()

    def schedule_update(self, dt=0):
        current_time = time.localtime()
        seconds = current_time[5]
        secs_to_next_minute = 60 - seconds
        if (self.display_time == self.alarm_time) and (self.alarm_switch == 1) and (self.is_alarming == 0):
            self.is_alarming = 1
            #print("!!ALARM!!")
            Clock.schedule_once(self.update, secs_to_next_minute)
            self.schedule_alarm()
        else:
            Clock.schedule_once(self.update, secs_to_next_minute)

    #Making schedule_alarm its own function to also be called from multiple functions that run only once. Saves cycles from the loop scheduling itself once every second.
    def schedule_alarm(self, dt=0):
        self.alarm_event = Clock.schedule_interval(self.alarm_loop, 1)
        #print('schedule_alarm running')

    def alarm_loop(self, *args):
        #print('alarm_loop running')
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
                if self.nfc_read == self.nfc_cap:  # Determine audio file path based on NFC read
                    self.audio_path = "/home/pi/Desktop/PyClock/Sounds/01-CaptainAmerica/"
                    self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                    #print("Audio File: Cap - " + str(self.audio_file))
                    sound_file = pygame.mixer.Sound(str(self.audio_file)) #Load sound file into Pygame
                    #print(pygame.mixer.Sound)
                    pygame.mixer.Sound.play(sound_file) # Play sound file
                else:
                    if (self.nfc_read == self.nfc_hulk): # Repeat from above, but for Hulk
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/02-Hulk/"
                        self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                        print("Audio File: HULK - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        print(pygame.mixer.Sound)
                        pygame.mixer.Sound.play(sound_file)
                    else:
                        self.rando = random.randint(1, 3) # Default alarm sounds if no NFC tag is found that matches above
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/"
                        self.audio_file = (self.audio_path + str(self.rando) + ".wav")
                        print("Audio File: Default - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        print(pygame.mixer.Sound)
                        pygame.mixer.Sound.play(sound_file)
        else:
            self.is_alarming = 0 # Shouldn't need this, but doesn't hurt. Some redundant stuff from def switch_state
            Clock.unschedule(self.alarm_event)

    def snooze_func(self, *args):
        if (self.is_alarming == 1):
            Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
            Clock.unschedule(self.snooze)           # unschedule any existing 4-minute Snooze timer, otherwise they stack on top of each other with every button press
            self.snooze = Clock.schedule_once(self.schedule_alarm, 240) # schedule new 4-minute Snooze timer
            self.colour = 0                         # Set background color to Black
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
            events = Clock.get_events()             # Grab currently scheduled events
            print(events)                           # Print out events to Console
            #self.schedule_update()  # Used for testing only - Comment out after

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
            #print("Alarm On: " + str(self.alarm_switch))
        else:
            self.alarm_switch = 0
            self.colour = 0
            self.is_alarming = 0
            Clock.unschedule(self.schedule_alarm) #Unschedule all alarm events, whether they're running or not.
            Clock.unschedule(self.alarm_event)
            Clock.unschedule(self.snooze)
            if pygame.mixer.get_busy() == True: #Cut off the audio.
                pygame.mixer.stop()
            #print("Alarm Off: " + str(self.alarm_switch))

    def hour10_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (14):
                self.alarm_time_hour = self.alarm_time_hour + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2) #zfill used for padding single digits numbers with a zero
            else:
                pass

    def hour1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (23):
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
                self.alarm_time_hour = 24
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


class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':

    DigitalClockApp().run()
