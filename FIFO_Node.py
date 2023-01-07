import random
from Jobs import A, B, C, D

class FIFO_Node:

    def __init__(self, name, rate = 1):
        self.name = name
        self.jobs = []
        self.time = 0
        self.rate = rate
        self.busy_time = 0
        self.response_times = []
        self.next_event = float("inf")
        self.service_time = 0
        self.total_service_time = 0
        self.num_services = 0
        self.job_count = 0
        self.next_check = 0

    def arrive(self, job):
        self.job_count+=1
        self.jobs.append(job)
        job.arrival_time = self.time
        #sets the service time for this job
        self.service_time = job.get_service_time()
        self.total_service_time += self.service_time
        self.num_services+=1
        #sets it for next process
        job.set_next()
        if len(self.jobs) == 1:
            self.calc_next()

    def calc_next(self):
        size = self.service_time
        self.next_event = self.time + size

    def update_clock(self, time):
        if len(self.jobs) > 0:
            self.busy_time += time - self.time
        self.time = time

    def depart(self):
        #print("departing: ", self.name, self.response_times)
        #print(self.time - self.jobs[0].arrival_time)
        self.jobs[0].set_last(self.name)
        self.response_times.append(self.time - self.jobs[0].arrival_time)
        if len(self.jobs) > 1:
            self.calc_next()
        else:
            self.next_event = float("inf")
        return self.jobs.pop(0)

        #print(self.time, self.name, "Departure:", "Jobs at node: " + str(len(self.jobs)))

    def check(self):
        if self.time >= self.next_check:
            if random.uniform(0, 1) <= 0.05:
                self.next_check = self.time+730 # one month intervals                
                return True
            else:
                return False
        else:
            if random.uniform(0, 1) <= 0.01:
                self.next_check = self.time+730 # one month intervals
                return True
            else:
                return False

    def get_queue_time(self):
        total = 0
        for job in self.jobs:
            total += job.get_service_time()
        return total

    def get_next_event(self):
        return self.next_event

    def average_response(self):
        if len(self.response_times) == 0:
            return 0
        return sum(self.response_times)/len(self.response_times)

    def average_service(self):
        if self.num_services > 0 and self.total_service_time > 0:
            return 1/(self.total_service_time/self.num_services)
        return 0

    def get_num_jobs(self):
        return self.job_count

    def utilization(self):
        return self.busy_time/self.time 