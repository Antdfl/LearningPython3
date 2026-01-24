def cesar_encrypt(plaintext, shift):
    text = '' 
    for char in plaintext:
        #print(char)
        if not char.isalpha():
            continue
        char = char.upper()
        #print(char)
        code = ord(char) + shift
        #print(code)
        if code > ord('Z'):
            code = ord('A')
        elif code < ord('A'):
            code = ord('Z')
        #print(chr(code))
        text += chr(code)
    return text


def cesar_decrypt(ciphertext, shift):
    return cesar_encrypt(ciphertext, -shift)
# Example usage
# plaintext = "Hello, World!"
shift = 1
plaintext = input("Enter your message: ")
encrypted = cesar_encrypt(plaintext, shift)
print ("Encrypted:", encrypted)
decrypted = cesar_decrypt(encrypted, shift)
print ("Decrypted:", decrypted)