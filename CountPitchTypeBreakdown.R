
# Load required libraries
library(tidyverse)
library(gridExtra)

# List of CSV files and corresponding custom titles
csv_files <- c("Stevens/Fisse-AC.csv", "Stevens/Buur-AC.csv", "Stevens/Vill-AC.csv")
custom_titles <- c("Fisse", "Buurman", "Villapiano")

# Custom pitch type colors
pitch_colors <- c(
  "FF" = "goldenrod",
  "Breaking" = "purple",
  "CH" = "dodgerblue2",
  "SP" = "mediumaquamarine",
  "CT" = "gray34",
  "ST" = "black"
)

# Store plots
plot_list <- list()

# Loop through files and create plots with custom titles
for (i in seq_along(csv_files)) {
  data <- read_csv(csv_files[i])

  data <- data %>%
    mutate(PitchType = case_when(
      PitchType %in% c("SL", "CR") ~ "Breaking",
      TRUE ~ PitchType
    )) %>%
    mutate(count = paste0(Balls, "-", Strikes))

  pitch_usage <- data %>%
    group_by(count, PitchType) %>%
    summarise(N = n(), .groups = "drop") %>%
    group_by(count) %>%
    mutate(total = sum(N),
           usage = N / total)

  p <- ggplot(pitch_usage, aes(x = count, y = usage, fill = PitchType)) +
    geom_bar(stat = "identity") +
    geom_text(aes(label = scales::percent(round(usage, 2))), 
              position = position_stack(vjust = 0.5), color = "white", size = 3) +
    scale_fill_manual(values = pitch_colors) +
    theme_minimal() +
    coord_flip() +
    labs(title = custom_titles[i],
         x = "Count", y = "Usage", fill = "Pitch Type")

  plot_list[[i]] <- p
}

# Output PDF
pdf("Pitch_Usage_By_Game-p2.pdf", width = 10, height = 12)
grid.arrange(grobs = plot_list, ncol = 2)
dev.off()
