'''
John Quiruz
Student ID: 011843486
'''
from abstractions import HashTable
from objects import Driver, Truck
from utilities.convert_to_matrix import load_distance_data
from utilities.convert_to_package_list import load_packages_from_excel

# remember: time is minutes since midnight
DELAYED_ARRIVAL = 545    # 9:05 am, delayed packages get to the hub
ADDRESS_FIX_TIME = 620   # 10:20 am, package 9 gets its real address
HUB = 0                  # hub is row 0 in the distance matrix

# returns digits in the special note as a list of integers
def find_numbers(message):
    return [int(word.strip(",")) for word in message.split() if word.strip(",").isdigit()]

# turns minutes into text like human readable time
def time_to_text(minutes):
    return f"{int(minutes // 60):02d}:{int(minutes % 60):02d}"

# turns human readable time into minutes since midnight
def text_to_time(text):
    hours, minutes = text.split(":")
    return int(hours) * 60 + int(minutes)

def load_status_check(truck):
    if len(truck.packages) == truck.max_load:
        print(f"Truck {truck.id} fully loaded, ", end="")
    else:
        print(f"Truck {truck.id} loaded, ", end="")
    print(f"has {len(truck.packages)} packages.")


# SETUP: ------------------------------

# build a destination and routing map by mapping a relation between distance and package sheets
matrix_addresses, distance_matrix = load_distance_data()
packages = load_packages_from_excel(matrix_addresses)
TOTAL_PACKAGES = len(packages)

# create a hash table for easy lookups
# Insert function is technically inserting every attribute of the package by encapsulation (object: package)
package_table = HashTable(size=53)
for package in packages:
    package_table.insert(package.id, package) # insert package which encapsulates all attributes

# lookup package 9 in hash table and keep its old address for status checks before 10:20
package9 = package_table.get(9)
package9_old_address = package9.address
package9_old_zip = package9.zip_code

# create objects
driver1 = Driver(id=1, name="Driver 1")
driver2 = Driver(id=2, name="Driver 2")

truck1 = Truck(id=1, model="Truck 1")
truck2 = Truck(id=2, model="Truck 2")
truck3 = Truck(id=3, model="Truck 3")
trucks = [truck1, truck2, truck3]



# LOADING TRUCKS: ------------------------------

# package is assigned to truck and then loaded, stops if truck is full
def load_onto_truck(package, truck):
    if len(truck.packages) >= truck.max_load:
        raise ValueError(f"Truck {truck.id} is full; can't load package {package.id}")
    package.assigned_truck = truck
    truck.packages.append(package)
    package.status = "Loaded"

# update the packages at the hub by removing packages marked "loaded"
def update_hub():
    packages[:] = [p for p in packages if p.status != "Loaded"]



# four special conditions to load trucks
# condition 1: packages that have special assignment to specific truck
for package in packages:
    note = package.special_note.lower()

    # gets truck id from the special note
    if "on truck" in note:
        load_onto_truck(package, trucks[find_numbers(note)[0] - 1])
update_hub()


# condition 2: identify bundled packages that must be loaded together
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
            load_onto_truck(package, truck)
        break
update_hub()


# condition 3: packages with deadlines should be loaded first onto truck 1
for package in packages:
    if package.deadline != "EOD" and "delayed" not in package.special_note.lower():
        load_onto_truck(package, truck1)
update_hub()


# condition 4: delayed packages go on truck 2, truck 2 waits at the hub until they show up
truck2.time = DELAYED_ARRIVAL
for package in packages:
    if "delayed" in package.special_note.lower():
        load_onto_truck(package, truck2)
update_hub()


# load remaining packages to next available truck
next_truck = 0
for package in packages:
    # skip trucks that are full or reach the end of the truck list
    while next_truck < len(trucks) and len(trucks[next_truck].packages) >= trucks[next_truck].max_load:
        next_truck += 1

    # notify dev no more trucks can be loaded
    if next_truck >= len(trucks):
        raise ValueError("No truck has available capacity")

    load_onto_truck(package, trucks[next_truck])
update_hub()


print("\nLOADING COMPLETE - SUMMARY:")
load_status_check(truck1)
load_status_check(truck2)



# EN ROUTE -----------------------------------------------------

# fix package 9 address once the truck carrying it hits 10:20
def fix_package_9(truck):
    if package9.assigned_truck is truck and truck.time >= ADDRESS_FIX_TIME and package9.address != "410 S State St":
        package9.address = "410 S State St"
        package9.zip_code = 84111
        # find the new address in the distance matrix
        for i in range(len(matrix_addresses)):
            if "410 S State St" in matrix_addresses[i]:
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

# pick the occupied truck thats furthest behind in time so everything happens in clock order
def get_earliest_truck():
    earliest = None
    for truck in trucks:
        if truck.is_occupied and (earliest is None or truck.time < earliest.time):
            earliest = truck
    return earliest

