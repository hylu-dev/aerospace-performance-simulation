import numpy as np

"""
    arrival_time: the time this job enters the production line
    process: a list of the processes required for this part to be produced, specifically a list of cooresponding rows from runtime_and_processing_rates.csv
    QNProcess: a list of the QNprocesses required for this part to be reworked, specifically a list of cooresponding rows from QN_Extract_Data_Censored.csv
"""
class Job:

    def __init__(self, arrival_time, process, QNProcess, QNProbabilities):
        self.arrival_time = arrival_time
        self.process = process
        self.QNProcess = QNProcess
        self.QNProbabilities = QNProbabilities
        self.currentQN = 'MRB QA'
        self.inQN = False
        self.startQNTime = 0
        self.totalQNTime = 0
        self.last_process = None

    def get_next(self):
        if not self.inQN:
            #print(f"{len(self.process)} PROCESSES LEFT AT TIME {self.arrival_time}")
            MACHINES = 4
            if self.process:
                return self.process[0][MACHINES].replace(']','').replace('[','').split(',')
            #print(f"TOTAL QN TIME: {self.totalQNTime} FINISHED AT {self.arrival_time}")
            #print(f"{self.totalQNTime},{self.arrival_time}")
            return "End of processing"
        else:
            self.totalQNTime = self.arrival_time-self.startQNTime
            processes = []
            probabilities = []
            for transition, prob in self.QNProbabilities.items():
                if transition[0] == self.currentQN:
                    processes.append(transition[1])
                    probabilities.append(prob)
            choice = np.random.choice(processes, 1, p=probabilities)
            self.currentQN = choice[0]
            if 'End of QNProcessing' in self.currentQN or self.totalQNTime > 400: # if finished qn, go back to original process
                self.inQN = False
                return self.get_next()
            return choice


    def startQN(self):
        self.inQN = True
        self.currentQN = 'MRB QA'
        self.startQNTime = self.arrival_time
        return self.currentQN

    def get_last(self):
        return self.last_process

    def set_last(self, new_process):
        self.last_process = new_process

    def get_service_time(self):
        if not self.inQN:
            RUN_TIME = 2
            try:
                result = float(self.process[0][RUN_TIME])
                return result
            except:
                return 0
        else:
            return self.QNProcess[self.currentQN]


    def set_next(self):
        MACHINES = 4
        if not self.inQN:
            self.process.pop(0)