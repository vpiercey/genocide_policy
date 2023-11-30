colkeep <- c(1:36,41:52)
> ind_numeric_2022 <- indicators_2022[,colkeep]
> View(ind_numeric_2022)
> View(ind_numeric_2022)
> View(ind_numeric_2022)
> ind_numeric_2022 <- indicators_2022 %>% select(colkeep)
Warning message:
  Using an external vector in selections was deprecated in tidyselect 1.1.0.
ℹ Please use `all_of()` or `any_of()` instead.
# Was:
data %>% select(colkeep)

# Now:
data %>% select(all_of(colkeep))

See <https://tidyselect.r-lib.org/reference/faq-external-vector.html>.
This warning is displayed once every 8 hours.
Call `lifecycle::last_lifecycle_warnings()` to see where this warning was generated. 
> ind_numeric_2022 <- ind_numeric_2022 %>% select(!(2:5))
> rownames(ind_numeric_2022) <- ind_numeric_2022$country
Error in `.rowNamesDF<-`(x, value = value) : 
  duplicate 'row.names' are not allowed
In addition: Warning messages:
  1: Setting row names on a tibble is deprecated. 
2: non-unique value when setting 'row.names': ‘Indonesia’ 
> row.names(ind_numeric_2022) <- ind_numeric_2022$country
Error in `.rowNamesDF<-`(x, value = value) : 
  duplicate 'row.names' are not allowed
In addition: Warning messages:
  1: Setting row names on a tibble is deprecated. 
2: non-unique value when setting 'row.names': ‘Indonesia’ 
> ind_numeric_2022 <- ind_numeric_2022[-23,]
> row.names(ind_numeric_2022) <- ind_numeric_2022$country
Warning message:
  Setting row names on a tibble is deprecated. 
> ind_numeric_2022 <- ind_numeric_2022[,-1]
> View(ind_numeric_2022)
> ind_numeric_2022 <- indicators_2022 %>% select(colkeep)
> ind_numeric_2022 <- ind_numeric_2022 %>% select(!(2:5))
> ind_numeric_2022 <- ind_numeric_2022[-23,]
> row.names(ind_numeric_2022) <- ind_numeric_2022$country
Warning message:
  Setting row names on a tibble is deprecated. 
> ind_only_numeric_2022 <- ind_numeric_2022 %>% select(2:44)
> View(ind_only_numeric_2022)
> row.names(ind_only_numeric_2022) <- indicators_2022$country
Error in `.rowNamesDF<-`(x, value = value) : invalid 'row.names' length
In addition: Warning message:
  Setting row names on a tibble is deprecated. 
> row.names(ind_only_numeric_2022) <- ind_numeric_2022$country
Warning message:
  Setting row names on a tibble is deprecated. 
