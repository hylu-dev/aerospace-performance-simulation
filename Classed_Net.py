import numpy as np
from ExtractData import ExtractData

NUM_NODES = 140
NUM_CLASSES = 4
EXTERNAL_ARRIVALS = [0.00365,0.00365,0.00365,0.00365]

class Node:

    def __init__(self, num, name, external_arrivals, service_rate, class_probabilities):
        self.num = num
        self.name = name
        self.mu = service_rate
        self.lambda_class = np.zeros([NUM_CLASSES, NUM_NODES]) # Fake variables
        self.r_classes = np.array(external_arrivals) # Fake variables
        self.routing_prob = np.array(class_probabilities) # Fake variables
        self.total_lambda = 0

    def get_lambda_eq(self, class_num):
        neg_lambda = np.zeros(NUM_NODES)
        neg_lambda[self.num] = 1
        return self.lambda_class[class_num] - (neg_lambda)

class Classed_Network:

    def __init__(self, data):
        self.nodes = []
        self.total_nodes = NUM_NODES
        self.data = data
        self.id_map = data.node_id
        self.external_arrivals = data.getExternalRates()
        self.service_rates = data.getServiceRates()
        self.__populate_nodes()

    def __populate_nodes(self):
        probabilities = self.data.buildUniformDict()
        for i in range(NUM_NODES):
            self.nodes.append(Node(i, self.id_map[i], self.external_arrivals[i], self.service_rates[self.id_map[i]], self.data.getUniformProbabilities(i, probabilities)))

    def append_node(self, node):
        self.nodes.append(node)

    def construct_lambda_class(self):
        for i in range(len(self.nodes)): # Each Node
            for j in range(len(self.nodes[i].routing_prob)): # Each Class in Each Node
                for k in range(len(self.nodes)): # Each Probability of Each Class Routing to Each Node
                    self.nodes[k].lambda_class[j][i] += self.nodes[i].routing_prob[j][k]

    def calculate_lambda_c(self, class_num):
        _sys_eq = []
        _arrival_constants = []
        for i in range(len(self.nodes)):
            _sys_eq.append(self.nodes[i].get_lambda_eq(class_num))
            _arrival_constants.append(self.nodes[i].r_classes[class_num])
        sys_eq = np.array(_sys_eq) # + (10**-8)*np.random.rand(141, 141)
        arrival_constants = -1 * np.array(_arrival_constants)
        #print(sys_eq)
        class_lambdas = np.linalg.solve(sys_eq, arrival_constants)
        #print("Total Arrival rate for class#{} jobs".format(class_num))
        #print(class_lambdas)
        for i in range(len(self.nodes)):
            self.nodes[i].total_lambda += class_lambdas[i]


if __name__ == "__main__":
    data = ExtractData(2) # data pulled from sim running for 2 years
    CN = Classed_Network(data)
    CN.construct_lambda_class()
    CN.calculate_lambda_c(0)
    CN.calculate_lambda_c(1)
    CN.calculate_lambda_c(2)
    CN.calculate_lambda_c(3)
    for i in range(len(CN.nodes)):
        print("{:42} total arrival rate: {:20} | utilization: {:20} | response time: {:20}".format(
            CN.nodes[i].name, CN.nodes[i].total_lambda,
            CN.nodes[i].total_lambda / CN.nodes[i].mu, 1.0 / (CN.nodes[i].mu - CN.nodes[i].total_lambda), CN.nodes[i].mu))