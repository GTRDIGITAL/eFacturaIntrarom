import datetime
import pyotp

# key = pyotp.random_base32()
key ='cedracu'

# print(key)

totp = pyotp.TOTP(key)

print(totp.now())

input_code = input('baga 2fa')
