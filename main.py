from abstractions import HashTable
from objects import Driver, Truck
from utilities.convert_to_matrix import load_distance_data
from utilities.convert_to_package_list import load_packages

def find_numbers(message):
    # saves digits in a string as a list of integers and returns the list
    return [int(word.strip(",")) for word in message.split() if word.strip(",").isdigit()]

# SETUP: ------------------------------
# map package addresses to their index in the distance matrix for routing
matrix_addresses, distance_matrix = load_distance_data()
packages = load_packages(matrix_addresses)

# store package references by id for looking up state
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
# check for any special instructions before placing package on truck
next_truck = 0
for package in packages:
    note = package.special_note.lower()

    if "delivered with" in note:
        package.must_deliver_with = find_numbers(note)

    elif "on truck" in note:
        truck_number = find_numbers(note)[0]
        package.assigned_truck = trucks[truck_number - 1]
        package.assigned_truck.packages.append(package)

    elif "delayed" in note:
        package.status = "Delayed"

    else:
        # place each package on the next available truck
        while next_truck < len(trucks) and len(trucks[next_truck].packages) == trucks[next_truck].max_load:
            next_truck += 1

        if next_truck == len(trucks):
            raise ValueError("No truck has available capacity")

        package.assigned_truck = trucks[next_truck]
        package.assigned_truck.packages.append(package)
        package.status = "At Hub"

# drivers get behind the wheel
driver1.assign_truck(truck1)
driver2.assign_truck(truck2)

# TEST: 
print(len(truck1.packages))
print(len(truck2.packages))
print(len(truck3.packages))
print(len(packages)) # TODO: the packages that were loaded should be removed from the packages list, but they are not. This is a bug that needs to be fixed.


# ROUTING: ------------------------------
# for package in packages:
#     print(package.status)

# for bucket in package_table.buckets:
    # for package_id, package in bucket:
        # print(f"Package ID: {package.id}, Address: {package.address}, Location Index: {package.location_index}, Status: {package.status}")