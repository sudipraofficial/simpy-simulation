import simpy as sp
import random

# CONSTANTS
NO_BERTHS = 2
PER_VESSSEL_CONTAINERS = 150
NO_OF_QUAY_CRANE = 2
NO_OF_TRUCKS = 3
SIMULATION_TIME = 1440 # 24 hours in Minutes


class ContainerTerminal:
    """Class to handle simulation for Vessel, Berth, Quay Creane, Trucks"""

    def __init__(self, env):
        """Defining enviroment and resource"""
        self.env = env
        self.berth = sp.Resource(env, capacity=NO_BERTHS)
        self.quay_crane = sp.Resource(env, capacity=NO_OF_QUAY_CRANE)
        self.truck = sp.Resource(env, capacity=NO_OF_TRUCKS)
        self.vessel_in_use = []
        self.quay_crane_in_use = []
        self.truck_in_use = []

    def vessel_discharge(self, name):
        """Funciton to handle vessel discharge simulation"""

        vessel_dischage_time = 3 * PER_VESSSEL_CONTAINERS
        print(f"{name} arrives at time {self.env.now:2f} and waiting for free berth")
        yield self.env.timeout(1) # Time to ship at berth

        with self.berth.request() as berth_req:
            yield berth_req
            print(f"{name} assigned berth on {self.env.now:2f} and starts discharging")
            yield self.env.timeout(vessel_dischage_time)
            print(f"{name} finished discharging at {self.env.now:2f} and leaves the berth")
            self.vessel_in_use.append(name) # storing the name of the vessel which discharged container in berth and waiting for next process

    def move_container_to_truck(self, name):
        """Funciton to handle moving container to truck simulation"""
        C2T_moving_timing = 3 * PER_VESSSEL_CONTAINERS # Moving timing of container to truck
        # print(f"{name} Ready and waiting to move container to the truck at {self.env.now:.2f}")
        # yield env.timeout(1) # Time to reach the vessel

    
        random_vessel = str(random.choice(self.vessel_in_use))  # get a random vessel among the waiting vessel
        with self.quay_crane.request() as quay_crane_req:
            self.vessel_in_use.remove(random_vessel) # remove the vessel from the berth list as it going to next process of quay_crane
            yield quay_crane_req
            print(f"{name} starts moving containers from {random_vessel} at {self.env.now:2f}")
            yield self.env.timeout(C2T_moving_timing)
            print(f"{name} finished moving containers from {random_vessel} at {self.env.now:.2f}")
            self.quay_crane_in_use.append(name) # storing the name of the quay creane which finishes moving container to truck

    def transport_container_to_yard(self, name):
        """Funciton to handle simulation of transportation of container from crane to yard"""
        with self.truck.request() as truck_req:
            crane_name = self.quay_crane_in_use[0]
            del self.quay_crane_in_use[0] # removing one crane at a time to rectify the crane is unloaded in truck.
            yield truck_req
            print(f"{name} starts transporting container from {crane_name} to the yard block at {self.env.now:.2f}")
            yield self.env.timeout(6) #Time to move all containers
            print(f"{name} finishes transporting container form {crane_name} to the yard block {self.env.now:.2f}")

          

def vessel_generator(env, terminal):
    """Function to handle arrival of vessel at berth and call the vessel discharge process"""
    vessel_number = 1
    while True:
        vessel_arrival_time = random.expovariate(lambd = 1 / 300) # 5 Hours average arrival time (converted into minute)
        yield env.timeout(vessel_arrival_time)
        env.process(terminal.vessel_discharge(name=f"Vessel {vessel_number}"))
        vessel_number += 1


def quay_crane_control_process(env, terminal):
    """Function to handle quay crane simulation"""
    quay_crane_number = 1
    while True:
        yield env.timeout(1) # Time to reach the vessel
        if terminal.vessel_in_use and (len(terminal.truck_in_use) != NO_OF_TRUCKS): # Check at least one vessel in waiting after disposing in berth and atleast one truck is available to do the transportaion
            env.process(terminal.move_container_to_truck(name=f"Quay Crane {quay_crane_number}"))
            quay_crane_number = (quay_crane_number % NO_OF_QUAY_CRANE) + 1


def truck_control_process(env, terminal):
    """Function to handle truck simulation"""
    truck_count = 1
    while True:
        yield env.timeout(1) # Time to laod container
        if terminal.quay_crane_in_use: # Check if crane is in use then only call the tranportation event
            env.process(terminal.transport_container_to_yard(name=f"Truck {truck_count}"))
            truck_count = (truck_count % NO_OF_TRUCKS) + 1



# simpy Environment declare
env = sp.Environment()
terminal = ContainerTerminal(env) # objet of the Container Terminal Class


env.process(vessel_generator(env=env, terminal=terminal)) # Call the vessel generator process to keep track of vessel arrival on berth
env.process(quay_crane_control_process(env=env, terminal=terminal)) # Process to handle quay crane to move containers from vessel to truck
env.process(truck_control_process(env=env, terminal=terminal)) # Process to handle truck to move containers from quay cranes to yard blocks

env.run(until=SIMULATION_TIME) # run the simulation enviroment



    

