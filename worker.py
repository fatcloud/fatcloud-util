import thread
import Queue

class Worker(object):
    
    def __init__(self):
        self.mission_queue = Queue.PriorityQueue()
        
        # only those worker who work faster then self
        # shall be maintained in this list
        self.init_inout_list()
        self.routines = [self.routine]
    
    def init_inout_list(self, in_list = [], out_list = []):
        self.in_list  = in_list[:]
        self.out_list = out_list[:]
        
    @staticmethod
    def infinite_loop(func):
        while True:
            func()
    
    def start_loop(self):
        for routine in self.routines:
            thread.start_new_thread(Worker.infinite_loop, (routine,))

    # Do something actively
    def routine(self):
        for colleague in self.in_list:
            missions = colleague.tell_todo(self)
            for mission in missions:
                self.add_todo(mission)
                
        self._routine()
        
        for colleague in self.out_list:
            missions = self._export_missions(colleague)
            for mission in missions:
                colleague.add_todo(mission)
    
    # Passively respond to co-workers
    def add_todo(self, mission):
        """Assign jobs to self by slow up-stream co-workers"""
        if mission != {}:
            self.mission_queue.put(mission)
        else:
            return
        
        immediate = False
        try: immediate = mission["immediate"]
        except (KeyError, TypeError): pass
        
        if immediate is True:
            self.routine()
    
    def tell_todo(self, caller):
        """Tell a down-stream co-worker what to do now when they ask"""
        return self._export_missions(caller)
    
    # common job to do no matter yo are fast or slow
    def _export_missions(self, receiver):
        """Tell receiver what to do next"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + "._export_missions()")

    def _routine(self):
        """Pop and execute commands queued in self.mission_queue"""
        raise NotImplementedError("Please Implement " + self.__class__.__name__ + ".routine()")
        