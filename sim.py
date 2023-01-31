import random
import datetime
from collections import Counter
import FIFO_Node
import csv
import unittest
from Jobs import A, B, C, D

class Sim:
    """
        The production line is simulated through generating each machine process as a FIFO_Node.
        Jobs are then fed through as a specified rate for the liftime of the simulation.

        total_time: length of simulation in seconds
        arrival_distr: how job arrivals should be distributed
        rate: how often should jobs arrive per hour
        max_jobs: the maximum number of jobs that shoud be introduced into the simulation
    """
    def __init__(self, total_time, arrival_distr, rate = 1, max_jobs = float("inf")):
        self.rate = rate
        self.arrival_distr = arrival_distr
        self.time = 0
        self.total_time = total_time
        self.process_file = "runtimes_and_processing_rates.csv"
        self.QN_file = "filtered.csv"
        self.max_jobs = max_jobs
        self.job_count = 0
        self.jobs_completed = 0
        self.includeQN = True

        # 4 arrival streams for 4 different job types
        self.A_next_arrival = arrival_distr(rate) #random.expovariate(self.rate)
        self.B_next_arrival = arrival_distr(rate)
        self.C_next_arrival = arrival_distr(rate)
        self.D_next_arrival = arrival_distr(rate)
        self.arrivals = [self.A_next_arrival, self.B_next_arrival, self.C_next_arrival, self.D_next_arrival]
        self.A_process = self.__create_process("A")
        self.A_QNprocess, self.A_QNprobilities= self.__create_QNprocess("2649A4101")
        self.B_process = self.__create_process("B")
        self.B_QNprocess, self.B_QNprobilities= self.__create_QNprocess("2649A4102")
        self.C_process = self.__create_process("C")
        self.C_QNprocess, self.C_QNprobilities= self.__create_QNprocess("2649A4101")
        self.D_process = self.__create_process("D")
        self.D_QNprocess, self.D_QNprobilities= self.__create_QNprocess("2649A4102")
        # arrival probabilities
        self.A_external_arrivals = Counter()
        self.B_external_arrivals = Counter()
        self.C_external_arrivals = Counter()
        self.D_external_arrivals = Counter()
        # variables to pull routing probabilities
        self.A_probs = Counter()
        self.A_count = Counter()
        self.B_probs = Counter()
        self.B_count = Counter()
        self.C_probs = Counter()
        self.C_count = Counter()
        self.D_probs = Counter()
        self.D_count = Counter()

        self.nodes = {} # keys will be the names of each machine, that way we have any easy way to send jobs from machine to machine

    # generates a list machine processes that a particular job requires to be produced
    def __create_process(self, job_type):
        PART_TYPE = 0
        process = []
        with open(self.process_file) as f:
            next(f)
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                if line[PART_TYPE] == job_type and len(line) > 0:
                    process.append(line)
        return process

    # process data we scraped occasionally has missing data due to error, skip these and note in report
    def __create_skips(self):
        # get transitions
        nodeTransitions = Counter() #instead of prob, get occurences of transitions
        delimiter = ","
        skips = set()
        threshhold = 2
        with open(self.QN_file) as f:
            next(f) # skip first line
            last_line = ""
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                if len(line) > 1 and not '' in last_line and not '' in line:
                    first = last_line[9]
                    second = line[9]
                    if first != second:
                        nodeTransitions[first,second] += 1
                last_line = line
        #print("\nTRANSCOUNT\n", nodeTransitions)
        for transition, val in nodeTransitions.items():
            if val < threshhold and not transition in skips:
                skips.add(transition[1])
        #print("\nSKIP THESE TRANSITIONS\n\n", skips)
        return skips

    # it's a real struggle since normal processes are conditionally routed, but QN's are suddenly probabilistically routed ._.
    def __create_QNprocess(self, job_type):
        # get transitions
        nodeTransitions = Counter()
        nodeTransCounts = Counter()
        delimiter = ","
        skips = self.__create_skips() # remove low probability transitions in hopes of reducing amount of jobs getting stuck in QN
        with open(self.QN_file) as f:
            next(f) # skip first line
            last_line = ""
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                if len(line) + len(last_line) > 18 and job_type in last_line[1]:# and not any(item in skips for item in line): # specifically 'Finish Machining routes to nowhere'
                    first = last_line[9]
                    second = line[9]
                    if line[0] == '' and first != '': #second == all(x=='' for x in line)
                        #print(f"TESTING {last_line}\n{line}\n")
                        nodeTransitions[first, 'End of QNProcessing'] += 1
                        nodeTransCounts[first] += 1
                    elif first != second and first != '' and second != '':
                        nodeTransitions[first,second] += 1
                        nodeTransCounts[first] += 1

                    
                last_line = line
        for transition, val in nodeTransitions.items():
            nodeTransitions[transition] /= nodeTransCounts[transition[0]]

        # get service times
        nodeTimes = Counter()
        nodeCount = Counter()
        num = 0
        with open(self.QN_file) as f:
            next(f) # skip first line
            last_line = ""
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                num+=1
                if len(line) + len(last_line) > 18 and not last_line[9] == '' and not line[9] == '' and not 'N/A' in line[7:] and job_type in line[1]:
                    if last_line[9] != line[9]:
                        nodeCount[line[9]] += 1
                    #print(line)
                    date1 = list(map(int, line[-3].split('/')))
                    date2 = list(map(int, line[-2].split('/')))
                    date_start = datetime.date(date1[2], date1[0], date1[1])
                    date_finish = datetime.date(date2[2], date2[0], date2[1])
                    #print("Hours:", (date_finish-date_start).days*24)
                    if ((date_finish-date_start).days == 0):
                        nodeTimes[line[9]] += 8
                    else:
                        nodeTimes[line[9]] += (date_finish-date_start).days*24                    
                    nodeTimes[line[9]] += (date_finish-date_start).days*24
                last_line = line
        for key, val in nodeCount.items():
            nodeTimes[key] /= val
        #print(f"\nFINAL TRANSITIONS\n{nodeTransitions}\n")
        #print(f"\nTIMES\n{nodeTimes}\n")
        return nodeTimes, nodeTransitions
        #consider removing nodes with transcount of 11 or less

    # set clocks of all jobs to current sim time
    def update_clocks(self, time):
        self.time = time
        for node in self.nodes.values():
            node.update_clock(time)

    # run simulation
    def run(self):
        self.populate_nodes()
        while self.time < self.total_time:
            # list of all departure times for all our nodes
            departures = []
            departure_nodes = {}
            for node in self.nodes.values():
                time = node.get_next_event()
                departures.append(time)
                departure_nodes[time] = node
            # choose the next event that occurs
            next_event_time = min(self.arrivals+departures)
            self.update_clocks(next_event_time)
            if next_event_time in self.arrivals:
                self.job_count += 1 # to limit jobs for testing
                new_job = self.create_job(next_event_time)
                # add job arrival to machine with shortest time queue
                best_machine = self.getBestMachine(new_job.get_next())
                # log arrival data
                if type(new_job) is A.A:
                    self.A_external_arrivals[best_machine] += 1
                elif type(new_job) is B.B:
                    self.B_external_arrivals[best_machine] += 1
                elif type(new_job) is C.C:
                    self.C_external_arrivals[best_machine] += 1
                elif type(new_job) is D.D:
                    self.D_external_arrivals[best_machine] += 1
                # send to QN if necessary
                if self.includeQN and self.nodes[best_machine].check():
                    self.nodes[new_job.startQN()].arrive(new_job)
                else:
                    self.nodes[best_machine].arrive(new_job)
                if self.job_count < self.max_jobs:# limit jobs
                    self.arrivals[self.arrivals.index(self.time)] = self.time + self.arrival_distr(self.rate) # update next arrival time for that job type
                else:
                    self.arrivals[self.arrivals.index(self.time)] = float("inf")

            elif next_event_time in departures:
                node = departure_nodes[departures[departures.index(next_event_time)]]
                self.time = node.next_event
                processing_job = node.depart()
                # if the job is not done being processed, send it to its next machine
                if not processing_job.get_next() == "End of processing":
                    # send to QN if necessary
                    if self.includeQN and self.nodes[best_machine].check():
                        processing_job.startQN()
                    # add job arrival to machine with shortest time queue
                    best_machine = self.getBestMachine(processing_job.get_next())
                    # log transition data from departed job
                    if type(processing_job) is A.A:
                        self.A_probs[processing_job.get_last(), best_machine] += 1
                        self.A_count[processing_job.get_last()] += 1
                    elif type(processing_job) is B.B:
                        self.B_probs[processing_job.get_last(), best_machine] += 1
                        self.B_count[processing_job.get_last()] += 1
                    elif type(processing_job) is C.C:
                        self.C_probs[processing_job.get_last(), best_machine] += 1
                        self.C_count[processing_job.get_last()] += 1
                    elif type(processing_job) is D.D:
                        self.D_probs[processing_job.get_last(), best_machine] += 1
                        self.D_count[processing_job.get_last()] += 1
                    self.nodes[best_machine].arrive(processing_job)
                else:
                    self.jobs_completed += 1              

    # In cases where multiple machines are available for a job, choose the best one (least full)
    def getBestMachine(self, next_machines):
        shortest_queue = float("inf")
        best_machines = []
        for machine in next_machines:
            queue_length = self.nodes[machine].get_queue_time()
            if queue_length < shortest_queue:
                shortest_queue, best_machines = queue_length, [machine]
            elif queue_length == shortest_queue:
                best_machines.append(machine)
        return best_machines[random.randrange(0, len(best_machines))] # uniformly choose from best machines (all same queue length)

    # Generate a FIFO_Node for each of the machine processes
    def populate_nodes(self):
        PART_TYPE = 0
        MACHINES = 4
        with open(self.process_file) as f:
            next(f)
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                if len(line) > 0:
                    for machine in line[MACHINES].replace(']','').replace('[','').split(','):
                            self.nodes[machine] = FIFO_Node.FIFO_Node(machine)

        with open(self.QN_file) as f:
            next(f) # skip first line
            last_line = ""
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                if len(line) + len(last_line) > 18 and not last_line[9] == '' and not line[9] == '':
                    self.nodes[line[9]] = FIFO_Node.FIFO_Node(line[9])
                last_line = line
        self.nodes[''] = FIFO_Node.FIFO_Node('')
        #print("NODES:\n", self.nodes, "\n")

    # create a new job of required type
    def create_job(self, arrival_type):
        if arrival_type == self.arrivals[0]:
            return A.A(self.time, self.A_process.copy(), self.A_QNprocess, self.A_QNprobilities)
        if arrival_type == self.arrivals[1]:
            return B.B(self.time, self.B_process.copy(), self.B_QNprocess, self.B_QNprobilities)
        if arrival_type == self.arrivals[2]:
            return C.C(self.time, self.C_process.copy(), self.C_QNprocess, self.C_QNprobilities)
        if arrival_type == self.arrivals[3]:
            return D.D(self.time, self.D_process.copy(), self.D_QNprocess, self.D_QNprobilities)

    def print_results(self, part_type="ALL"):
        print(f"---------START {part_type}---------")
        if part_type == "ALL":
            for node in self.nodes.values():
                print(f"Process {node.name:44} | Average Response:{node.average_response():20} | Utilization:{node.utilization():22} | Average Service:{node.average_service():20} | # Jobs: {node.get_num_jobs():4}")
        else:
            # only show processes that are related to the given class of jobs:20
            new_nodes = []
            process = self.__create_process(part_type)
            for p in process: 
                for machine in p[4].replace(']','').replace('[','').split(','):
                    new_nodes.append(self.nodes[machine])
            for node in new_nodes:
                    print(f"Process {node.name:44} | Average Response: {node.average_response():20} | Utilization: {node.utilization():22} | # Jobs: {node.get_num_jobs():4}")
        print(f"Jobs Completed: {self.jobs_completed}")
        print(f"---------END {part_type}---------\n")

    #service rates for each FIFO_Node
    def get_service_rates(self):
        service_rates = {}
        for node in self.nodes.values():
            service_rates[node.name] = node.average_service()
        return service_rates

    #rate of job arrivals to nodes
    def get_external_rates(self):
        #calculate external rates
        for node in self.A_external_arrivals:
            self.A_external_arrivals[node] /= self.total_time
        for node in self.B_external_arrivals:
            self.B_external_arrivals[node] /= self.total_time
        for node in self.C_external_arrivals:
            self.C_external_arrivals[node] /= self.total_time
        for node in self.D_external_arrivals:
            self.D_external_arrivals[node] /= self.total_time
        result = [self.A_external_arrivals, self.B_external_arrivals, self.C_external_arrivals, self.D_external_arrivals]
        return(result)

    #probabilities for parts transitioning to specific FIFO_Nodes
    def get_probabilities(self):
        #calculate transition probabilities
        for transition, val in self.A_probs.items():
            self.A_probs[transition] /= self.A_count[transition[0]]
        for transition, val in self.B_probs.items():
            self.B_probs[transition] /= self.B_count[transition[0]]
        for transition, val in self.C_probs.items():
            self.C_probs[transition] /= self.C_count[transition[0]]
        for transition, val in self.D_probs.items():
            self.D_probs[transition] /= self.D_count[transition[0]]
        return([self.A_probs, self.B_probs, self.C_probs, self.D_probs])

        
