from ecdsa import SigningKey
from ecdsa import SECP256k1
from hashlib import sha256
import hashlib
import base58

#generate private and public keys using ECDSA
#bitcoin uses the curve SECP256k1
private_key = SigningKey.generate(curve=SECP256k1)
public_key = private_key.get_verifying_key()
string_public_key = public_key.to_string()

#Perform SHA-256 hashing on the public key
sha = hashlib.sha256()
sha.update(string_public_key)
string_public = sha.digest()


# Perform RIPEMD-160 hashing on the result of SHA-256
ripemd160 = hashlib.new('ripemd160')
ripemd160.update(string_public)
sharip = ripemd160.hexdigest()


#add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
main_address = "00" + sharip

#Perform SHA-256 hash on the extended RIPEMD-160 result twice
checksum = sha256(sha256(main_address.decode('hex')).digest()).hexdigest()

# Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
checksum = checksum[:8]
print "checksum: " + checksum

# Add the 4 checksum bytes from stage 7 at the end of extended RIPEMD-160 hash from stage 4. This is the 25-byte binary Bitcoin Address.
main_address = main_address + checksum.upper()

#Convert the result from a byte string into a base58 string using Base58Check encoding. This is the most commonly used Bitcoin Address format
main_address = base58.b58encode(main_address.decode('hex'))


print ("Bitcoin Address: " + main_address)


#you can validate the addresses here: http://lenschulwitz.com/base58
#https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
#https://en.bitcoin.it/wiki/Address