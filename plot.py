#!/usr/bin/env python
# 2021 - LambdaConcept - po@lambdaconcept.com

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tail

TIMEOUT = 1000

file = tail.Tail("out.csv")

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

def append(line):
    ts, value = line.strip().split(",")
    ts = time.strftime('%a %H:%M:%S', time.localtime(float(ts)))
    value = round(float(value), 2)

    xs.append(ts)
    ys.append(value)
    print(ts, value)

def populate():
    for line in file.readall():
        append(line)

def draw():
    ax.clear()
    ax.set(ylim=(0, 4.5)) # vertical range (li-ion bat voltage)
    ax.plot(xs, ys)

    # limit to 20 horizontal ticks
    xmax = len(xs)
    if xmax >= 20:
        xstep = xmax // 20
    else:
        xstep = 1

    # plot
    plt.xticks(np.arange(0, xmax, step=xstep), rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Voltage over Time')
    plt.ylabel('Voltage (V)')

def animate(i, xs, ys):
    line = file.fetch()
    if line:
        append(line)
    draw()

# Set up plot to call animate() function periodically
populate()
draw()
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=TIMEOUT)
plt.show()
