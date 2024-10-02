import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time

def fuzzy_moisture(soil_moisture):
    if soil_moisture <= 30:
        return {'dry': 1, 'moderate': 0, 'wet': 0}
    elif 30 < soil_moisture <= 70:
        return {'dry': (70 - soil_moisture) / 40, 'moderate': 1, 'wet': (soil_moisture - 30) / 40}
    else:
        return {'dry': 0, 'moderate': (100 - soil_moisture) / 30, 'wet': 1}

def fuzzy_temperature(temperature):
    if temperature <= 15:
        return {'low': 1, 'moderate': 0, 'high': 0}
    elif 15 < temperature <= 30:
        return {'low': (30 - temperature) / 15, 'moderate': 1, 'high': (temperature - 15) / 15}
    else:
        return {'low': 0, 'moderate': (40 - temperature) / 10, 'high': 1}

def defuzzify(output_fuzzy_values):
    return (output_fuzzy_values['short'] * 7.5 + 
            output_fuzzy_values['medium'] * 15 + 
            output_fuzzy_values['long'] * 22.5) / 30

def fuzzy_watering_system(soil_moisture_input, temperature_input):
    moisture = fuzzy_moisture(soil_moisture_input)
    temp = fuzzy_temperature(temperature_input)
    
    watering_time = {'short': 0, 'medium': 0, 'long': 0}
    
    if moisture['wet'] == 1:
        return 0 
    
    watering_time['long'] = min(moisture['dry'], temp['high'])
    watering_time['medium'] = min(moisture['moderate'], temp['moderate'])
    watering_time['short'] = moisture['wet']
    
    return defuzzify(watering_time)

def calculate_watering_time():
    try:
        soil_moisture_input = float(soil_moisture_entry.get())
        temperature_input = float(temperature_entry.get())

        if soil_moisture_input < 0 or soil_moisture_input > 100:
            raise ValueError("Soil moisture must be between 0 and 100.")
        if temperature_input < 0 or temperature_input > 40:
            raise ValueError("Temperature must be between 0 and 40.")
        
        watering_time = fuzzy_watering_system(soil_moisture_input, temperature_input)
        flow_rate = 2.0
        water_volume = watering_time * flow_rate

        if watering_time == 0:
            messagebox.showinfo("No Watering Needed", "The soil is already wet. No watering is necessary.")
            return

        progress_bar['value'] = 0
        root.update_idletasks()
        
        for i in range(101):
            time.sleep(watering_time / 100)
            progress_bar['value'] = i
            root.update_idletasks()

        messagebox.showinfo(
            "Watering Time and Volume", 
            f"Recommended watering time: {watering_time:.2f} minutes\n"
            f"Water volume: {water_volume:.2f} liters"
        )

        visualize_sprinkling_with_motion(watering_time, water_volume)
        
    except ValueError as ve:
        messagebox.showerror("Invalid Input", str(ve))

def visualize_sprinkling_with_motion(watering_time, water_volume):
    fig = plt.figure(figsize=(10, 7), dpi=120)
    ax = fig.add_subplot(111, projection='3d')

    x_soil = np.linspace(-5, 5, 50)
    y_soil = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x_soil, y_soil)
    Z = np.random.normal(0, 0.1, X.shape)

    ax.plot_surface(X, Y, Z, color='saddlebrown', rstride=1, cstride=1, alpha=0.7)

    num_streams = 20
    stream_angles = np.linspace(0, 2 * np.pi, num_streams, endpoint=False)

    water_droplets = []

    for angle in stream_angles:
        t = np.linspace(0, 1, 100) 
        x_stream = t * 5 * np.cos(angle)
        y_stream = t * 5 * np.sin(angle)
        z_stream = 5 * t * (1 - t) 
        water_droplets.append([x_stream, y_stream, z_stream])

    scatters = []
    for _ in range(num_streams):
        scatters.append(ax.scatter([], [], [], color='blue', s=20))

    fps = 20
    total_frames = int(watering_time * 60 * fps)

    def update(frame):
        if frame >= total_frames:
            return

        for i, scatter in enumerate(scatters):
            x_stream, y_stream, z_stream = water_droplets[i]
            scatter._offsets3d = (x_stream[:frame % 100], y_stream[:frame % 100], z_stream[:frame % 100])
        return scatters

    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_zlim([0, 5])

    ax.set_xlabel('X Axis (Width)')
    ax.set_ylabel('Y Axis (Length)')
    ax.set_zlabel('Z Axis (Height)')
    plt.title(f'Water Sprinkler with Motion - {watering_time:.2f} mins', fontsize=14)

    ani = FuncAnimation(fig, update, frames=total_frames, interval=4000/fps, blit=False)

    plt.show()

root = tk.Tk()
root.title("Water Sprinkler System")
root.config(bg='lightblue')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

frame = tk.Frame(root, bg='#3A6D8C')
frame.grid(row=1, column=0, columnspan=2, pady=20, padx=20)

tk.Label(frame, text="Soil Moisture (0-100):", font=("Arial", 16, "bold"), bg='lightblue').grid(row=0, column=0, padx=10, pady=10)
soil_moisture_entry = tk.Entry(frame, width=25, font=("Arial", 10)) 
soil_moisture_entry.grid(row=0, column=1, padx=5, pady=10, ipady=5)  

tk.Label(frame, text="Temperature (0-40):", font=("Arial", 16, "bold"), bg='lightblue').grid(row=1, column=0, padx=10, pady=10)
temperature_entry = tk.Entry(frame, width=25, font=("Arial", 10))
temperature_entry.grid(row=1, column=1, padx=5, pady=10, ipady=5) 

progress_bar = ttk.Progressbar(frame, orient='horizontal', mode='determinate', length=300)
progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

submit_button = tk.Button(frame, text="Calculate Watering Time", command=calculate_watering_time, font=("Arial", 12, "bold"), bg='#2B547E', fg='white')
submit_button.grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()
