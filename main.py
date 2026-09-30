from abstractions import HashTable
from objects import Driver, Truck
from utilities.convert_to_matrix import load_distance_data
from utilities.convert_to_package_list import load_packages

# returns digits in the special note as a list of integers
def find_numbers(message):
    return [int(word.strip(",")) for word in message.split() if word.strip(",").isdigit()]

# SETUP: ------------------------------

# build a destination and routing map by mapping a relation between distance and package sheets
matrix_addresses, distance_matrix = load_distance_data()
packages = load_packages(matrix_addresses)

# create a hash table for easy lookups
package_table = HashTable(size=53)
for package in packages:
    package_table.insert(package.id, package)

# create objects
driver1 = Driver(id=1, name="Driver 1")
driver2 = Driver(id=2, name="Driver 2")

truck1 = Truck(id=1, model="Truck 1")
truck2 = Truck(id=2, model="Truck 2")
truck3 = Truck(id=3, model="Truck 3")
trucks = [truck1, truck2, truck3]



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
packages[:] = [p for p in packages if p.status != "Loaded"]



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
packages[:] = [p for p in packages if p.status != "Loaded"]


# 3 leave the delayed packages at the hub
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

        # 4 load remaining packages to next available truck
        package.assigned_truck = trucks[next_truck]
        package.assigned_truck.packages.append(package)
        package.status = "Loaded"

# update the packages at the hub by removing packages marked "loaded"
packages[:] = [p for p in packages if p.status != "Loaded"]




# EN ROUTE -----------------------------------------------------

# remember: time is minutes since midnight
ADDRESS_FIX_TIME = 620   # 10:20 am, package 9 gets its real address

# turns minutes into text like 09:05
def time_to_text(minutes):
    return f"{int(minutes // 60):02d}:{int(minutes % 60):02d}"

# lookup package 9 in hash table
package9 = package_table.get(9)

# fix package 9 address once the truck carrying it hits 10:20
def fix_package_9(truck):
    if package9.assigned_truck is truck and truck.time >= ADDRESS_FIX_TIME and package9.address != "410 S State St":
        package9.address = "410 S State St"
        package9.zip_code = "84111"
        for i in range(len(matrix_addresses)):
            if "410 S State St" in matrix_addresses[i]:   # check it matches your matrix spelling
                package9.location_index = i

# driver leaves current truck and takes the next free truck that still has work
def occupy_next_truck(current_truck):
    for next_truck in trucks:
        if next_truck.is_occupied is False and (len(next_truck.packages) > 0 or len(packages) > 0):
            next_truck.is_occupied = True
            next_truck.needs_loading = True
            # next truck cant leave before the driver gets back
            next_truck.time = max(next_truck.time, current_truck.time)
            current_truck.is_occupied = False
            return

    # no other truck has work
    if len(current_truck.packages) == 0:
        current_truck.is_occupied = False   # driver is done for the day
    else:
        # only package 9 left, wait at the hub for 10:20
        current_truck.time = max(current_truck.time, ADDRESS_FIX_TIME)


driver1.assign_truck(truck1)
driver2.assign_truck(truck2)

# start route
while True:
    for truck in trucks:
        if not truck.is_occupied:
            continue

        # make sure a freshly occupied truck loads
        if truck.needs_loading:
            truck.load_packages(packages)
            packages[:] = [p for p in packages if p.status != "Loaded"]
            truck.needs_loading = False

        fix_package_9(truck)

        for package in truck.packages:
            if package.status == "Loaded":
                package.status = "En Route"

        # executes NN algorithm, skips 9 before 10:20
        if truck.deliver_package(distance_matrix):
            truck.delivered += 1
            # lookups and status checks here -----

        elif len(truck.packages) == 0:
            truck.return_to_hub(distance_matrix)
            occupy_next_truck(truck)

        elif truck.packages[0].status == "Wrong Address":
            truck.return_to_hub(distance_matrix)
            truck.packages[0].status = "Loaded"   # sitting on the truck at the hub
            occupy_next_truck(truck)

    packages_delivered = truck1.delivered + truck2.delivered + truck3.delivered
    if packages_delivered >= 40:
        break


# TEST RUN: ------------------------------
for truck in trucks:
    truck.report_summary()

total_miles = truck1.distance_traveled + truck2.distance_traveled + truck3.distance_traveled
print(f"Total miles: {total_miles:.1f}")  # has to be under 140

# check every package got delivered and when
for package_id in range(1, 41):
    # look up package information using hash table
    package = package_table.get(package_id)
    print(f"Package {package.id}, Truck {package.assigned_truck.id}, Status: {package.status}, Delivered: {time_to_text(package.delivery_time)}, Deadline: {package.deadline}")