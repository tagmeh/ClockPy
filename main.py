#!/bin/python

import time
import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *


class DigitalClock(FloatLayout):
    display_time = StringProperty("00 : 00")


    def update(self, dt=0):
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()


    def schedule_update(self):
        current_time = time.localtime()
        seconds = current_time[5]

        # Handle leap seconds?
        secs_to_next_minute = 60 - seconds

        Clock.schedule_once(self.update, secs_to_next_minute)


class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':
    DigitalClockApp().run()
