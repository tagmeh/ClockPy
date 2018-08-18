#!/bin/python

import time
import os
import datetime
import random
#  from pygame import mixer   #         Needs Pygame installed
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config



class DigitalClock(FloatLayout):
    display_time = StringProperty("00 : 00")
    alarm_time = StringProperty("00 : 00")
    alarm_time_hour = NumericProperty(00)
    alarm_time_minute = NumericProperty(00)
    clock_view = StringProperty("1")
    settings_view = StringProperty("0")
    alarm_switch = NumericProperty(0)       # Alarm On/Off Switch
    alarm_active = NumericProperty(0)       # Initial Alarm Call
    is_alarming = NumericProperty(0)        # Alarm Loop
    nfc_read = list(('04', '33', '3A', '4A', '22', '4B', '81')) #Starting list structure for NFC tags
    rando = NumericProperty(0)
    section = NumericProperty(1)            # Section of audio files to use 1=1-7, 2=8-14, 3=15-21
    play_num = NumericProperty(0)
    audio_path = StringProperty("")
    audio_file = StringProperty("")
    colour = NumericProperty(0)
    alarm_event = ()
    snooze = ()

    def update(self, dt=0):
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()


    def schedule_update(self, dt=0):
        current_time = time.localtime()
        seconds = current_time[5]
        secs_to_next_minute = 60 - seconds

        #print("Alarm Switch: " + str(self.alarm_switch))
        #print("alarm_time: " + self.alarm_time)
        #print("Current Time: " + self.display_time)
        #print("Is Alarming: " + str(self.is_alarming))
        if (self.display_time == self.alarm_time) and (self.alarm_switch == 1) and (self.is_alarming == 0):
            self.is_alarming = 1
            print("!!ALARM!!")
            Clock.schedule_once(self.update, secs_to_next_minute + 1) #add 1 second to ensure it updates after the new minute
            events = Clock.get_events()
            print(events)
            self.schedule_alarm()
        else:
            Clock.schedule_once(self.update, secs_to_next_minute)

    #Making schedule_alarm its own function to also be called when I put in the snooze function
    def schedule_alarm(self, dt=0):
        self.alarm_event = Clock.schedule_interval(self.alarm_loop, 1)


    def alarm_loop(self, *args):
        if self.is_alarming == 1 and (self.alarm_switch == 1):
            print("NFC UID: " + str(self.nfc_read[1])) # TODO READ NFC UID RIGHT HERE
            if self.colour == 0:
                self.colour = 1
            else:
                self.colour = 0
        else:
            self.is_alarming = 0
            Clock.unschedule(self.alarm_event)
            # TODO PLAY AUDIO FROM RASPBERRY PI CODE
                     #### Running the Audio File while in alarm ####
                #music = pygame.mixer.music
            #if music.get_busy() == False:
                #self.rando = random.randint(1, 7)
               # self.play_num = (self.rando) * (self.section)
                #self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                #print("Audio File: " + str(self.audio_file))
             #   if self.section == 1:
             #       self.section = 2
             #   else:
             #       if self.section == 2:
             #           self.section = 3
             #       else:
             #           self.section = 1
             #   if self.nfc_read[1] == "3E" or "3A":       # TODO THIS PATH NEEDS TO CHANGE ONCE ON THE RASPPI ######
             #       self.audio_path = "C:/Users/tate.justin/AppData/Local/Programs/Python/Python36-32/PiClock/KivyDigitalClock-master/KivyDigitalClock-master/Sounds/01-CaptainAmerica/"
             #       print("Audio Path: Cap - " + str(self.audio_path))  ## ^^^^^^^ CHANGE PATH HERE ^^^^^^^^ ##
             #   else:
             #       if self.nfc_read[1] == "33" or "CD":
             #           self.audio_path = "C:/Users/tate.justin/AppData/Local/Programs/Python/Python36-32/PiClock/KivyDigitalClock-master/KivyDigitalClock-master/Sounds/02-Hulk/"
             #           print("Audio Path: HULK - " + str(self.audio_path)) ## ^^^^^^^ CHANGE PATH HERE ^^^^^^^^ ##
             #           self.alarm_mode()
             #   else:
             #       self.audio_path = "C:/Users/tate.justin/AppData/Local/Programs/Python/Python36-32/PiClock/KivyDigitalClock-master/KivyDigitalClock-master/Sounds/"
             #       print("Audio Path: Default - " + str(self.audio_path))
             #       self.alarm_mode()


    # TODO - Add Snooze Function
    def snooze_func(self, *args):
        if (self.is_alarming == 1):
            Clock.unschedule(self.alarm_event)
            Clock.unschedule(self.snooze)
            self.snooze = Clock.schedule_once(self.schedule_alarm, 240)
            self.colour = 0
            events = Clock.get_events()
            print(events)
            #if music.get_busy() == True:
                #music.stop()

    def click_settings(self, *args):
        if args[1] == 'down':
            self.settings_view = "1"
            self.clock_view = "0"
            print("clock enabled: " + self.clock_view)
            print("settings enabled: " + self.settings_view)
            #self.schedule_update()  # Used for testing only - Comment out after

        else:
            self.settings_view = "0"
            self.clock_view = "1"
            print("clock enabled: " + self.clock_view)
            print("settings enabled: " + self.settings_view)
            #self.schedule_update()  # Used for testing only - Comment out after

    def switch_state(self, *args):
        if args[1] == True:
            self.alarm_switch = 1
            print("Alarm On: " + str(self.alarm_switch))
        else:
            self.alarm_switch = 0
            self.colour = 0
            self.is_alarming = 0
            Clock.unschedule(self.schedule_alarm)
            Clock.unschedule(self.snooze)
            print("Alarm Off: " + str(self.alarm_switch))

    def hour10_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (14):
                self.alarm_time_hour = self.alarm_time_hour + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def hour1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (23):
                self.alarm_time_hour = self.alarm_time_hour + 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_hour = 0

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





class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':
    Config.set('graphics', 'fullscreen', '0')              ####ENABLE FULLSCREEN#### 'auto'=fullscreen / '0'=not-fullscreen
    Config.set('graphics', 'window_state', 'normal')        ###MAY NOT NEED THIS ONE###
    Config.write()
    DigitalClockApp().run()
