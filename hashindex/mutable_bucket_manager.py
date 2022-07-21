from sortedcontainers import SortedDict

from hashindex.mutable_buckets import DictBucket, HashBucket
from hashindex.constants import HASH_MIN, HASH_MAX

from typing import Union

"""
Both HashIndex and FrozenHashIndex use SortedDict to hold their buckets.
Due to the mutability, HashIndex does lots of creation / deletion of buckets, and that gets complicated.
So it's in a separate class to help manage the complexity and provide easy testing.
"""


class MutableBucketManager:
    def __init__(self):
        self.buckets = SortedDict()

    def remove_bucket(self, bkey):
        """
        Remove a bucket.

        If this creates a gap in the [HASH_MIN..HASH_MAX] space that is not covered by a bucket, fix that first.
        """
        left_key, right_key = self.get_neighbors(bkey)
        if left_key is not None and isinstance(self.buckets[left_key], HashBucket):
            # Case 1: There is a hash bucket to the left.
            # Just delete this bucket; the gap is covered.
            del self.buckets[bkey]
        else:
            # Case 2: The left neighbor is nonexistent, or is a DictBucket. Let's look right.
            if right_key is not None and isinstance(
                self.buckets[right_key], HashBucket
            ):
                # Case 2a. The right neighbor is a hash bucket. We can expand it leftwards to cover the gap.
                b = self.buckets[right_key]
                del self.buckets[right_key]
                self.buckets[bkey] = b
            else:
                # Case 2b. The right neighbor is nonexistent, or is a DictBucket.
                # Deletion of this bucket is not allowed, even if empty.
                # All we'll do is demote this bucket to a HashBucket if it's a DictBucket.
                if isinstance(self.buckets[bkey], DictBucket):
                    self.buckets[bkey] = HashBucket()

    def get_neighbors(self, bkey):
        """
        Find the key of the buckets on the left and right of this one, if any.

        Used when splitting or removing buckets, as part of ensuring there are no gaps in the hashspace.
        """
        if len(self.buckets) <= 1:
            return None, None
        if bkey == HASH_MIN:
            left_key = None
        else:
            left_idx = self.buckets.bisect_left(bkey) - 1
            if left_idx < 0:
                # this can happen if the bucket at HASH_MIN was just deleted and we're
                # about to make a new neighbor for it.
                left_key = None
            else:
                left_key, _ = self.buckets.peekitem(left_idx)
        if bkey == HASH_MAX:
            right_key = None
        else:
            try:
                right_idx = self.buckets.bisect_right(bkey)
                right_key, _ = self.buckets.peekitem(right_idx)
            except IndexError:
                right_key = None
        return left_key, right_key

    def get_bucket_key_for(self, val_hash):
        list_idx = self.buckets.bisect_right(val_hash) - 1
        k, _ = self.buckets.peekitem(list_idx)
        return k

    def __getitem__(self, bkey):
        return self.buckets[bkey]

    def __setitem__(self, bkey, value):
        self.buckets[bkey] = value

    def __delitem__(self, bkey):
        del self.buckets[bkey]

    def pop(self, bkey) -> Union[HashBucket, DictBucket]:
        b = self.buckets[bkey]
        del self.buckets[bkey]
        return b