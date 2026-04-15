"""
Text Encryption / Decryption Program
=====================================
Encryption rules:
  Lowercase (a-m): shift FORWARD  by shift1 * shift2  (mod 26)
  Lowercase (n-z): shift BACKWARD by shift1 + shift2  (mod 26)
  Uppercase (A-M): shift BACKWARD by shift1           (mod 26)
  Uppercase (N-Z): shift FORWARD  by shift2 ** 2      (mod 26)
  All other chars: unchanged

Note on collisions:
  Certain (shift1, shift2) combinations cause two different plaintext letters
  to encrypt to the same ciphertext letter.  When that happens, perfect
  decryption is impossible for those characters.  The program detects this
  condition and warns the user before proceeding.
"""

INPUT_FILE      = "raw_text.txt"
ENCRYPTED_FILE  = "encrypted_text.txt"
DECRYPTED_FILE  = "decrypted_text.txt"


# ── encryption ────────────────────────────────────────────────────────────────

def _encrypt_char(ch: str, shift1: int, shift2: int) -> str:
    """Return the encrypted version of a single character."""
    if ch.islower():
        offset = ord(ch) - ord('a')          # 0-25
        if offset <= 12:                      # a-m  (first half)
            new_offset = (offset + shift1 * shift2) % 26
        else:                                 # n-z  (second half)
            new_offset = (offset - (shift1 + shift2)) % 26
        return chr(new_offset + ord('a'))

    elif ch.isupper():
        offset = ord(ch) - ord('A')          # 0-25
        if offset <= 12:                      # A-M  (first half)
            new_offset = (offset - shift1) % 26
        else:                                 # N-Z  (second half)
            new_offset = (offset + shift2 ** 2) % 26
        return chr(new_offset + ord('A'))

    else:
        return ch                             # spaces, digits, symbols …


# ── collision detection ───────────────────────────────────────────────────────

def check_collisions(shift1: int, shift2: int) -> dict:
    """
    Build forward (plain->cipher) maps for lowercase and uppercase and detect
    any ciphertext letter produced by more than one plaintext letter.

    Returns a dict:
        'lower': list of (plain1, plain2, cipher_char)
        'upper': list of (plain1, plain2, cipher_char)
    """
    def _find(start):
        seen = {}
        cols = []
        for offset in range(26):
            plain = chr(offset + ord(start))
            enc   = _encrypt_char(plain, shift1, shift2)
            if enc in seen:
                cols.append((seen[enc], plain, enc))
            else:
                seen[enc] = plain
        return cols

    return {'lower': _find('a'), 'upper': _find('A')}


# ── decryption ────────────────────────────────────────────────────────────────

def _build_decrypt_table(shift1: int, shift2: int) -> dict:
    """
    Build a cipher-char -> plain-char reverse-lookup table by inverting the
    full encryption map.  When a collision exists the first original letter
    encountered wins (preserving as much information as possible).
    """
    table = {}
    for offset in range(26):
        for start in ('a', 'A'):
            plain = chr(offset + ord(start))
            enc   = _encrypt_char(plain, shift1, shift2)
            if enc not in table:          # first-seen wins for collisions
                table[enc] = plain
    return table


def decrypt(shift1: int, shift2: int) -> None:
    """Read ENCRYPTED_FILE, decrypt contents, write to DECRYPTED_FILE."""
    with open(ENCRYPTED_FILE, 'r', encoding='utf-8') as fh:
        ciphertext = fh.read()

    table     = _build_decrypt_table(shift1, shift2)
    plaintext = ''.join(table.get(ch, ch) for ch in ciphertext)

    with open(DECRYPTED_FILE, 'w', encoding='utf-8') as fh:
        fh.write(plaintext)

    print(f"[✓] Decrypted  '{ENCRYPTED_FILE}'  ->  '{DECRYPTED_FILE}'")


# ── main functions ────────────────────────────────────────────────────────────

