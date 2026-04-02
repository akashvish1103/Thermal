import matplotlib.pyplot as plt
import numpy as np
import time

# Turn ON interactive mode
plt.ion()

x_data = []
y_data = []

fig, ax = plt.subplots()
line, = ax.plot(x_data, y_data)

i = 0

while True:
    # Simulate incoming value (replace with your mean_temp)
    value = np.sin(i * 0.1)

    x_data.append(i)
    y_data.append(value)

    # Update line data
    line.set_xdata(x_data)
    line.set_ydata(y_data)

    # Rescale axes
    ax.relim()
    ax.autoscale_view()

    # Draw updated plot
    plt.draw()
    plt.pause(0.01)

    i += 1
    time.sleep(0.05)