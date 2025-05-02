from PyPDF2 import PdfMerger

pdf_pitcher = "Pitch_Usage_By_Game-p1.pdf"  # Output from the Python script
pdf_contact = "Pitch_Usage_By_Game-p2.pdf"  # Output from the R script
pdf_combined = "Pitcher_Count_Splits.pdf"

merger = PdfMerger()
merger.append(pdf_pitcher)
merger.append(pdf_contact)
merger.write(pdf_combined)
merger.close()
print(f"\n Combined report saved as: {pdf_combined}")
