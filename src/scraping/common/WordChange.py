def full_to_half(word):
    return word.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

def half_to_full(word):
    return word.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))