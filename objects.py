SPEED = 18  # mph
HUB = 0     # hub is row 0 in the distance matrix



class Driver:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.truck = None

    def assign_truck(self, truck):
        self.truck = truck
        truck.is_occupied = True



class Truck:
    def __init__(self, id, model):
        self.id = id
        self.model = model
        self.packages = []
        self.max_load = 16
        self.is_occupied = False
        self.needs_loading = False   # True when a driver just took this truck
        self.distance_traveled = 0.0
        self.delivered = 0
        self.time = 480              # minutes since midnight, 480 = 8:00 am
        self.location = HUB          # where the truck is in the distance matrix

    # load packages from the hub
    def load_packages(self, packages):
        for package in packages:
            # take packages meant for this truck or ones no truck has yet
            if package.assigned_truck is self or package.assigned_truck is None:
                if len(self.packages) >= self.max_load:
                    raise ValueError(f"Truck {self.id} is full; can't load package {package.id}")

                # delayed ones get to the hub at 9:05 so truck waits for them
                if package.status == "Delayed":
                    self.time = max(self.time, 545)

                package.assigned_truck = self
                self.packages.append(package)
                package.status = "Loaded"
        print(f"Truck {self.id} loaded, has {len(self.packages)} packages.")



    # NN algorithm: one stop per call, goes to the closest package it can deliver
    # returns False if nothing can be delivered right now
    def deliver_package(self, distance_matrix):
        # skip package 9 until 10:20, thats when the address gets fixed
        ready = []
        for package in self.packages:
            if "wrong address" in package.special_note.lower() and self.time < 620:
                package.status = "Wrong Address"
            else:
                ready.append(package)

        if len(ready) == 0:
            return False

        # packages with a deadline go first, NN only picks between those
        urgent = []
        for package in ready:
            if package.deadline != "EOD":
                urgent.append(package)
        if len(urgent) > 0:
            ready = urgent

        # find the closest package from where the truck is now
        nearest = ready[0]
        shortest = float(distance_matrix[self.location][nearest.location_index])
        for package in ready:
            dist = float(distance_matrix[self.location][package.location_index])
            if dist < shortest:
                shortest = dist
                nearest = package

        # drive there and drop it off
        self.distance_traveled += shortest
        self.time += shortest / SPEED * 60   # miles to minutes
        self.location = nearest.location_index

        nearest.status = "Delivered"
        nearest.delivery_time = self.time
        self.packages.remove(nearest)
        return True



    # drive back to hub, anything left on the truck stays on it
    def return_to_hub(self, distance_matrix):
        dist = float(distance_matrix[self.location][HUB])
        self.distance_traveled += dist
        self.time += dist / SPEED * 60
        self.location = HUB



    # dist traveled and packs delivered
    def report_summary(self):
        clock = f"{int(self.time // 60):02d}:{int(self.time % 60):02d}"
        print(f"Truck {self.id}: {self.delivered} delivered, {self.distance_traveled:.1f} miles, time {clock}")



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
        self.status = "At Hub"
        self.delivery_time = None   # minutes since midnight, set when delivered