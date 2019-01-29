

def calculatePid(frameId):

    bit0 = (frameId & 0x01)
    bit1 = (frameId & 0x02) >> 1
    bit2 = (frameId & 0x04) >> 2
    bit3 = (frameId & 0x08) >> 3
    bit4 = (frameId & 0x10) >> 4
    bit5 = (frameId & 0x20) >> 5


    parity0 = ((bit0 ^ bit1) ^ bit2) ^ bit4
    parity1 = int(bool(not(((bit1 ^ bit3) ^ bit4) ^ bit5)))

    print(parity1, parity0, bit5, bit4, bit3, bit2, bit1, bit0)

    output = (parity1 << 7) | \
             (parity0 << 6) | \
             (bit5 << 5) | \
             (bit4 << 4) | \
             (bit3 << 3) | \
             (bit2 << 2) | \
             (bit1 << 1) | \
             bit0

    return output

if __name__ == "__main__":

    print(calculatePid(0x3d))