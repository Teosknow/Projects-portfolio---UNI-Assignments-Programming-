# =============================================================================
# reshape_behaviorspace.R
# Reshapes all 6 NetLogo BehaviorSpace spreadsheets into a single tidy table.
# Each row = one run. Each column = one reporter variable.
#
# Input:  exp1.xlsx ... exp6.xlsx  (BehaviorSpace spreadsheet format v2.0)
# Output: all_experiments_tidy.csv
#         all_experiments_summary.csv
# =============================================================================

library(readxl)
library(dplyr)
library(tidyr)

# --- 0. CONFIG ---------------------------------------------------------------

input_files <- c(
  "exp1.xlsx",
  "exp2.xlsx",
  "exp3.xlsx",
  "exp4.xlsx",
  "exp5.xlsx",
  "exp6.xlsx",
  "exp7.xlsx",
  "exp8.xlsx"
)

experiment_labels <- c(
  "Exp1_Adaptive_Busiest_Short",
  "Exp2_Stubborn_Busiest_Short",
  "Exp3_Adaptive_Random_Short",
  "Exp4_Stubborn_Random_Short",
  "Exp5_Adaptive_Busiest_Long",
  "Exp6_Stubborn_Busiest_Long",
  "Exp7_Adaptive_Random_Long",
  "Exp8_Stubborn_Random_Long"
)

output_tidy    <- "all_experiments_tidy.csv"
output_summary <- "all_experiments_summary.csv"

# --- 1. FUNCTION: reshape one file -------------------------------------------

reshape_one <- function(filepath, experiment_label) {
  
  # Detect sheet — BehaviorSpace names it after the experiment
  sheet <- excel_sheets(filepath)[1]
  raw   <- read_excel(filepath, sheet = sheet, col_names = FALSE)
  
  run_nums  <- as.character(raw[8,  -1])
  var_names <- as.character(raw[12, -1])
  values    <- as.character(raw[13, -1])
  
  # Detect variables per run from where [step] repeats
  first_step_pos <- which(var_names == "[step]")
  vars_per_run   <- first_step_pos[2] - first_step_pos[1]
  var_block      <- var_names[1:vars_per_run]
  n_runs         <- length(run_nums) / vars_per_run
  
  cat("  ->", basename(filepath), "| sheet:", sheet,
      "| runs:", n_runs, "| vars:", vars_per_run, "\n")
  
  # Clean variable names to R-friendly snake_case
  clean_names <- var_block |>
    trimws() |>
    gsub("\\[|\\]", "", x = _) |>
    gsub("[^a-zA-Z0-9]+", "_", x = _) |>
    gsub("^_|_$", "", x = _) |>
    tolower()
  
  # Build one row per run
  rows <- lapply(seq_len(n_runs), function(i) {
    s   <- (i - 1) * vars_per_run + 1
    row <- setNames(as.list(values[s:(s + vars_per_run - 1)]), clean_names)
    row$run        <- as.integer(run_nums[s])
    row$experiment <- experiment_label
    row
  })
  
  bind_rows(rows) |>
    select(experiment, run, everything()) |>
    mutate(across(-c(experiment), ~ suppressWarnings(as.numeric(.x))))
}


# --- 2. PROCESS ALL FILES ----------------------------------------------------

cat("Processing files...\n")
all_data <- mapply(
  reshape_one,
  filepath         = input_files,
  experiment_label = experiment_labels,
  SIMPLIFY         = FALSE
) |> bind_rows()

# --- 3. ADD DERIVED METRICS --------------------------------------------------

# Detect the FDI column name dynamically (it has a long formula-based name)
fdi_col <- names(all_data)[grepl("flow_count.*yellow", names(all_data))][1]

