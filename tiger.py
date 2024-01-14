import struct

from sboxes import t1, t2, t3, t4

MASK_64_BITS = 0xFFFFFFFFFFFFFFFF


class TigerHash:
    def __init__(self):
        self.x = None
        self.a = 0x0123456789ABCDEF
        self.b = 0xFEDCBA9876543210
        self.c = 0xF096A5B4C3B2E187

    @staticmethod
    def _tiger_round(a, b, c, x, mul):
        c ^= x & MASK_64_BITS
        [c_0, c_1, c_2, c_3, c_4, c_5, c_6, c_7] = [(c >> (8 * i)) & 0xFF for i in range(8)]
        a -= t1[c_0] ^ t2[c_2] ^ t3[c_4] ^ t4[c_6]
        b += t4[c_1] ^ t3[c_3] ^ t2[c_5] ^ t1[c_7]
        b *= mul
        a &= MASK_64_BITS
        b &= MASK_64_BITS
        c &= MASK_64_BITS
        return {"a": a, "b": b, "c": c}

    def tiger_pass(self, a, b, c, mul):
        [self.a, self.b, self.c] = self._tiger_round(a, b, c, self.x[0], mul).values()
        [self.a, self.b, self.c] = self._tiger_round(self.b, self.c, self.a, self.x[1], mul).values()

        values = self._tiger_round(self.b, self.c, self.a, self.x[2], mul)

        values = {"c": values["a"], "a": values["b"], "b": values["c"]}

        values = self._tiger_round(values["a"], values["b"], values["c"], self.x[3], mul)

        values = self._tiger_round(values["b"], values["c"], values["a"], self.x[4], mul)
        values = {"b": values["a"], "c": values["b"], "a": values["c"]}

        values = self._tiger_round(values["c"], values["a"], values["b"], self.x[5], mul)

        values = {"c": values["a"], "a": values["b"], "b": values["c"]}

        values = self._tiger_round(values["a"], values["b"], values["c"], self.x[6], mul)

        values = self._tiger_round(values["b"], values["c"], values["a"], self.x[7], mul)
        values = {"b": values["a"], "c": values["b"], "a": values["c"]}

        return [values['a'], values['b'], values['c']]

    def tiger_prepare_message(self, message):
        self.x = []

        for j in range(0, 8):
            self.x.append(struct.unpack('Q', message[j * 8:j * 8 + 8])[0])

    def tiger_key_schedule(self):
        self.x[0] = (self.x[0] - (self.x[7] ^ 0xA5A5A5A5A5A5A5A5) & MASK_64_BITS) & MASK_64_BITS
        self.x[1] ^= self.x[0]
        self.x[2] = (self.x[2] + self.x[1]) & MASK_64_BITS
        self.x[3] = (self.x[3] - (self.x[2] ^ (~self.x[1] & MASK_64_BITS) << 19) & MASK_64_BITS) & MASK_64_BITS
        self.x[4] ^= self.x[3]
        self.x[5] = (self.x[5] + self.x[4]) & MASK_64_BITS
        self.x[6] = (self.x[6] - (self.x[5] ^ (~self.x[4] & MASK_64_BITS) >> 23) & MASK_64_BITS) & MASK_64_BITS
        self.x[7] ^= self.x[6]
        self.x[0] = (self.x[0] + self.x[7]) & MASK_64_BITS
        self.x[1] = (self.x[1] - (self.x[0] ^ (~self.x[7] & MASK_64_BITS) << 19) & MASK_64_BITS) & MASK_64_BITS
        self.x[2] ^= self.x[1]
        self.x[3] = (self.x[3] + self.x[2]) & MASK_64_BITS
        self.x[4] = (self.x[4] - (self.x[3] ^ (~self.x[2] & MASK_64_BITS) >> 23) & MASK_64_BITS) & MASK_64_BITS
        self.x[5] ^= self.x[4]
        self.x[6] = (self.x[6] + self.x[5]) & MASK_64_BITS
        self.x[7] = (self.x[7] - (self.x[6] ^ 0x0123456789ABCDEF) & MASK_64_BITS) & MASK_64_BITS

    def tiger_compress(self, message, result):
        # setup
        a = result[0]
        b = result[1]
        c = result[2]

        self.tiger_prepare_message(message)

        # compress
        aa = a
        bb = b
        cc = c

        for i in range(3):
            if i != 0:
                self.tiger_key_schedule()

            shifts = [5, 7, 9]
            a, b, c = self.tiger_pass(a, b, c, shifts[i])
            a, b, c = c, a, b

        a ^= aa
        b = (b - bb) & MASK_64_BITS
        c = (c + cc) & MASK_64_BITS

        # map values out
        result[0] = a
        result[1] = b
        result[2] = c

    @staticmethod
    def little_endian_to_big_endian(input_str):
        if len(input_str) % 16 != 0:
            raise ValueError("Input length must be a multiple of 16 for 8-byte little endian to big endian conversion")

        chunks = [input_str[i:i + 16] for i in range(0, len(input_str), 16)]

        output_str = ''
        for chunk in chunks:
            # Convert pairs of characters in each 8-byte chunk from little endian to big endian
            converted_chunk = ''.join(reversed([chunk[i:i + 2] for i in range(0, len(chunk), 2)]))
            output_str += converted_chunk

        return output_str

    def hash(self, message):
        message = message.encode('utf-8')

        results = [0x0123456789ABCDEF, 0xFEDCBA9876543210, 0xF096A5B4C3B2E187]
        message_length = len(message)
        i = 0
        while i < message_length - 63:
            self.tiger_compress(message[i:i + 64], results)
            i += 64
        temp = bytes(message[i:])
        j = len(temp)
        temp += bytes([0x01])
        j += 1

        while j & 7 != 0:
            temp += bytes([0x00])
            j += 1

        if j > 56:
            while j < 64:
                temp += bytes([0x00])
                j += 1
            self.tiger_compress(temp, results)
            j = 0

        temp += bytes([0] * (56 - j))
        temp = temp[:56]
        temp += struct.pack('Q', message_length << 3)
        self.tiger_compress(temp, results)

        return self.little_endian_to_big_endian("%016x%016x%016x" % (results[0], results[1], results[2]))
