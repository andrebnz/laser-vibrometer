import matplotlib.pyplot as plt
import numpy as np

# ------------------ DATA POINTS -------------------------
frequencies = np.array([200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900])
amplitudes = np.array([300, 390, 440, 520, 590,   0,   0,   0,   0,   0, 1040, 1120, 1190, 1270, 1340])

# Uncertainties
x_error = 10
y_error = 30

# ---------------- LINEAR REGRESSION ----------------------

# Part 1: 200 Hz to 400 Hz
f_reg1 = frequencies[0:5]
a_reg1 = amplitudes[0:5]
p1, cov1 = np.polyfit(f_reg1, a_reg1, 1, cov=True)
m1, b1 = p1[0], p1[1]
dm1, db1 = np.sqrt(np.diag(cov1))

# Part 2: 700 Hz to 900 Hz
f_reg2 = frequencies[10:]
a_reg2 = amplitudes[10:]
p2, cov2 = np.polyfit(f_reg2, a_reg2, 1, cov=True)
m2, b2 = p2[0], p2[1]
dm2, db2 = np.sqrt(np.diag(cov2))

# Output of the equations, including uncertainties, to the terminal
print("--- TRANSFER FUNCTION ---")
print(f"Bereich 200-400 Hz: H1(f) = ({m1:.2f} ± {dm1:.2f}) * f + ({b1:.1f} ± {db1:.1f})")
print(f"Bereich 700-900 Hz: H2(f) = ({m2:.2f} ± {dm2:.2f}) * f + ({b2:.1f} ± {db2:.1f})")

# Part 3: 700 Hz bis 900 Hz (Messpunkte 10 bis 14)
f_reg2 = frequencies[10:]
a_reg2 = amplitudes[10:]
m2, b2 = np.polyfit(f_reg2, a_reg2, 1)

# Plot setup
plt.figure(figsize=(11, 6.5))

# ----------------- PLOTTING THE FITTED LINES ------------------
# Continuous x-values ​​for a clean representation of the straight lines
x_fit1 = np.linspace(200, 400, 100)
x_fit2 = np.linspace(700, 900, 100)

plt.plot(x_fit1, m1 * x_fit1 + b1, '-', color='#004c6d', linewidth=2.5, 
         label=f'Linear Fit 1: $H(f) = {m1:.2f}f + {b1:.0f}$')
plt.plot(x_fit2, m2 * x_fit2 + b2, '-', color='#00a1c1', linewidth=2.5, 
         label=f'Linear Fit 2: $H(f) = {m2:.2f}f + {b2:.0f}$')

# --------------- DASHED TRANSITIONS AND DEAD ZONE ---------------
# Gestrichelte Linien von den Endpunkten der Geraden zu den Nullstellen
plt.plot([400, 450], [m1*400 + b1, 0], '--', color='#004c6d', linewidth=1.5)
plt.plot([450, 650], [0, 0], '-', color='gray', linewidth=2)
plt.plot([650, 700], [0, m2*700 + b2], '--', color='#00a1c1', linewidth=1.5)

# ------------------- DATA POINTS WITH ERROR BARS ------------------
plt.errorbar(frequencies, amplitudes, xerr=x_error, yerr=y_error, fmt='o', 
             ecolor='#de425b', elinewidth=1.5, capsize=3, mfc='#de425b', mec='#de425b', 
             ms=6, zorder=5, label='Data Points with Uncertainties')

# Highlight the structural dead zone
plt.axvspan(450, 650, color='gray', alpha=0.12, label='Mechanical Nodal Line (Antiresonance)')

# Scientific labeling
plt.xlabel("Excitation Frequency $f$ (Hz)", fontsize=12)
plt.ylabel("Measured Peak Amplitude (ADC Digits)", fontsize=12)

# Axis limits and ticks
plt.xlim(150, 950)
plt.ylim(-50, max(amplitudes) * 1.1)
plt.xticks(np.arange(200, 901, 50))

plt.grid(True, which='major', linestyle='--', alpha=0.5)
plt.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='none')

plt.tight_layout()
plt.show()