# 2. Only run this block if the raw column exists (prevents the "not found" error)
if (!is.na(fdi_col)) {
  all_data <- all_data |>
    mutate(
      # All metrics created directly as 0-100 percentages
      seizure_rate_pct      = (total_seized_value / (total_delivered_value + total_seized_value)) * 100,
      yellow_link_rate_pct   = (count_links_with_color_yellow / count_links) * 100,
      drug_through_yellow_rate_pct = .data[[fdi_col]] * 100,
      clustering_rate_pct    = mean_nw_clustering_coefficient_of_nodes * 100,
      
      # Logic flags
      never_adapted = if_else(first_yellow_tick == -1 | is.na(first_yellow_tick), TRUE, FALSE),
      
      # Factor decoding
      cartel_type          = if_else(grepl("Adaptive", experiment), "Adaptive", "Stubborn"),
      enforcement_target   = if_else(grepl("Busiest",  experiment), "Busiest",  "Random"),
      enforcement_duration = if_else(grepl("Long",     experiment), "Long",     "Short")
    ) |>
    # Drop original messy columns (using any_of for safety)
    select(-any_of(c(fdi_col, "mean_nw_clustering_coefficient_of_nodes")))
}

# 3. Round ALL numeric metrics to 2 decimals (keeps them as numbers for plots)
all_data <- all_data |> 
  mutate(across(where(is.numeric) & !run, ~ round(.x, 2)))

# --- 4. SUMMARY STATISTICS PER EXPERIMENT ------------------------------------

summary_stats <- all_data |>
  group_by(experiment, cartel_type, enforcement_target, enforcement_duration) |>
  summarise(
    n_runs                 = n(),
    
    # Deliveries
    mean_delivered         = mean(total_delivered_value, na.rm = TRUE),
    sd_delivered           = sd(total_delivered_value,   na.rm = TRUE),
    
    # Seizures
    mean_seized            = mean(total_seized_value,    na.rm = TRUE),
    sd_seized              = sd(total_seized_value,      na.rm = TRUE),
    
    # Seizure rate
    mean_seizure_rate_pct  = mean(seizure_rate_pct,      na.rm = TRUE),
    sd_seizure_rate_pct    = sd(seizure_rate_pct,        na.rm = TRUE),
    
    # Network structure
    mean_total_links       = mean(count_links,                         na.rm = TRUE),
    mean_yellow_links      = mean(count_links_with_color_yellow,       na.rm = TRUE),
    mean_yellow_link_rate_pct = mean(yellow_link_rate_pct,             na.rm = TRUE),
    
    # Drug through yellow links
    mean_drug_through_yellow_rate_pct = mean(drug_through_yellow_rate_pct, na.rm = TRUE),
    sd_drug_through_yellow_rate_pct = sd(drug_through_yellow_rate_pct, na.rm = TRUE),
    
    # Clustering
    mean_clustering_rate_pct        = mean(clustering_rate_pct, na.rm = TRUE),
    sd_clustering_rate_pct          = sd(clustering_rate_pct,   na.rm = TRUE),
    
    # Adaptation speed
    mean_first_yellow_tick = mean(
      first_yellow_tick[!is.na(first_yellow_tick) & first_yellow_tick != -1],
      na.rm = TRUE
    ),
    pct_never_adapted      = mean(never_adapted, na.rm = TRUE) * 100,
    
    .groups = "drop"
  )

summary_stats <- summary_stats |> 
  mutate(across(
    where(is.numeric) & !any_of(c("run", "n_runs")), 
    ~ round(.x, 2)
  ))


# --- 5. EXPORT (FIXED FOR PLOTS.RMD) -----------------------------------------

# Export RAW NUMERIC data to standard CSV format (comma separated)
# This prevents string corruption and ensures Plots.Rmd can read the data natively.
write.csv(all_data, output_tidy, row.names = FALSE)
write.csv(summary_stats, output_summary, row.names = FALSE)


# --- OPTIONAL: EXPORT "PRETTY" VERSION FOR EXCEL ONLY ------------------------
# If you still need a presentation-ready version for a spreadsheet, use this.
# Notice the correct across() syntax: c(where(is.numeric), -any_of(...))

format_for_excel <- function(df) {
  df %>%
    mutate(across(c(where(is.numeric), -any_of(c("run", "n_runs"))), ~ {
      # format() behaves better without forcing decimal.mark here; 
      # standard rounding keeps it clean.
      val <- format(round(.x, 2), nsmall = 2) |> trimws()
      if (grepl("pct", cur_column())) paste0(val, "%") else val
    }))
}

# Uncomment the lines below to generate the pretty versions
# write.csv2(format_for_excel(all_data), "all_experiments_tidy_PRETTY.csv", row.names = FALSE)
# write.csv2(format_for_excel(summary_stats), "all_experiments_summary_PRETTY.csv", row.names = FALSE)