def encrypt(shift1: int, shift2: int) -> None:
    """Read INPUT_FILE, encrypt contents, write to ENCRYPTED_FILE."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as fh:
        plaintext = fh.read()

    ciphertext = ''.join(_encrypt_char(ch, shift1, shift2) for ch in plaintext)

    with open(ENCRYPTED_FILE, 'w', encoding='utf-8') as fh:
        fh.write(ciphertext)

    print(f"[✓] Encrypted  '{INPUT_FILE}'  ->  '{ENCRYPTED_FILE}'")


def verify() -> bool:
    """Compare INPUT_FILE with DECRYPTED_FILE; print and return result."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as fh:
        original = fh.read()
    with open(DECRYPTED_FILE, 'r', encoding='utf-8') as fh:
        recovered = fh.read()

    if original == recovered:
        print("[✓] Verification PASSED — decrypted text matches the original.")
        return True
    else:
        mismatches = [(i, a, b)
                      for i, (a, b) in enumerate(zip(original, recovered))
                      if a != b]
        if mismatches:
            i, a, b = mismatches[0]
            print(f"[✗] Verification FAILED — {len(mismatches)} mismatch(es). "
                  f"First at position {i}: expected {repr(a)}, got {repr(b)}.")
        else:
            print(f"[✗] Verification FAILED — lengths differ "
                  f"({len(original)} vs {len(recovered)} chars).")
        return False


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("          Text Encryption Program")
    print("=" * 55)

    # ── get user inputs ──────────────────────────────────────
    while True:
        try:
            shift1 = int(input("Enter shift1 (integer): "))
            break
        except ValueError:
            print("  Please enter a valid integer.")

    while True:
        try:
            shift2 = int(input("Enter shift2 (integer): "))
            break
        except ValueError:
            print("  Please enter a valid integer.")

    print()
    print(f"Using shift1 = {shift1},  shift2 = {shift2}")
    print("-" * 55)

    # ── collision warning ────────────────────────────────────
    cols    = check_collisions(shift1, shift2)
    lc_cols = cols['lower']
    uc_cols = cols['upper']

    if lc_cols or uc_cols:
        print("[!] WARNING: These shift values cause letter collisions.")
        print("    Two different plaintext letters encrypt to the same")
        print("    ciphertext letter, so perfect decryption is impossible")
        print("    for those characters.\n")
        for p1, p2, c in lc_cols:
            print(f"    lowercase: '{p1}' and '{p2}' both map to '{c}'")
        for p1, p2, c in uc_cols:
            print(f"    uppercase: '{p1}' and '{p2}' both map to '{c}'")
        print()
        print("    Tip: choose values where (shift1*shift2) % 26 and")
        print("         (shift1+shift2) % 26 don't overlap (both < 13),")
        print("         shift1 % 26 < 14, and (shift2**2) % 26 < 13.\n")
    else:
        print("[✓] No collisions — perfect decryption is guaranteed.")

    print("-" * 55)

    # ── run pipeline ─────────────────────────────────────────
    encrypt(shift1, shift2)
    decrypt(shift1, shift2)
    verify()
    print("=" * 55)

    # ── preview ──────────────────────────────────────────────
    with open(INPUT_FILE,     'r', encoding='utf-8') as fh: raw = fh.read()
    with open(ENCRYPTED_FILE, 'r', encoding='utf-8') as fh: enc = fh.read()
    with open(DECRYPTED_FILE, 'r', encoding='utf-8') as fh: dec = fh.read()

    raw_line = raw.split('\n')[0]
    enc_line = enc.split('\n')[0]
    dec_line = dec.split('\n')[0]
    n = 70
    print(f"\nPreview (first line, up to {n} chars):")
    print(f"  Original : {raw_line[:n]}")
    print(f"  Encrypted: {enc_line[:n]}")
    print(f"  Decrypted: {dec_line[:n]}")


if __name__ == "__main__":
    main()
