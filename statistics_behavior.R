# =========================================================================
# IMPORTS
# =========================================================================

library(tidyverse)
library(afex)
library(emmeans)
library(effectsize)
library(rstatix)

# =========================================================================
# SETTINGS
# =========================================================================

reversible_pairs <- list(
  horizontal = list(c("b","d"), c("p","q")),
  vertical   = list(c("b","p"), c("d","q"))
)

letters_rev    <- c("b","d","p","q")
letters_nonrev <- c("r","a","e","f","h","k")

conditions <- tibble(
  condition = c("horizontal", "vertical", "90° rotation", "large"),
  suffix    = c("_normal_flip_h", "_normal_flip_v", "_normal_rot90", "_large")
)


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

get_cell <- function(mat, a, b) {
  if (a %in% rownames(mat) && b %in% colnames(mat)) {
    return(mat[a,b])
  }
  if (b %in% rownames(mat) && a %in% colnames(mat)) {
    return(mat[b,a])
  }
  NA_real_
}


safe_mean <- function(x) {
  if (all(!is.finite(x))) {
    return(NA_real_)
  }
  mean(x[is.finite(x)])
}


# reversible letters extraction

extract_reversible <- function(mat, participant) {
  
  map_dfr(conditions$condition, function(cond) {
    
    if (cond %in% c("horizontal","vertical")) {
      
      vals <- map_dbl(
        reversible_pairs[[cond]],
        function(pair) {
          
          get_cell(
            mat,
            paste0(pair[1], "_normal"),
            paste0(pair[2], "_normal")
          )
        }
      )
      
    } else {
      
      suffix <- conditions$suffix[
        conditions$condition == cond
      ]
      
      vals <- map_dbl(
        letters_rev,
        function(l) {
          
          get_cell(
            mat,
            paste0(l, "_normal"),
            paste0(l, suffix)
          )
          
        }
      )
    }
    tibble(
      participant   = participant,
      letter_class  = "reversible",
      condition     = cond,
      dissimilarity = safe_mean(vals)
    )
  })
}


# non-reversible letters extraction

extract_nonrev <- function(mat, participant) {
  
  map_dfr(conditions$condition, function(cond) {
    
    suffix <- conditions$suffix[
      conditions$condition == cond
    ]
    
    vals <- map_dbl(
      letters_nonrev,
      function(l) {
        
        get_cell(
          mat,
          paste0(l, "_normal"),
          paste0(l, suffix)
        )
      }
    )
    
    tibble(
      participant   = participant,
      letter_class  = "non_reversible",
      condition     = cond,
      dissimilarity = safe_mean(vals)
    )
  })
}


# paired Cohen's d

compute_paired_d <- function(df, cond1, cond2) {
  
  wide <- df %>%
    filter(condition %in% c(cond1, cond2)) %>%
    select(participant, condition, dissimilarity) %>%
    pivot_wider(
      names_from = condition,
      values_from = dissimilarity
    ) %>%
    drop_na(all_of(c(cond1, cond2)))
  
  if (nrow(wide) < 2) {
    
    return(
      tibble(
        d = NA_real_,
        ci_low = NA_real_,
        ci_high = NA_real_
      )
    )
    
  }
  
  wide_long <- wide %>%
    pivot_longer(
      cols = all_of(c(cond1, cond2)),
      names_to = "condition",
      values_to = "dissimilarity"
    ) %>%
    mutate(
      condition = factor(
        condition,
        levels = c(cond1, cond2)
      )
    )
  
  res <- cohens_d(
    wide_long,
    dissimilarity ~ condition,
    paired = TRUE,
    ci = TRUE
  )
  
  tibble(
    d      = res$effsize,
    ci_low = res$conf.low,
    ci_high = res$conf.high
  )
  
}

# =========================================================================
# LOAD RDM FILES
# =========================================================================

files <- list.files(
  "../rdms/behavior",
  pattern = "\\.csv$",
  full.names = TRUE
)

