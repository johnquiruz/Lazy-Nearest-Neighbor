class Driver:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.truck = None

    def assign_truck(self, truck):
        self.truck = truck
        truck.occupied = True



class Truck:
    def __init__(self, id, model):
        self.id = id
        self.model = model
        self.packages = None
        self.max_load = 16
        self.occupied = False
        self.distance_traveled = 0.0



class Package:
    def __init__(self, id, address, city, state, zip_code, deadline, weight, special_note="", location_index=None):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_note = special_note
        self.location_index = location_index
        self.assigned_truck = None
        self.must_deliver_with = []
        self.status = "Held at Hub"