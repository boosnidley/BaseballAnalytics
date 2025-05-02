import subprocess
import os
from PyPDF2 import PdfMerger

# Define file names
python_script = "Pitching Scripts/Pitching Reports/PitcherReport.py"
r_script = "Pitching Scripts/Pitching Reports/PitchingReportVersion.R"

pdf_pitcher = "PR1.pdf"  # Output from the Python script
pdf_contact = "PR2.pdf"  # Output from the R script
pdf_combined = "Combined_Trackman_Report.pdf"

# Step 1: Run the Python pitcher report script
print("Running Python pitcher report...")
subprocess.run(["python", python_script], check=True)
print("Pitcher report generated.")

# Step 2: Run the R script to generate the contact plots
print("Running R contact report...")
subprocess.run(["Rscript", r_script], check=True)
print("Contact report generated.")

# Step 3: Merge both PDFs
print("Merging PDFs into a 2-page report...")
merger = PdfMerger()
merger.append(pdf_pitcher)
merger.append(pdf_contact)
merger.write(pdf_combined)
merger.close()

print(f"\n Combined report saved as: {pdf_combined}")
