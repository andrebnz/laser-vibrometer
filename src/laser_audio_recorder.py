import serial
import wave
import struct
import time
import os
import numpy as np
from scipy.signal import butter, lfilter

# ------------ CONFIGURATION OF MICROCONTROLLER ----------------
PORT = '/dev/cu.usbmodem11103'    # Port
BAUD = 115200
RECORDING_LENGTH = 10              # recording time in seconds
FS = 8000                        # sample rate
DESKTOP_PATH = os.path.expanduser("~/Desktop")
DATEINAME = os.path.join(DESKTOP_PATH, "laser_recording.wav")

# -------------------- FILTER SETUP -----------------------------
def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

# --------------------- FURTHER PORT SETUP ----------------------
print(f"Connect with {PORT}...")
try:
    ser = serial.Serial(PORT, BAUD, timeout=None)
except Exception as e:
    print(f"Error opening the port: {e}")
    print("Check whether the board is plugged in correctly and the port number is correct.")
    exit()

#-------------------------- RECORDING ----------------------------
print(f"\n--- READY FOR THE RECORDING-SESSION ---")
input("Push ENTER to start the Recording...")

raw_data = []
ser.reset_input_buffer()
start_time = time.time()

print("🔴 Recording... ")

byte_buffer = []

while (time.time() - start_time) < RECORDING_LENGTH:
    raw_byte = ser.read(1)
    if raw_byte:
        byte_buffer.append(raw_byte[0])
        
        while len(byte_buffer) >= 2:
            high = byte_buffer.pop(0)
            low = byte_buffer.pop(0)
            
            val = (high << 8) | low
            if 0 <= val <= 4095:
                raw_data.append(val - 2048)

ser.close()
print(f"⬜ Recording ended. {len(raw_data)} Data Points Received.")

if len(raw_data) > 100:
    print("🪄 Apply a digital bandpass filter (40Hz - 3999Hz)...")
    filtered_data = bandpass_filter(np.array(raw_data), 40, 3999, FS, order=3)
    
    max_val = np.max(np.abs(filtered_data))
    if max_val > 0:
        filtered_data = (filtered_data / max_val) * 30000
    
    audio_signals = filtered_data.astype(np.int16)
    
    print(f"💾 Save File")
    with wave.open(DATEINAME, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 16-Bit
        
        # Calculating the real b-tab rate
        effektive_rate = int(len(audio_signals) / RECORDING_LENGTH)
        wav_file.setframerate(effektive_rate if effektive_rate > 0 else FS)
        
        for sample in audio_signals:
            wav_file.writeframes(struct.pack('<h', sample))
            
    print(f"🎉 FINISHED! The file 'laser_recording.wav' is saved.")
else:
    print("❌ Error: No data received. Click on reset.")