INPUT_FILE = "raw_text.txt"
ENCRYPTED_FILE = "encrypted_text.txt"
DECRYPTED_FILE = "decrypted_text.txt"


def _encrypt_char(ch, shift1, shift2):

    shift = (shift1 + shift2) % 26

    if ch.islower():
        offset = ord(ch) - ord('a')
        return chr((offset + shift) % 26 + ord('a'))

    elif ch.isupper():
        offset = ord(ch) - ord('A')
        return chr((offset + shift) % 26 + ord('A'))

    else:
        return ch


def _decrypt_char(ch, shift1, shift2):

    shift = (shift1 + shift2) % 26

    if ch.islower():
        offset = ord(ch) - ord('a')
        return chr((offset - shift) % 26 + ord('a'))

    elif ch.isupper():
        offset = ord(ch) - ord('A')
        return chr((offset - shift) % 26 + ord('A'))

    else:
        return ch


def encrypt(shift1, shift2):

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    encrypted = ''.join(_encrypt_char(ch, shift1, shift2) for ch in text)

    with open(ENCRYPTED_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted)

    return encrypted


def decrypt(shift1, shift2):

    with open(ENCRYPTED_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    decrypted = ''.join(_decrypt_char(ch, shift1, shift2) for ch in text)

    with open(DECRYPTED_FILE, "w", encoding="utf-8") as f:
        f.write(decrypted)

    return decrypted


def main():

    print("=" * 50)
    print("TEXT ENCRYPTION / DECRYPTION PROGRAM")
    print("=" * 50)

    shift1 = int(input("Enter shift1: "))
    shift2 = int(input("Enter shift2: "))

    encrypted_text = encrypt(shift1, shift2)
    decrypted_text = decrypt(shift1, shift2)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        original = f.read()

    print("\nOriginal Text:")
    print(original)

    print("\nEncrypted Text:")
    print(encrypted_text)

    print("\nDecrypted Text:")
    print(decrypted_text)

    if original == decrypted_text:
        print("\n✓ Decryption Successful (Original Restored)")
    else:
        print("\n✗ Error in Decryption")


if __name__ == "__main__":
    main()
