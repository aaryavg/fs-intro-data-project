# Step 1
import polars as pl

path = "data/software-data.parquet"

# Reading and loading the binary parquet file which consists of raw binary data into a Polars DataFrame
df = pl.read_parquet(path)

#Load and forward fill the the empty cells, then backfill leading nulls, which also carries previous sensor readings forward across time gaps and cleans leading nulls
df = df.fill_null(strategy="forward").fill_null(strategy="backward")

#Print column names and the first 20 rows
print("Column in file:")
print(df.columns)
print("\nFirst 20 rows:")
print(df.head(20))

# Step 2: Calculate Ground Speed & Graphs vs. Time
import numpy as np
import matplotlib.pyplot as plt

# Physicss Constants
WR = 0.2 # Wheel Radius
GR = 12/41 #Sprocket Gear Ratio

#Using Polars to add a new Speed_ms column & Computing the Speed
df = df.with_columns(
    (pl.col("SME_TRQSPD_Speed") * GR * (2 * np.pi / 60) * WR).alias("Speed_ms")

# Physics Breakdown:
# Wheel RPM (wRPM) = mRPM x 12/41
# Angular Velocity (w) = wRPM x 2π/60
# Linear Ground Speed (v) = w x WR
# V substitution: v = mRPM x 12/41 x 2π/60 x WR
)

# Plot Speed vs time using matplotlib
plt.figure(figsize=(10, 5))
plt.plot(df["Time"], df["Speed_ms"], label = "Speed (m/s)", color = "blue")
plt.title("Vehicle Ground Speed vs Time")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")
plt.legend()
plt.grid()
plt.show()

# Determine the speed when times = 10 seconds
speed10s = df.filter(pl.col("Time") >= 10.0)
print("Speed at 10 seconds: ", speed10s.select(["Time", "Speed_ms"]))


# Step 3: Give a time frame for when the car is accelerating, braking, and coasting. 
# Explain how you found these values out. Then plot those states over time on three different graphs

# dv/dt >0 with high positive slope = Acceleration with around 10.5 m/s
df_accel = df.filter((pl.col("Time") >= 20.0) & (pl.col("Time") <= 24.5))

#dv/dt = 0 with low positive slope = Coasting with around 4.5 m/s
df_coast = df.filter((pl.col("Time") >= 24.5) & (pl.col("Time") <= 40.0))

#dv/dt < 0 with high negative slope = Braking goung down to 0 m/s
df_brake = df.filter((pl.col("Time") >= 72.5) & (pl.col("Time") <= 77.5))

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (10, 10))

ax1.plot(df_accel["Time"], df_accel["Speed_ms"], color = "green", linewidth = 2)
ax1.set_title("Acceleration Phase")
ax1.set_ylabel("Speed (m/s)")
ax1.set_xlabel("Time (s)")

ax2.plot(df_coast["Time"], df_coast["Speed_ms"], color = "orange", linewidth = 2)
ax2.set_title("Coasting Phase")
ax2.set_ylabel("Speed (m/s)")
ax2.set_xlabel("Time (s)")

ax3.plot(df_brake["Time"], df_brake["Speed_ms"], color = "red", linewidth = 2)
ax3.set_title("Braking Phase")
ax3.set_ylabel("Speed (m/s)")
ax3.set_xlabel("Time (s)")

plt.tight_layout()
plt.show()

# Step 4: Find out how many laps the car drove as well as the start and end time for each lap. 
# The car has a GPS system you can utilize to visualize this. 
# Provide a screenshot of your method along with an explanation of how you went about finding this.

# Implemted a GPS Track Map using the latitude and longitude data from the dataset.
plt.figure(figsize=(10, 10))
scatter = plt.scatter(df["VDM_GPS_Longitude"], df["VDM_GPS_Latitude"], c=df["Time"], cmap='viridis', s=10)
plt.colorbar(scatter, label = "Time (s)")

#Start Position Marker: Single Red Dot - needed to delete it
#launchpoint = df.filter(pl.col("Speed_Ms") > 1.0)
#plt.plot(launchpoint["VDM_GPS_Longitude"][0], launchpoint["VDM_GPS_Latitude"][0], "ro", markersize = 8, label = "Start Point")

plt.title("Vehicle 2D GPS Trajectory & Time: Color Coded")
plt.ylabel("GPS Latitude")
plt.xlabel("GPS Longitude")
plt.grid(True) # Easier to trace values by eye with gridlines across the plot
# plt.legend() #Displays small label box
plt.tight_layout() #Adjusts the subplot 
plt.show() #Opens the user window and displays the figure on your screen

# First row where the vehcile is driving
first = df.filter(pl.col("Speed_ms") > 0.5)

# Marking where it actually starts
plt.plot(first["VDM_GPS_Longitude"][0], first["VDM_GPS_Latitude"][0], "ro", markersize = 8, label = "Dynamic Start Point")

#Explanation on why I did this:
# I used the GPS Latitude & Longitude Data to plot the car's plath on to a 2D scatter plot. 
# I then led on to color code the points based on the time data..
# This allowed me to visualize the car's path and identify when the start and end of each lap occured. 
# Addtionally i plotted the vehicle posiiton using VDM_GPS_Longitude and VDM_GPS_Latitude to maps the car's path onto a cartesian space which is (x,y) coordinates.
# Each of the run's trajectory was color coded based on the time data, its easier to map the telemetary and trace it, in order to know when the vehicle leaves and even returns at a specific coordinate.

# Step 5: Using the lap times found from part 4
# Determine the max speed, max acceleration, time spent accelerating, and time spent coasting.

pass1 = df.filter((pl.col("Time") >= 20.5) & (pl.col("Time") <= 45))

# Max Speed
maxspeed_ms = pass1["Speed_ms"].max()
maxspeed_mph = maxspeed_ms * 2.23694  # Convert m/s to mph

# Max Acceleration
accel_window = df.filter((pl.col("Time") >= 20.0) & (pl.col("Time") <= 24.5))
Vstart = accel_window["Speed_ms"][0]
Vend = accel_window["Speed_ms"][-1]
tstart = accel_window["Time"][0]
tend = accel_window["Time"][-1]

maxaccel = (Vend - Vstart) / (tend - tstart)

# Time Spent Accelerating
timespent_accelerating = tend - tstart

# Time spent Coasting
coast_window = df.filter((pl.col("Time") >= 24.5) & (pl.col("Time") <= 40.0))
timespent_coasting = coast_window["Time"][-1] - coast_window["Time"][0]

print(f"Max Speed: {maxspeed_ms:.2f} m/s ({maxspeed_mph:.2f} mph)")
print(f"Max Acceleration: {maxaccel:.2f} m/s^2")
print(f"Time Spent Accelerating: {timespent_accelerating:.2f} seconds")
print("Time Spent Coasting: {timespent_coasting:.2f} seconds")