rdms <- set_names(
  lapply(
    files,
    function(f)
      as.matrix(read.csv(f, row.names = 1))
  ),
  tools::file_path_sans_ext(basename(files))
)

# =========================================================================
# BUILD DATASET
# =========================================================================

combo_df <- imap_dfr(
  rdms,
  function(mat, id) {
    
    bind_rows(
      extract_reversible(mat, id),
      extract_nonrev(mat, id)
    )
  }
) %>%
  mutate(
    participant = factor(participant),
    letter_class = factor(
      letter_class,
      levels = c(
        "reversible",
        "non_reversible"
      )
    ),
    
    condition = factor(
      condition,
      levels = conditions$condition
    )
  )

# =========================================================================
# REMOVE INCOMPLETE PARTICIPANTS
# =========================================================================

bad <- combo_df %>%
  group_by(participant) %>%
  summarise(
    bad = any(!is.finite(dissimilarity)),
    .groups = "drop"
  ) %>%
  filter(bad) %>%
  pull(participant)


combo_df_clean <- combo_df %>%
  filter(!participant %in% bad)

condition_levels <- levels(combo_df_clean$condition)

# =========================================================================
# ANOVA
# =========================================================================

anova_model <- aov_ez(
  id = "participant",
  dv = "dissimilarity",
  data = combo_df_clean,
  within = c(
    "letter_class",
    "condition"
  ),
  anova_table = list(
    correction = "GG",
    es = "pes"
  )
)

anova_model$anova_table

# =========================================================================
# REVERSIBLE VS NON-REVERSIBLE WITHIN CONDITIONS
# =========================================================================

emm_class <- emmeans(
  anova_model,
  ~ letter_class | condition
)

pairs_class <- pairs(
  emm_class,
  adjust = "holm"
)

pairs_class
confint(pairs_class)

d_class_by_cond <- combo_df_clean %>%
  group_by(condition) %>%
  filter(n_distinct(letter_class) == 2) %>%
  cohens_d(
    dissimilarity ~ letter_class,
    paired = TRUE,
    ci = TRUE
  )

d_class_by_cond

# =========================================================================
# CONDITIONS WITHIN EACH LETTER CLASS
# =========================================================================

emm_cond <- emmeans(
  anova_model,
  ~ condition | letter_class
)

pairs_cond_within <- pairs(
  emm_cond,
  adjust = "holm"
)

pairs_cond_within
confint(pairs_cond_within)

effect_sizes_conditions <- map_df(
  levels(combo_df_clean$letter_class),
  function(cls) {

    df_cls <- combo_df_clean %>%
      filter(letter_class == cls)
    
    combn(
      condition_levels,
      2,
      simplify = FALSE
    ) %>%
      map_df(function(p) {
        
        d_res <- compute_paired_d(
          df_cls,
          p[1],
          p[2]
        )
        
        tibble(
          letter_class = cls,
          contrast = paste(p, collapse = " - "),
          d = d_res$d,
          ci_low = d_res$ci_low,
          ci_high = d_res$ci_high
        )
        
      })
  }
)

effect_sizes_conditions

# =========================================================================
# CONDITIONS COLLAPSED ACROSS LETTER CLASS
# =========================================================================

emm_cond_overall <- emmeans(
  anova_model,
  ~ condition
)

pairs_cond_overall <- pairs(
  emm_cond_overall,
  adjust = "holm"
)

pairs_cond_overall
confint(pairs_cond_overall)

combo_df_collapsed <- combo_df_clean %>%
  group_by(
    participant,
    condition
  ) %>%
  summarize(
    dissimilarity = mean(dissimilarity),
    .groups = "drop"
  )

effect_sizes_conditions_overall <- combn(
  condition_levels,
  2,
  simplify = FALSE
) %>%
  map_df(function(p) {
    
    d_res <- compute_paired_d(
      combo_df_collapsed,
      p[1],
      p[2]
    )
    
    tibble(
      contrast = paste(p, collapse = " - "),
      d = d_res$d,
      ci_low = d_res$ci_low,
      ci_high = d_res$ci_high
    )
  })

effect_sizes_conditions_overall