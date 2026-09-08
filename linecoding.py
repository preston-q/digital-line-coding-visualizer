# 1. Polar NRZ-L
def nrz_l(bits):
    signal = []

    for bit in bits:
        if bit == '1':
            signal.append([1])
        else:
            signal.append([-1])

    return signal

# 2. Polar NRZ-I
def nrz_i(bits):
    signal = []
    level = 1

    for bit in bits:
        if bit == '1':
            level = -level

        signal.append([level])

    return signal

# 3. Polar RZ
def rz(bits):
    signal = []

    for bit in bits:
        if bit == '1':
            signal.append([1, 0])
        else:
            signal.append([-1, 0])

    return signal

# 4. Manchester
def manchester(bits):
    signal = []

    for bit in bits:
        if bit == '1':
            signal.append([-1, 1])
        else:
            signal.append([1, -1])

    return signal

# 5. Differential Manchester
def differential_manchester(bits):
    signal = []
    level = 1

    for bit in bits:
        if bit == '0':
            level = -level

        signal.append([level, -level])
        level = -level

    return signal