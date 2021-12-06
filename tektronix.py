#!/usr/bin/env python
# 2021 - LambdaConcept - po@lambdaconcept.com

import time
import socket
import numpy as np

class Tektronix:
    """ The oscilloscope must be available on the network
    and remote protocol configured as terminal.
    Utility -> Config -> I/O -> Socket Server -> Protocol -> Terminal
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.recv_ascii()

    def close(self):
        self.sock.close()

    def send_ascii(self, text):
        print(text)
        msg = text + "\n"
        self.sock.send(bytes(msg, encoding="ASCII"))

    def recv_ascii(self):
        resp = ""
        while True:

            data = self.sock.recv(1024)
            line = data.decode("ASCII").strip()

            if line and line[-1] == ">":
                # end condition
                resp += line[:-1]
                break
            else:
                resp += line

        print(resp)
        return resp

    def recv_binary(self):
        data = self.sock.recv(1024)

        # decode the header (IEEE488.2 binary block header)
        assert(chr(data[0]) == "#")
        hdrlen = int(chr(data[1]))
        bytecount = int(data[2:2+hdrlen].decode("ASCII"))
        print("bytecount:", bytecount)

        # get the first data bytes
        values = data[2+hdrlen:]
        bytecount -= len(values)
        print("got:", len(values), "remains:", bytecount)

        # receive the remaining data bytes
        while bytecount > 0:
            data = self.sock.recv(1024)
            values += data
            bytecount -= len(data)
            print("got:", len(data), "remains:", bytecount)

        self.recv_ascii()
        return values

    def write(self, text):
        self.send_ascii(text)
        self.recv_ascii()

    def query_string(self, text):
        self.send_ascii(text)
        return self.recv_ascii().strip('"')

    def query_float(self, text):
        self.send_ascii(text)
        resp = self.recv_ascii()
        values = list(map(float, resp.split(",")))
        return np.array(values)

    def query_uint16(self, text):
        self.send_ascii(text)
        buf = self.recv_binary()
        return np.frombuffer(buf, dtype=">H") # big-endian unsigned short

def main():
    out = open("out.csv", "a")

    tek = Tektronix("192.168.10.109", 4000)
    tek.open()

    tek.write("*IDN?")

    tek.write("DATA:SOURCE CH1")
    tek.write("DATA:START 1")
    tek.write("DATA:STOP 10000")
    # tek.write("DATA:ENCDG ASCII")
    tek.write("DATA:ENCDG RPBINARY")
    tek.write("DATA:WIDTH 2")

    tek.write("HEADER 1")
    tek.write("WFMO?")

    tek.write("HEADER 0")
    ymult = tek.query_float("WFMPRE:YMULT?")
    yoff = tek.query_float("WFMPRE:YOFF?")
    yzero = tek.query_float("WFMPRE:YZERO?")
    yunit = tek.query_string("WFMPRE:YUNIT?")

    try:
        while True:
            ts = time.time()
            curve = tek.query_uint16("CURVE?")
            # print("Curve:", curve)
            value = (curve - yoff) * ymult  + yzero
            # print("Value:", value, yunit)
            average = np.average(value)
            print("Average:", average)

            out.write("{}, {}\n".format(ts, average))
            out.flush()
            time.sleep(10)

    except KeyboardInterrupt:
        pass

    out.close()

if __name__ == "__main__":
    main()