> r <- cor(ind_only_numeric_2022[,1:31],ind_only_numeric_2022[,32,43])
Warning message:
  In cor(ind_only_numeric_2022[, 1:31], ind_only_numeric_2022[, 32,  :
                                                                the standard deviation is zero
                                                              > r <- cor(ind_only_numeric_2022)
                                                              Warning message:
                                                                In cor(ind_only_numeric_2022) : the standard deviation is zero
                                                              > final_inds_2022 <- t(ind_only_numeric_2022)
                                                              > View(final_inds_2022)
                                                              > std_ind_2022 <- scale(std_ind_2022)
                                                              Error: object 'std_ind_2022' not found
                                                              > View(indicators_2022)
                                                              > std_ind_2022 <- scale(ind_only_numeric_2022)
                                                              > View(std_ind_2022)
                                                              > View(r)
                                                              > x<- c(6:17,19:36) #these are the EWP variables
                                                              > y <- 41:52 #these are the FSI variables
                                                              > 
                                                                > corr_2022 <- indicators_2022 %>% select(x,y) %>% cor()
                                                              > source("C:/Users/piercev1/Documents/Research/Genocide Resilience/FSIvsEWPindicators.R", echo=TRUE)
                                                              
                                                              > ##To find data:
                                                                > ##EWP. Go to Github then repository, download base____-run-_____.csv from "Modelling folder"
                                                                > ##Get data directly from FSI websit .... [TRUNCATED] 
                                                                
                                                                > library(readr)
                                                              
                                                              > ewp_2022 <- read_csv("Research/Genocide Resilience/2022 Data/base2021-run-2022-09-30.csv")
                                                              Rows: 162 Columns: 36                                                                                                                                           
                                                              ── Column specification ─────────────────────────────────────────────────────────────────────────────────────────────────────
                                                              Delimiter: ","
                                                              chr  (2): country, SFTGcode
                                                              dbl (34): COW, risk_in_2022, risk_in_2022_23, anymk.ongoing, anymk.ever, reg.afr, reg.eap, reg.eur, reg.mna, reg.sca, cou...
                                                              
                                                              ℹ Use `spec()` to retrieve the full column specification for this data.
                                                              ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.
                                                              
                                                              > View(ewp_2022)
                                                              
                                                              > fsi_2022 <- read_excel("Research/Genocide Resilience/2022 Data/fsi-2022-download.xlsx")
                                                              
                                                              > View(fsi_2022)
                                                              
                                                              > indicators_2022 <- inner_join(ewp_2022, fsi_2022, by = "COW")
                                                              
                                                              > x<- c(6:17,19:36) #these are the EWP variables
                                                              
                                                              > y <- 41:52 #these are the FSI variables
                                                              
                                                              > corr_2022 <- indicators_2022 %>% select(x,y) %>% cor()
                                                              
                                                              > heatmap(corr_2022)
                                                              > ind_for_clust <- t(std_ind_2022)
                                                              > View(ind_for_clust)
                                                              > ind_for_clust <- ind_for_clust[-"includesnonstate",]
                                                              Error in -"includesnonstate" : invalid argument to unary operator
                                                              > ind_for_clust <- ind_for_clust[-13,]
                                                              > clusters <- hclust(dist(ind_for_clust)
                                                                                   + 
                                                                                     + 
                                                                                     +   
                                                                                     + 
                                                                                     + )
                                                              > clusters <- hclust(dist(ind_for_clust))
                                                              > plot(clusters)
                                                              > View(corr_2022)
                                                              > View(ind_only_numeric_2022)
                                                              > View(std_ind_2022)
                                                              > ?t()
                                                              > ind_for_clust <- t(std_ind_2022)
                                                              > clusters <- hclust(dist(ind_for_clust))
                                                              Error in hclust(dist(ind_for_clust)) : 
                                                                NA/NaN/Inf in foreign function call (arg 10)
                                                              > ind_for_clust_safe <- ind_for_clust[-13,]
                                                              > View(ind_for_clust_safe)
                                                              > clusters <- hclust(dist(ind_for_clust_safe))
                                                              > plot(clusters)
                                                              > layout(1:1)
                                                              > plot(clusters)

                                                              ind_only_numeric_2022_safe <- ind_numeric_2022[,-13]
                                                              > View(ind_only_numeric_2022_safe)
                                                              > View(ind_only_numeric_2022)
                                                              > View(ind_only_numeric_2022_safe)
                                                              > colnames(ind_only_numeric_2022)[13]
                                                              [1] "includesnonstate"
                                                              > ind_only_numeric_2022_safe <- ind_numeric_2022 %>% select(-includesnonstate)
                                                              > r <- cor(ind_only_numeric_2022_safe[,1:31],ind_only_numeric_2022_safe[32:43])
                                                              Error in cor(ind_only_numeric_2022_safe[, 1:31], ind_only_numeric_2022_safe[32:43]) : 
                                                                'x' must be numeric
                                                              > ind_only_numeric_2022_safe <- ind_numeric_2022 %>% select(-includesnonstate)
                                                              > r <- cor(ind_only_numeric_2022_safe[,1:31],ind_only_numeric_2022_safe[32:43])
                                                              Error in cor(ind_only_numeric_2022_safe[, 1:31], ind_only_numeric_2022_safe[32:43]) : 
                                                                'x' must be numeric
                                                              > r <- cor(ind_only_numeric_2022_safe[1:31], ind_only_numeric_2022_safe[32:43])
                                                              Error in cor(ind_only_numeric_2022_safe[1:31], ind_only_numeric_2022_safe[32:43]) : 
                                                                'x' must be numeric
                                                              > r <- cor(ind_only_numeric_2022_safe[2:31], ind_only_numeric_2022_safe[32:43])
                                                              > heatmap(r)
                                                              > r <- t(r)
                                                              > heatmap(r)
                                                              > 