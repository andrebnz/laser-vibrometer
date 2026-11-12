import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import butter, lfilter
import os
import time

# --- CONFIGURATION OF MICROCONTROLLER  ---
PORT = '/dev/cu.usbmodem11103'  
BAUD = 115200
FFT_SIZE = 1024  
FS = 8000                     

# --------- DIGITAL FILTER SETUP ------------
def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


#---------------- SYSTEM TEST ------------------
try:
    ser = serial.Serial(PORT, BAUD, timeout=None)
    print(f"Successfully connected! Focus measurement range: 300Hz - 1600Hz")
except Exception as e:
    print(f"Error: {e}")
    exit()

data_buffer = [0] * FFT_SIZE
byte_buffer = []

#--------------------- PLOT -----------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7))

# 1. Upper Plot: Time Domain
line_time, = ax1.plot(data_buffer, color='g')
ax1.set_ylim(-1500, 1500)
ax1.set_title("Filtered live signal (time domain / oscillation)")
ax1.set_ylabel("Voltage change")
ax1.grid(True, linestyle=':', alpha=0.6)

# 2. Lower Plot: Frequency Domain
frequencies = np.fft.rfftfreq(FFT_SIZE, d=1/FS)
fft_data = np.zeros(len(frequencies))
line_freq, = ax2.plot(frequencies, fft_data, color='b')
ax2.set_ylim(0, 4000)
ax2.set_xlim(300, 1600) 
ax2.set_xticks(np.arange(300, 1601, 100))
ax2.set_xticks(np.arange(300, 1601, 20), minor=True)
ax2.grid(True, which='major', linestyle='-', color='gray', alpha=0.6)
ax2.grid(True, which='minor', linestyle=':', color='lightgray', alpha=0.6)
ax2.set_title("Fourier Transformation")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Amplitude")

plt.tight_layout()

#-------------------------------------------------------
def update(frame):
    global data_buffer, byte_buffer
    
    if ser.in_waiting > 0:
        raw_bytes = ser.read(ser.in_waiting)
        byte_buffer.extend(raw_bytes)
        
        while len(byte_buffer) >= 2:
            if byte_buffer[0] > 15:
                byte_buffer.pop(0)
                continue

            high = byte_buffer.pop(0)
            low = byte_buffer.pop(0)
            
            val = (high << 8) | low
            if 0 <= val <= 4095:
                data_buffer.append(val - 2048)
                data_buffer.pop(0)
                
    signal_array = np.array(data_buffer)
    try:
        filtered_signal = bandpass_filter(signal_array, 40, 3999, FS, order=3)
    except:
        filtered_signal = signal_array
        
    line_time.set_ydata(filtered_signal)
    
    fft_vals = np.abs(np.fft.rfft(filtered_signal * np.hanning(FFT_SIZE)))
    line_freq.set_ydata(fft_vals)
    
    return line_time, line_freq

#------------------- ANIMATION ---------------------------

ani = FuncAnimation(fig, update, interval=20, blit=True)
plt.show()

ser.close()