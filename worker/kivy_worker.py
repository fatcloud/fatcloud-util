#!/usr/bin/env python

'''
KivyGUI is a base class that meant to be inherited to create app
that convert keyboard event to "Model" signal and grab render
command back when it is ready to update the next frame
'''

import thread
import time

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from random import random as r
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.base import runTouchApp

from worker import Worker


class KivyWorker(Widget, Worker):

    def __init__(self):
        Widget.__init__(self)
        Worker.__init__(self)
        
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.__on_key_down)
        
        # OutputExecutor
        Clock.schedule_interval(self.__update_frame, 1.0/60.0)

    # Pseudo co-worker
    def __on_key_down(self, keyboard, key_code, text, modifiers):
        key_info = {'keyboard':keyboard,
                    'key_code':key_code,
                    'text':text,
                    'modifiers':modifiers}
        mission = {'immediate':True}
        mission.update(key_info)
        self.add_todo(mission)
            
    def __update_frame(self, dt):
        self.routine()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.interpret_input)
        self._keyboard = None

    def _routine(self):
        while not self.mission_queue.empty():
            mission = self.mission_queue.get_nowait()
            if 'key_code' in mission:
                self._execute_a_keyboard_mission(mission)
            else:
                self._execute_a_render_mission(mission)
        
    def _execute_a_keyboard_mission(self, mission):
        """Handle Keyboard mission and be prepared to _export_mission(model)"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + "._execute_a_keyboard_mission()")
    
    def _execute_a_render_mission(self, mission):
        """handle Model mission and do the render"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + "._execute_a_render_mission()")
        
    