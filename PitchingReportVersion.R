#!/usr/bin/env Rscript

# Load libraries
library(ggplot2)
library(dplyr)
library(readr)
library(gridExtra)
library(grid)

# Load data
data <- read_csv("Stevens/Gonz-AC.csv")

# Map PitchType abbreviations to full names for color matching
data$MappedPitchType <- recode(data$PitchType,
                               "FF" = "Fastball",
                               "SL" = "Slider",
                               "CR" = "Curveball",
                               "CH" = "ChangeUp",
                               "SP" = "Splitter",
                               "CT" = "Cutter",
                               "ST" = "Sinker",  # Used for ST, TwoSeamFastBall, OneSeamFastBall
                               "TwoSeamFastBall" = "Sinker",
                               "OneSeamFastBall" = "Sinker",
                               "Undefined" = "Fastball",
                               "FourSeamFastBall" = "Fastball"
)

# Full pitch color palette
pitch_colors <- c(
  "Fastball" = "red",
  "Slider" = "yellow",
  "Curveball" = "blue",
  "Changeup" = "green",
  "Cutter" = "mediumorchid",
  "Sinker" = "orange",
  "Splitter" = "cyan",
  "Knuckleball" = "purple",
  "Sweeper" = "brown",
  "Slurve" = "lime",
  "Forkball" = "darkblue",
  "Screwball" = "magenta",
  "Other" = "gray"
)

# Optional: warn if any pitch types don't match the palette
unmatched <- setdiff(unique(data$MappedPitchType), names(pitch_colors))
if (length(unmatched) > 0) {
  warning("These pitch types have no color mapping: ", paste(unmatched, collapse = ", "))
}

# Function to create a styled, Python-matching plot
standard_plot <- function(df, title) {
  df$MappedPitchType <- as.character(df$MappedPitchType)
  used_types <- unique(df$MappedPitchType)
  valid_colors <- pitch_colors[names(pitch_colors) %in% used_types]
  
  ggplot(df, aes(x = PlateLocSide, y = PlateLocHeight, fill = MappedPitchType)) +
    geom_point(shape = 21, color = "black", size = 2.5, alpha = 0.9) +
    
    # Strike zone box
    annotate("rect", xmin = -0.83, xmax = 0.83, ymin = 1.5, ymax = 3.5,
             color = "black", fill = NA, linetype = "solid", size = 0.8) +
    
    # Home plate polygon
    annotate("polygon",
             x = c(-0.71, -0.83, 0.83, 0.71, 0.0),
             y = c(0.78, 0.6, 0.6, 0.78, 0.9),
             fill = "white", color = "black", linewidth = 1.5) +
    
    labs(title = title) +
    scale_fill_manual(values = valid_colors, na.value = "gray") +
    coord_fixed(xlim = c(-2, 2), ylim = c(0.5, 4.5)) +
    theme_minimal(base_family = "Helvetica", base_size = 12) +
    theme(
      panel.background = element_rect(fill = "gray95", color = "black", size = 1),
      panel.border = element_rect(fill = NA, color = "black", size = 1),
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      axis.title = element_blank(),
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      legend.position = "none"
    )
}

# Create each of the 6 plots
plot1 <- standard_plot(data %>% filter(PitchCall == "StrikeSwinging", BatterSide == "Left"),
                       "SAMs vs LHH")

plot2 <- standard_plot(data %>% filter(PitchCall == "StrikeSwinging", BatterSide == "Right"),
                       "SAMs vs RHH")

plot3 <- standard_plot(data %>% filter(!is.na(ExitSpeed), ExitSpeed > 90, BatterSide == "Left"),
                       "Hard Hits > 90MPH vs LHH")

plot4 <- standard_plot(data %>% filter(!is.na(ExitSpeed), ExitSpeed > 90, BatterSide == "Right"),
                       "Hard Hits > 90MPH vs RHH")

plot5 <- standard_plot(data %>% filter(PitchCall == "StrikeCalled"),
                       "Called Strikes")

plot6 <- standard_plot(data %>% filter(!is.na(ExitSpeed), ExitSpeed < 80),
                       "Weak Contact < 80MPH")

# Optional title banner
title_banner <- textGrob(
  "Trackman Pitching Report – Plate Appearance Visuals",
  gp = gpar(fontsize = 18, fontface = "bold", fontfamily = "Helvetica"),
  just = "center"
)

# Output single-page PDF
pdf("Stevens/Gonz - R2.pdf", width = 9, height = 11)
grid.arrange(
  title_banner,
  arrangeGrob(plot1, plot2, plot3, plot4, plot5, plot6, ncol = 2),
  nrow = 2,
  heights = c(0.1, 0.9)
)
dev.off()

cat("✅ Styled PDF saved as 'trackman_whiff_ev_report.pdf'\n")
