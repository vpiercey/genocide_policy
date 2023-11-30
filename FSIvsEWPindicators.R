##To find data:
##EWP. Go to Github then repository, download base____-run-_____.csv from "Modelling folder"
##FSI - Get data directly from FSI website
##Alphabetize csv files, manually put in COW column in FSI (make sure to title "COW" exactly the same way). 
##From FSI, delete countries that don't exist in EWP (note some have different names, so put in codes first, then delte)
##countries deleted for 2022: 
##Antigua and Barbuda
##Bahamas
##Barbados
##Belize
##Brunei Darussalam
##Cabo Verde
##Grenada
##Iceland
##Luxembourg
##Maldives
##Malta
##Micronesia
##North Macedonia
##Palestine
##Samoa
##Sao Tome and Principe
##Seychelles
##Suriname
library(tidyverse)
library(readr)
ewp_2022 <- read_csv("Research/Genocide Resilience/2022 Data/base2021-run-2022-09-30.csv")
View(ewp_2022)
fsi_2022 <- read_excel("Research/Genocide Resilience/2022 Data/fsi-2022-download.xlsx")
View(fsi_2022)
indicators_2022 <- inner_join(ewp_2022, fsi_2022, by = "COW")

x<- c(6:17,19:36) #these are the EWP variables
y <- 41:52 #these are the FSI variables

corr_2022 <- indicators_2022 %>% select(x,y) %>% cor()
heatmap(corr_2022)
