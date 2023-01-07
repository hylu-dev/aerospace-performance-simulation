import datetime
import csv
import random
import sys
from collections import Counter
from sim import Sim

A = "2649A4101"
B = "2649A4102"
C = "2649A4101"
D = "2649A4102"

process_txt = "runtimes_and_processing_rates.csv"
qn_txt = "filtered.csv"
delimiter = ","

class ExtractData():

	def __init__(self, years = 0):
		self.sim = Sim(8760*years, random.expovariate, 0.00365)
		self.sim.run()
		self.node_id = self.__createIDS()
		self.node_names = inv_map = {v: k for k, v in self.node_id.items()}

	def __createIDS(self):
		delimiter = ","
		node_id = {}
		id = 0
		PART_TYPE = 0
		MACHINES = 4
		with open(process_txt) as f:
			next(f)
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(line) > 0 and not 'Total' in line[2]:
					for machine in line[MACHINES].replace(']','').replace('[','').split(','):
						if not machine in node_id.values():
							node_id[id] = machine
							id+=1

		with open(qn_txt) as f:
			next(f) # skip first line
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(line) > 9 and line[9] != '':
					process = line[9]
					if not process in node_id.values():
						node_id[id] = process
						id+=1
		return node_id

	def getServiceRates(self):
		serviceRates = Counter()
		count = Counter()
		RUN_TIME = 2
		MACHINES = 4

		with open(process_txt) as f:
			next(f)
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(line) > 4 and not 'Total' in line[RUN_TIME] and not line[RUN_TIME] == '':
					rate = line[RUN_TIME]
					for machine in line[MACHINES].replace(']','').replace('[','').split(','):
						serviceRates[machine] += float(rate)
						count[machine] += 1

		with open(qn_txt) as infile:
			next(infile) # skip first line
			reader = csv.reader(infile, delimiter=",")
			last_line = ""
			for line in reader:
				if len(line) + len(last_line) > 18 and not last_line[9] == '' and not line[9] == '' and not 'N/A' in line[7:]:
					if last_line[9] != line[9]:
						count[line[9]] += 1
					#print(line)
					date1 = list(map(int, line[-3].split('/')))
					date2 = list(map(int, line[-2].split('/')))
					date_start = datetime.date(date1[2], date1[0], date1[1])
					date_finish = datetime.date(date2[2], date2[0], date2[1])
					#print("Hours:", (date_finish-date_start).days*24)
					if ((date_finish-date_start).days == 0):
						serviceRates[line[9]] += 8
					else:
						serviceRates[line[9]] += (date_finish-date_start).days*24
				elif len(line) + len(last_line) > 18 and not last_line[9] == '' and not line[9] == '' and 'N/A' in line[7:]:
					serviceRates[line[9]] += 8
					count[line[9]] += 1
				last_line = line					

		for machine, rate in serviceRates.items():
			serviceRates[machine] /= count[machine]
			serviceRates[machine] = 1/serviceRates[machine]

		return serviceRates

	def getExternalRates(self):
		total_rates = []
		rates = self.sim.get_external_rates()

		for i in range(len(self.node_id)):
			class_rates = []
			class_group = set([0,1,2]) # classes in this have the same external rates
			for j in range(4):
				if j in class_group and self.node_id[i] in ['2312','2301']:
					class_rates.append(1/2)
				elif not j in class_group and self.node_id[i] in ['2301','2312','20740','20710','20910']:
					class_rates.append(1/5)
				else:
					class_rates.append(0)
			total_rates.append(class_rates)
		return total_rates

	# def getQNProbabilities(self):
	# 	nodeTransitions = Counter()
	# 	nodeTransCounts = Counter()
	# 	delimiter = ","
	# 	probabilities = []
	# 	part_types = [A,B,C,D]

	# 	for part in part_types:
	# 		with open(qn_txt) as f:
	# 			next(f) # skip first line
	# 			last_line = ""
	# 			reader = csv.reader(f, delimiter=",")
	# 			for line in reader:
	# 				if len(line) + len(last_line) > 18 and part in last_line[1]:
	# 					first = last_line[9]
	# 					second = line[9]
	# 					if first != second and first != '' and second != '':
	# 						nodeTransitions[first,second] += 1
	# 						nodeTransCounts[first] += 1
	# 					#assign ids
	# 				last_line = line
	# 		for transition, val in nodeTransitions.items():
	# 			nodeTransitions[transition] /= nodeTransCounts[transition[0]]
	# 		probabilities.append(nodeTransitions)
	# 	return probabilities

	# def getTotalProbabilities(self):
	# 	total_probabilities = []	
	# 	qn_probabilities = self.getQNProbabilities()
	# 	process_probabilities = self.sim.get_probabilities()
	# 	for i in range(4):
	# 		total_probabilities.append(qn_probabilities[i])
	# 		total_probabilities[i].update(process_probabilities[i])
	# 	return total_probabilities

	# def getSimProbabilities(self):
	# 	probabilities = []
	# 	sim_probabilities = self.sim.get_probabilities()
	# 	for i in range(4):
	# 		probabilities.append(sim_probabilities[i])
	# 	return probabilities

	# def getClassProbabilities(self, node, probabilities):
	# 	class_probabilities = []
	# 	for part_probs in probabilities:
	# 		prob_current_node = []
	# 		for i in range(len(self.node_id)):
	# 			prob_current_node.append(part_probs[(self.node_id[node], self.node_id[i])])
	# 		class_probabilities.append(prob_current_node)
	# 	#print(f"Calculated Node {start_node} of {len(self.node_id)}", end='\r', flush=True)
	# 	return class_probabilities

	def buildUniformDict(self):
		delimiter = ","
		id = 0
		PART_TYPE = 0
		MACHINES = 4
		part_types = ['A','B','C','D']
		QNPart_types = [A,B,C,D]
		probabilities = [Counter(), Counter(), Counter(), Counter()]


		with open(process_txt) as f:
			next(f)
			last_line = ''
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(last_line) > 4 and last_line[0] in part_types and not 'Total' in line[2]:
					first = last_line[MACHINES].replace(']','').replace('[','').split(',')
					second = line[MACHINES].replace(']','').replace('[','').split(',')
					for last_machine in first:
						for machine in second:
							probabilities[part_types.index(last_line[0])][last_machine, machine] += 1
				last_line = line

		with open(qn_txt) as f:
			next(f)
			last_line = ''
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(line) + len(last_line) > 18:
					first = last_line[9]
					second = line[9]
					if first != second and first != '' and second != '':
						for part in range(len(QNPart_types)):
							probabilities[part][first, second] += 1
				last_line = line
		return probabilities

	def getUniformProbabilities(self, start_node, probabilities):
		#create empty grid
		start = self.node_id[start_node]
		part_types = ['A','B','C','D']
		QNpart_types = [A,B,C,D]
		grid = []
		departure_nodes = set(['Final Inspection', '29353'])
		departure_QN_nodes = set()
		#get departure_QN_nodes
		with open(qn_txt) as f:
			next(f)
			last_line = ''
			reader = csv.reader(f, delimiter=",")
			for line in reader:
				if len(line) + len(last_line) > 18:
					first = last_line[9]
					second = line[9]
					if first != second and first != '' and second == '':
						departure_QN_nodes.add(first)
				last_line = line

		for row in range(len(part_types)):
			grid.append([0]*len(self.node_id))

		for class_job in range(len(grid)):
			for node in range(len(grid[class_job])):
				grid[class_job][node] = probabilities[class_job][self.node_id[start_node], self.node_id[node]]
			if start_node < 103: # nodes less than 103 are nonQN processes
				grid[class_job][self.node_names['MRB QA']] = 0.1 # then add a chance to goto QN
			elif self.node_id[start_node] in departure_QN_nodes: #if in departure qn nodes than chance to return back to any process node
				for i in range(103):
					grid[class_job][i] = 0.05
			if sum(grid[class_job]) and not self.node_id[start_node] in departure_nodes: # if in departure node, don't normalize, just leave 0.1 chance to QN
				grid[class_job] = [float(i)/sum(grid[class_job]) for i in grid[class_job]]
			elif self.node_id[start_node] in departure_nodes:
				grid[class_job] = [float(i)/(sum(grid[class_job])*2) for i in grid[class_job]]
		return grid

if __name__ == "__main__":
	data = ExtractData(0)
	# for i in range(141):
	# 	for row in data.getUniformProbabilities(i, data.buildUniformDict()):
	# 	 	print(sum(row))
	# 	 	if sum(row) > 1:
	# 	 		print(data.node_id)
	# 	 		print(i, row)
	# 	print()

	# print(data.getServiceRates())
	count = 0
	for node, rate in data.getServiceRates().items():
		print(f"{node} ---- {data.node_id[count]} at {count} with rate {rate}")
		count+=1