import matplotlib.pyplot as plt
import numpy as np

# Define the five categories
categories = [
    "Navigation & Usability",
    "Visual Design & Aesthetics",
    "Content & Info Architecture",
    "Trust & Credibility",
    "Functionality & Performance"
]

# Numerical scores for each website (out of 100)
frontdoor_scores = [85, 85, 80, 90, 90]
craftcall_scores = [85, 80, 75, 75, 85]
fiverr_scores    = [65, 75, 70, 65, 78]

# Number of variables
N = len(categories)

# Compute angles for each category on the radar chart
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # complete the loop

# Append the first score to the end of each list to close the radar chart loop
frontdoor_scores += frontdoor_scores[:1]
craftcall_scores += craftcall_scores[:1]
fiverr_scores += fiverr_scores[:1]

# Create the radar chart
plt.figure(figsize=(10, 10))
ax = plt.subplot(111, polar=True)

# Draw one axis per variable with the category labels
plt.xticks(angles[:-1], categories, fontsize=10)

# Set y-ticks (score ranges)
ax.set_rlabel_position(30)
plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=8)
plt.ylim(0, 100)

# Plot and fill the area for Frontdoor
ax.plot(angles, frontdoor_scores, linewidth=2, linestyle='solid', label="Frontdoor", color='green')
ax.fill(angles, frontdoor_scores, color='green', alpha=0.25)

# Plot and fill the area for Craft Call
ax.plot(angles, craftcall_scores, linewidth=2, linestyle='solid', label="Craft Call", color='blue')
ax.fill(angles, craftcall_scores, color='blue', alpha=0.25)

# Plot and fill the area for Fiverr
ax.plot(angles, fiverr_scores, linewidth=2, linestyle='solid', label="Fiverr", color='red')
ax.fill(angles, fiverr_scores, color='red', alpha=0.25)

plt.title("Comparison of Competitors' Websites Across Key Functionality Categories", size=15, y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.show()
