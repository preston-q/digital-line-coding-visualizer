import numpy as np


# --------------------------------------------------
# Convert bit string to NumPy array
# --------------------------------------------------

def _bits_array(bits):
    return np.fromiter(
        (int(bit) for bit in bits),
        dtype=np.int8
    )


# --------------------------------------------------
# 1. Polar NRZ-L
# --------------------------------------------------

def nrz_l(bits):

    bits = _bits_array(bits)

    return np.where(
        bits == 1,
        1,
        -1
    ).astype(np.int8)


# --------------------------------------------------
# 2. Polar NRZ-I
# --------------------------------------------------

def nrz_i(bits):

    bits = _bits_array(bits)

    signal = np.empty(
        len(bits),
        dtype=np.int8
    )

    level = 1

    for i, bit in enumerate(bits):

        if bit == 1:
            level = -level

        signal[i] = level

    return signal


# --------------------------------------------------
# 3. Polar RZ
# --------------------------------------------------

def rz(bits):

    bits = _bits_array(bits)

    levels = np.where(
        bits == 1,
        1,
        -1
    ).astype(np.int8)

    signal = np.empty(
        (len(bits), 2),
        dtype=np.int8
    )

    signal[:, 0] = levels
    signal[:, 1] = 0

    return signal


# --------------------------------------------------
# 4. Manchester
# --------------------------------------------------

def manchester(bits):

    bits = _bits_array(bits)

    signal = np.empty(
        (len(bits), 2),
        dtype=np.int8
    )

    signal[:, 0] = np.where(
        bits == 1,
        -1,
        1
    )

    signal[:, 1] = np.where(
        bits == 1,
        1,
        -1
    )

    return signal


# --------------------------------------------------
# 5. Differential Manchester
# --------------------------------------------------

def differential_manchester(bits):

    bits = _bits_array(bits)

    signal = np.empty(
        (len(bits), 2),
        dtype=np.int8
    )

    level = 1

    for i, bit in enumerate(bits):

        # 0 → transition at beginning of bit
        if bit == 0:
            level = -level

        signal[i, 0] = level
        signal[i, 1] = -level

        # Always transition in the middle
        level = -level

    return signal