from abstractions import HashTable
from objects import Driver, Truck
from utilities.convert_to_matrix import load_distance_data
from utilities.convert_to_package_list import load_packages

# returns digits in the special note as a list of integers
def find_numbers(message):
    return [int(word.strip(",")) for word in message.split() if word.strip(",").isdigit()]

# SETUP: ------------------------------
# map package addresses to their index in the distance matrix for routing
matrix_addresses, distance_matrix = load_distance_data()
packages = load_packages(matrix_addresses)

# store package references by id to a table for looking up state
package_table = HashTable(size=53)
for package in packages:
    package_table.insert(package.id, package)

# pre-processing before trucks are loaded
driver1 = Driver(id=1, name="Driver 1")
driver2 = Driver(id=2, name="Driver 2")

truck1 = Truck(id=1, model="Truck 1")
truck2 = Truck(id=2, model="Truck 2")
truck3 = Truck(id=3, model="Truck 3")
trucks = [truck1, truck2, truck3]

truck1.packages = []
truck2.packages = []
truck3.packages = []




# LOADING TRUCKS: ------------------------------

# 1 load packages designated for specific trucks
for package in packages:
    note = package.special_note.lower()

    # gets truck id from the special note
    if "on truck" in note:
        truck = trucks[find_numbers(note)[0] - 1]

        if len(truck.packages) >= truck.max_load:
            raise ValueError(f"Truck {truck.id} is full; can't load package {package.id}")

        # package is assigned to truck and then loaded
        package.assigned_truck = truck
        truck.packages.append(package)
        package.status = "Loaded"

# update the packages at the hub by removing packages marked "loaded"
packages[:] = [p for p in packages if p.status is not "Loaded"]

# 2 identify bundled packages and load them together
group_ids = set()
for package in packages:
    note = package.special_note.lower()
    if "delivered with" in note:
        group_ids.add(package.id)
        group_ids.update(find_numbers(note))

# group actual packages based on ids
group = [p for p in packages if p.id in group_ids]

# find truck that has enough room for group of packages and actually load them
for truck in trucks:
    if len(truck.packages) + len(group) <= truck.max_load:
        for package in group:
            package.assigned_truck = truck
            truck.packages.append(package)
            package.status = "Loaded"
        break

# update the packages at the hub by removing packages marked "loaded"
packages[:] = [p for p in packages if p.status is not "Loaded"]

# load remaining packages to next available truck
next_truck = 0
for package in packages:
    note = package.special_note.lower()

    if "delayed" in note:
        # this package stays at hub 
        package.status = "Delayed"

    else:
        # skip trucks that are full or reach the end of the truck list
        while next_truck < len(trucks) and len(trucks[next_truck].packages) >= trucks[next_truck].max_load:
            next_truck += 1

        # notify dev no more trucks can be loaded
        if next_truck >= len(trucks):
            raise ValueError("No truck has available capacity")

        # put package on the next truck with room
        package.assigned_truck = trucks[next_truck]
        package.assigned_truck.packages.append(package)
        package.status = "Loaded"

# update the packages at the hub by removing packages marked "loaded"
packages[:] = [p for p in packages if p.status is not "Loaded"]

# drivers get behind the wheel
driver1.assign_truck(truck1)
driver2.assign_truck(truck2)

print(f"Packages left: {len(packages)}")
for package in packages:
    print(f"Package: {package.id}, Status: {package.status}, Deadline: {package.deadline}, Special NOte: {package.special_note}")