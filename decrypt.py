from Crypto.Cipher import AES

key = b"3860CE6BE77DF41BF0B3F3B408BF37C0"
iv  = bytes.fromhex("00000000000000000000000000000000")

with open("WordFile", 'rb') as file:
    data = file.read()

cipher = AES.new(key, AES.MODE_CBC, iv)

d = cipher.decrypt(data)

print(d.decode())