# Package hash table using separate chaining for collisions.


class HashTable:
    def __init__(self, size):
        self.size = size
        self.buckets = [[] for _ in range(size)] # bucket implementation: array instead of LL
                                                 # for performance
    def insert(self, package_id, package):
        # get hash 
        index = self._hash(package_id)

        # if existing package id is found, replace it with parameters
        for bucket_index, (stored_id, stored_package) in enumerate(self.buckets[index]):
            if stored_id == package_id:
                self.buckets[index][bucket_index] = (package_id, package)
                return

        # if package id doesn't exist, add to the bucket
        self.buckets[index].append((package_id, package))

    def _hash(self, package_id):
        return hash(package_id) % self.size

    def get(self, package_id):
        index = self._hash(package_id)
        for stored_id, package in self.buckets[index]:
            if stored_id == package_id:
                return package
        return None

    def remove(self, package_id):
        index = self._hash(package_id)
        for bucket_index, (stored_id, package) in enumerate(self.buckets[index]):
            if stored_id == package_id:
                del self.buckets[index][bucket_index]
                return True
        return False