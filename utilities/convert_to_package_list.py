import pandas as pd
from objects import Package


# addresses the annoying inconsistent spelling of "station" between excel sheets
def _clean_address(address):
    address = str(address)
    address = address.replace("\n", " ")
    address = " ".join(address.split())
    address = address.lower()
    address = address.replace(" station ", " sta ")
    return address


# finds the index of a package's address in the distance matrix (index indicates address)
# this iterates proportional to the number of addresses in the distance matrix, 
# but the number of addresses is small enough that this is not a performance concern
def find_address_index(package_address, matrix_addresses):
    package_address = _clean_address(package_address)
    # we use a list because multiple addresses will produce multiple matching indices
    matches = [
        index
        for index, matrix_address in enumerate(matrix_addresses)
        if package_address in _clean_address(matrix_address)
    ]

    # we only expect 1:1 mapping between package address and distance matrix address
    if len(matches) != 1:
        raise ValueError(f"Could not uniquely match address: {package_address}")

    return matches[0]


# load the package data from the excel file and associate each package with 
# its index in the distance matrix
def load_packages(matrix_addresses):
    df = pd.read_excel("./dataset/WGUPS_Package_File.xlsx", header=7)
    df.columns = [
        "id",
        "address",
        "city",
        "state",
        "zip_code",
        "deadline",
        "weight",
        "special_note",
    ]
    df["special_note"] = df["special_note"].fillna("") # keep blank excel entries a string instead of nan

    packages = []

    for _, row in df.iterrows():
        # map the package's address to its index in the distance matrix
        # to establish a relationship between the excel sheets on addresses
        location_index = find_address_index(row["address"], matrix_addresses)

        package = Package(
            id=row["id"],
            address=row["address"],
            city=row["city"],
            state=row["state"],
            zip_code=row["zip_code"],
            deadline=row["deadline"],
            weight=row["weight"],
            special_note=row["special_note"],
            location_index=location_index,
        )
        packages.append(package)

    return packages