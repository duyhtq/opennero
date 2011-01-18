from OpenNero import *
import math
import random

class RTNEATAgent(AgentBrain):
    """
    rtNEAT agent
    """
    def __init__(self):
        """
        Create an agent brain
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        AgentBrain.__init__(self)
        global rtneat
        rtneat = get_ai("neat")

    def initialize(self, init_info):
        """
        Initialize an agent brain with sensor information
        """
        self.actions = init_info.actions # constraints for actions
        self.sensors = init_info.sensors # constraints for sensors
        return True

    def start(self, time, sensors):
        """
        start of an episode
        """
        global rtneat
        self.org = rtneat.next_organism(0.5)
        self.net = self.org.net
        self.reward = 0
        sensors = self.sensors.normalize(sensors)
        return self.network_action(sensors)

    def act(self, time, sensors, reward):
        """
        a state transition
        """
	if reward >= 1:
	    self.reward += reward # store reward
        sensors = self.sensors.normalize(sensors)
        return self.network_action(sensors)

    def end(self, time, reward):
        """
        end of an episode
        """
        self.reward += reward # store reward
        self.org.fitness = self.reward # assign organism fitness for evolution
        self.org.time_alive += 1
        return True

    def destroy(self):
        """
        the agent brain is discarded
        """
        return True
        
    def network_action(self, sensors):
        """
        Take the current network.
        Feed the sensors into it.
        Activate the network to produce the output.
        Collect and interpret the outputs as valid maze actions.
        """
        # make sure we have the right number of sensors
        assert(len(sensors)==6)
        # convert the sensors into the [0.0, 1.0] range
        sensors = self.sensors.normalize(sensors)
        # create the list of sensors
        inputs = [sensor for sensor in sensors]        
        # add the bias value
        inputs.append(0.3)
        # load the list of sensors into the network input layer
        self.net.load_sensors(inputs)
        # activate the network
        self.net.activate()
        # get the list of network outputs
        outputs = self.net.get_outputs()
        # create a C++ vector for action values
        actions = self.actions.get_instance()
        # assign network outputs to action vector
        for i in range(0,len(self.actions.get_instance())):
            actions[i] = outputs[i]
        # convert the action vector back from [0.0, 1.0] range
        actions = self.actions.denormalize(actions)
        #print "in:", inputs, "out:", outputs, "a:", actions
        return actions
