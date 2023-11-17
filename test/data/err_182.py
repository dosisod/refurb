import hashlib
from hashlib import (
    blake2b,
    blake2s,
    md5,
    sha1,
    sha3_224,
    sha3_256,
    sha3_384,
    sha3_512,
    sha224,
)
from hashlib import sha256
from hashlib import sha256 as hash_algo
from hashlib import sha384, sha512, shake_128, shake_256

# these will match

h1 = blake2b()
h1.update(b"data")

h2 = blake2s()
h2.update(b"data")

h3 = md5()
h3.update(b"data")

h4 = sha1()
h4.update(b"data")

h5 = sha224()
h5.update(b"data")

h6 = sha256()
h6.update(b"data")

h7 = sha384()
h7.update(b"data")

h8 = sha3_224()
h8.update(b"data")

h9 = sha3_256()
h9.update(b"data")

h10 = sha3_384()
h10.update(b"data")

h11 = sha3_512()
h11.update(b"data")

h12 = sha512()
h12.update(b"data")

h13 = shake_128()
h13.update(b"data")

h14 = shake_256()
h14.update(b"data")

h15 = hashlib.sha256()
h15.update(b"data")

h16 = hash_algo()
h16.update(b"data")


# these will not

h17 = sha256()
h17.digest()

h18 = sha256(b"data")
h18.update(b"more data")
h18.digest()

h19 = sha256()
pass
h19.digest()

class Hash:
    def update(self, data: bytes) -> None:
        return None


h20 = Hash()
h20.update(b"data")