class TestStringMethods(unittest.TestCase):

    # def test_singleA(self):
    #     sim = Sim(1000, random.expovariate, 1, 1)
    #     f = float("inf")
    #     sim.arrivals = [sim.A_next_arrival, f, f, f]
    #     sim.run()
    #     sim.print_results("A")

    # def test_singleB(self):
    #     sim = Sim(1000, random.expovariate, 1, 1)
    #     f = float("inf")
    #     sim.arrivals = [f, sim.B_next_arrival, f, f]
    #     sim.run()
    #     sim.print_results("B")

    # def test_singleC(self):
    #     sim = Sim(1000, random.expovariate, 1, 1)
    #     f = float("inf")
    #     sim.arrivals = [f, f, sim.C_next_arrival, f]
    #     sim.run()
    #     sim.print_results("C")

    # def test_singleD(self):
    #     sim = Sim(50000, random.expovariate, 1, 1)
    #     f = float("inf")
    #     sim.arrivals = [f, f, f, sim.D_next_arrival]
    #     sim.includeQN = True
    #     sim.run()
    #     sim.print_results("D")

    def test_all(self):
        sim = Sim(8760*10, random.expovariate, 0.00365)
        sim.run()
        sim.print_results()
        #print(sim.get_probabilities())


if __name__ == '__main__':
    unittest.main()