# runs the whole day until every package is delivered
def run_deliveries():
    while True:
        truck = get_earliest_truck()

        # no drivers left on any truck
        if truck is None:
            break

        # make sure a freshly occupied truck loads
        if truck.needs_loading:
            truck.load_packages(packages)
            update_hub()
            truck.needs_loading = False

        fix_package_9(truck)

        # truck is leaving the hub, save when each package on it left
        if truck.location == HUB:
            for package in truck.packages:
                package.depart_time = truck.time

        for package in truck.packages:
            if package.status == "Loaded":
                package.status = "En Route"

        # executes NN algorithm, skips 9 before 10:20
        if truck.deliver_package(distance_matrix):
            truck.delivered += 1

        elif len(truck.packages) == 0:
            truck.return_to_hub(distance_matrix)
            occupy_next_truck(truck)

        elif truck.packages[0].status == "Wrong Address":
            truck.return_to_hub(distance_matrix)
            truck.packages[0].status = "Loaded"   # sitting on the truck at the hub

            # if its already past 10:20 the driver gets the new address and keeps going
            if truck.time < ADDRESS_FIX_TIME:
                occupy_next_truck(truck)

        packages_delivered = truck1.delivered + truck2.delivered + truck3.delivered
        if packages_delivered >= TOTAL_PACKAGES:
            break


driver1.assign_truck(truck1)
driver2.assign_truck(truck2)
run_deliveries()



# STATUS LOOKUPS: ------------------------------

# checks status of package at anytime
def get_status(package, check_time):
    if "delayed" in package.special_note.lower() and check_time < DELAYED_ARRIVAL:
        return "Delayed"
    if check_time < package.depart_time:
        return "At Hub"
    if check_time < package.delivery_time:
        return f"En Route (left hub at {time_to_text(package.depart_time)})"
    return f"Delivered at {time_to_text(package.delivery_time)}"

# old address and zip code are saved for package 9 because only the newer state is saved
# after the simulation runs, so we must save the original field values
def get_address(package, check_time):
    if package is package9 and check_time < ADDRESS_FIX_TIME:
        return package9_old_address, package9_old_zip
    return package.address, package.zip_code

# print all fields for a given package at anytime
def print_package(package, check_time):
    address, zip_code = get_address(package, check_time)
    print(f"Package {package.id} | Truck {package.assigned_truck.id} | {address}, {package.city}, {zip_code} | "
          f"Deadline: {package.deadline} | Weight: {package.weight} | {get_status(package, check_time)}")

def get_total_miles():
    total = 0
    for truck in trucks:
        total += truck.distance_traveled
    return total

# asks for a time until the user types one that works
def ask_for_time():
    while True:
        try:
            return text_to_time(input("Enter a time (HH:MM, 24 hour): "))
        except ValueError:
            print("Time has to look like 09:30 or 13:00.")



# SAMPLE RUN/INTERFACE: ------------------------------
'''
LOADING COMPLETE - SUMMARY:
Truck 1 fully loaded, has 16 packages.
Truck 2 fully loaded, has 16 packages.
Truck 3 loaded, has 8 packages.

ROUTING COMPLETE - SUMMARY:
Truck 1: 16 delivered, 38.6 miles, time 10:08
Truck 2: 16 delivered, 42.5 miles, time 11:26
Truck 3: 8 delivered, 27.5 miles, time 11:40
All 40 packages delivered. Total mileage: 108.6

MAIN MENU:
[1] Status of all packages at a time
[2] Status of one package at a time
[3] Total mileage
[4] Exit
Choose an option: 2
Enter a package ID: 9
Enter a time (HH:MM, 24 hour): 10:00
Package 9 | Truck 2 | 300 State St, Salt Lake City, 84103 | Deadline: EOD | Weight: 2 | En Route (left hub at 09:05)

Choose an option: 2
Enter a package ID: 9
Enter a time (HH:MM, 24 hour): 11:00
Package 9 | Truck 2 | 410 S State St, Salt Lake City, 84111 | Deadline: EOD | Weight: 2 | Delivered at 10:26

Choose an option: 3
Total mileage: 108.6
'''

print("\nROUTING COMPLETE - SUMMARY:")
for truck in trucks:
    truck.report_summary()
print(f"All {TOTAL_PACKAGES} packages delivered. Total mileage: {get_total_miles():.1f}")

while True:
    print("\nMAIN MENU:")
    print("[1] Status of all packages at a time")
    print("[2] Status of one package at a time")
    print("[3] Total mileage")
    print("[4] Exit")
    choice = input("Choose an option: ")

    if choice == "1":
        check_time = ask_for_time()
        # packages grouped by truck so each truck shows up together
        for truck in trucks:
            print(f"\n--- Truck {truck.id} ---")
            for package_id in range(1, TOTAL_PACKAGES + 1):
                package = package_table.get(package_id)
                if package.assigned_truck is truck:
                    print_package(package, check_time)

    elif choice == "2":
        package = None
        try:
            package = package_table.get(int(input("Enter a package ID: ")))
        except ValueError:
            # don't do anything, leave package null
            pass
        if package is None:
            print("No package with that ID.")
            continue
        print_package(package, ask_for_time())

    elif choice == "3":
        print(f"Total mileage: {get_total_miles():.1f}")

    elif choice == "4":
        break

    else:
        print("\nError: Please choose options 1-4")