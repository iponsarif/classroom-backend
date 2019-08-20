shift = 3
alphanumeric = 'abcdefghijlkmnopqrstuvwxyz0123456789'
listAlphanumeric = list(alphanumeric)

def encrypt(password):
    encryptedPassword = ""
    for i in range(len(password)):
        charPosition = listAlphanumeric.index(password[i])
        newPosition = (charPosition + shift) % len(listAlphanumeric)
        encryptedPassword += listAlphanumeric[newPosition]
    
    return encryptedPassword

def decrypt(password):
    encryptedPassword = ""
    for i in range(len(password)):
        charPosition = listAlphanumeric.index(password[i])
        newPosition = (charPosition - shift) % len(listAlphanumeric)
        encryptedPassword += listAlphanumeric[newPosition]
    
    return encryptedPassword