#!/usr/bin/env python

'''
KivyWorker integrates kivy framework and class Worker

Open file \"kivy_worker.py\" and scroll down to see sample code
press space bar to test the sample
'''

import thread
import time

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from random import random as r
from kivy.clock import Clock, mainthread
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
        
        self._mission_out = []


    #============================= TODO =================================
        
    def _execute_a_keyboard_mission(self, mission):
        """Handle Keyboard mission and be prepared to _export_mission(model)"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + "._execute_a_keyboard_mission()")
    
    def _execute_a_render_mission(self, mission):
        """handle Model mission and do the render"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + "._execute_a_render_mission()")

    #====================================================================


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
        while not self.mission_in.empty():
            mission = self.mission_in.get_nowait()
            if 'key_code' in mission:
                self._execute_a_keyboard_mission(mission)
            else:
                self._execute_a_render_mission(mission)
        
    def start_loop(self, new_thread=False):
        if new_thread:
            print "Warning: kivy apps cannot run in any thread other then mainthread,"\
                   "thus " + self.__class__.__name__ + ".start_loop() is running in blocking mode"\
                   "the parameter \"new_thread=True\" passed in "+ self.__class__.__name__ + ".start_loop(new_thread=True)"\
                   " is invalid and disabled."
        runTouchApp(self)

    def _put_mission_out(self, mission):
        self._mission_out.append(mission)
    
    def _export_missions(self, receiver):
        missions = self._mission_out[:]
        self._mission_out = []
        return missions


        
# ========================== Test + sample code =============================
        
if __name__ == '__main__':
    print __doc__
    
    class TestModel(Worker):

        def __init__(self):
            super(TestModel, self).__init__()
            self._add_sqrt = 0

        def _routine(self):
            missions = self.mission_in
            while not missions.empty():
                mission = missions.get_nowait()
                self._add_sqrt += mission['show square']

        def _export_missions(self, caller):
            if self._add_sqrt > 0:
                mission = {'add_rect':self._add_sqrt}
                self._add_sqrt -= 1
                return [mission]
            return []

        
    class TestWindow(KivyWorker):

        def __init__(self):
            super(TestWindow, self).__init__()

        def _execute_a_keyboard_mission(self, mission):
            key_code = mission['key_code']
            if key_code[1] == 'spacebar':
                sig = {'show square':1}
            else:
                exit()
            self._put_mission_out(sig)
        
        def _execute_a_render_mission(self, mission):
            """handle Model mission and do the render"""
            if mission['add_rect']:
                with self.canvas:
                    Color(r(), 1, 1, mode='hsv')
                    Rectangle(pos=(r() * self.width,
                        r() * self.height), size=(20, 20))

    
    tm = TestModel()
    tw = TestWindow()
    # The module that work slower shall keep the list of co-workers
    tw.init_inout_list([tm], [tm])  

    tm.start_loop(new_thread=True)
    tw.start_loop()
