import random
import os

# RSA operations

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def generate_prime_number():
    while True:
        num = random.randint(100, 500)  # Adjust the range for larger prime numbers
        if is_prime(num):
            return num

def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def generate_keypair(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Both numbers must be prime.")
    elif p == q:
        raise ValueError("p and q cannot be equal.")
    
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 2
    while gcd(e, phi) != 1:
        e += 1

    d = mod_inverse(e, phi)

    return ((e, n), (d, n))

def encrypt(public_key, plaintext):
    e, n = public_key
    cipher = [str(pow(ord(char), e, n)) for char in plaintext]
    return ' '.join(cipher)

def encrypt_file(public_key, file_name):
    try:
        with open(file_name, 'r') as file:
            plaintext = file.read()
        ciphertext = encrypt(public_key, plaintext)
        return ciphertext
    except FileNotFoundError:
        print(f"File '{file_name}' not found!")
        return None

def main():
    public_key = None
    private_key = None
    ciphertext = None
    decrypted_message = None

    while True:
        #print("\nChoose an option:")
        #print("1. Generate Key Pair | 2. Encrypt | 3. Decrypt | 4. Save Encrypted Text to File | 5. Read Ciphertext from File and Decrypt | 6. Save Decrypted Text to File | 7. Clear Output | 8. Read Plaintext from File and Encrypt | 9. Exit")
        print("1. Generete Keys")
        print("2. Encrypt")
        print("3. Decrypt")
        print("4. Save Encrypted Text to File")
        #print("5. Read Ciphertext from File and Decrypt")
        print("5. Save Decrypted Text to File")
        print("6. Clear Output")
        print("7. Read Plaintext from File and Encrypt")  # New option
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            p = generate_prime_number()
            q = generate_prime_number()
            #print("Generated prime numbers:")
            print("p =", p)
            print("q =", q)
            public_key, private_key = generate_keypair(p, q)
            #print("Keys generated successfully!")
            print("Public Key (e, n):", public_key)
            print("Private Key (d, n):", private_key)

        elif choice == '2':
            if public_key is None:
                print("Please generate keys first!")
                continue
            plaintext = input("Enter the message to encrypt: ")
            ciphertext = encrypt(public_key, plaintext)
            print("Encrypted message:", ciphertext)

        elif choice == '3':
            print("private key for decryption:")
            d = int(input("Enter private key 'd': "))
            n = int(input("Enter modulus 'n': "))

            file_name = input("Enter ciphertext file name (leave blank if not): ")

            try:
                if file_name:
                    with open(file_name, 'r') as file:
                        ciphertext = file.read()
                    print(f"Ciphertext read from {file_name}")
                else:
                    ciphertext = input("Enter the ciphertext: ")

                decrypted = ''.join([chr(pow(int(char), d, n)) for char in ciphertext.split()])
                print("Decrypted message:", decrypted)

            except FileNotFoundError:
                print(f"File '{file_name}' not found!")
                continue

        elif choice == '4':
            if ciphertext is None:
                print("No encrypted text available to save.")
                continue
            file_name = input("Enter file name to save encrypted text: ")
            try:
                with open(file_name, 'w') as file:
                    file.write(ciphertext)
                print(f"Content saved to {file_name}")
            except IOError:
                print(f"Failed to write to {file_name}")

        #elif choice == '5':
        #    print("private key for decryption:")
        #    d = int(input("Enter private key 'd': "))
        #    n = int(input("Enter modulus 'n': "))
        #
        #    file_name = input("Enter ciphertext file name: ")
        #
        #    try:
        #        with open(file_name, 'r') as file:
        #            ciphertext = file.read()
        #        print(f"Ciphertext read from {file_name}")
        #
        #        decrypted = ''.join([chr(pow(int(char), d, n)) for char in ciphertext.split()])
        #        print("Decrypted message:", decrypted)
        #
        #    except FileNotFoundError:
        #        print(f"File '{file_name}' not found!")
        #        continue

        elif choice == '5':
            if decrypted_message is None:
                print("No decrypted text available to save.")
                continue
            file_name = input("Enter file name to save decrypted text: ")
            try:
                with open(file_name, 'w') as file:
                    file.write(decrypted_message)
                print(f"Content saved to {file_name}")
            except IOError:
                print(f"Failed to write to {file_name}")

        elif choice == '6':
            os.system('cls' if os.name == 'nt' else 'clear')

        elif choice == '7':
            if public_key is None:
                print("Please generate keys first!")
                continue
            file_name = input("Enter file name with plaintext to encrypt: ")
            ciphertext = encrypt_file(public_key, file_name)
            if ciphertext:
                print("Encrypted message:", ciphertext)

        elif choice == '8':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()

