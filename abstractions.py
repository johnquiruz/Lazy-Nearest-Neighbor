class HashTable:
    def __init__(self, size):
        self.size = size

        # each inner list stores entries that share the same bucket
        self.buckets = [[] for _ in range(size)]

    def insert(self, package_id, package):
        # use the hash as the index of the target bucket
        index = self._hash(package_id)

        # replace the existing package when the id is already stored
        for bucket_index, (stored_id, stored_package) in enumerate(self.buckets[index]):
            if stored_id == package_id:
                self.buckets[index][bucket_index] = (package_id, package)
                return

        # add a new entry to the bucket
        self.buckets[index].append((package_id, package))

    def _hash(self, package_id):
        # convert the package id into a valid bucket index
        return hash(package_id) % self.size

    def get(self, package_id):
        # search only the bucket selected by the hash
        index = self._hash(package_id)

        for stored_id, package in self.buckets[index]:
            if stored_id == package_id:
                return package
        return None

    def remove(self, package_id):
        # search the matching bucket before removing the entry
        index = self._hash(package_id)

        for bucket_index, (stored_id, package) in enumerate(self.buckets[index]):
            if stored_id == package_id:
                del self.buckets[index][bucket_index]
                return True
        return False