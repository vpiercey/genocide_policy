## Enter COW data directly into FSI spreadsheet. 
## Since we have them all in 2022, we can use the 2022 to join by
## country with other FSI data and insert.

##Palestine does not have a COW value, and is not in the EWP data.
##This is because Palestine does not have significant international
##recognition as an independent nation.
##Delete Palestine row from FSI data.

library(tidyverse) #as is tradition
library(readr) #for CSV
library(readxl) #for Excel

#Read in FSI
fsi_2022 <- read_excel("Research/Genocide Resilience/FSI_EWP/data/fsi_2022.xlsx")
View(fsi_2022)

fsi_2021 <- read_excel("Research/Genocide Resilience/FSI_EWP/data/fsi_2021.xlsx")
View(fsi_2021)

#Add in COW for new FSI
fsi_COW <- fsi_2022[,1:2] #Keep only the columns with country name and COW from 2022
fsi_2021 <- inner_join(fsi_COW, fsi_2021, by = "Country") #add COW with inner join
#Check nothing funny going on - in this case, had extra COW columns, so deleted them.
fsi_2021 <- subset(fsi_2021, select = -c(3,4))

#Read in EWP
sra_2021 <- read_csv("Research/Genocide Resilience/FSI_EWP/data/sra_2021.csv")
View(sra_2021)

#Get rid of everything except COW and indicators
fsi_2021 <- subset(fsi_2021, select = -c(3,4,5))
sra_2021 <- subset(sra_2021, select = -c(2,4,5))

#Check to see if variance of any column for EWP is 0 (not a concern for FSI)
for (i in 3:33) {
  if (var(sra_2021[,i])==0){print(i)}
  if (var(sra_2021[,i]) > 0) {print("No Problem")}
}

#In this case, column 15 had variance 0. This is "includenonstate" which has to do with the inclusion of nonstate actors in the data, which they started to do in 1989. Next, delete this column.
sra_2021 <- subset(sra_2021, select = -c(15))

#We should be good to join the two dfs now! 
fsi_ewp_2021 <- merge(fsi_2021, sra_2021, by = "COW", all = TRUE) #the last gives us all rows even if not in both, so we can see if there is anything missing.

#Now we'll check for problems in the list of countries.
v <- c(1,2,15) #these are column numbers with countries and COW
countries_2021 <- fsi_ewp_2021[,v]

#We can see some EWP countries are not in FSI and vice versa.
#Next we remove rows that aren't in both.
#We could have done this from the start with inner join, but I Want to document which countries we removed and why. The df "countries" keeps this information.

#Remove the NAs
fsi_ewp_2021 <- na.omit(fsi_ewp_2021)
nrow(fsi_ewp_2021) #check that the number is correct. Should be 178 original rows minus 18 NAs.

#We can now reduce the df to only have the indicator values by making the country names into the row names, and deleting all but the indicators.
fsi_ewp_2021_final <- subset(fsi_ewp_2021, select = -c(1, 15))
rownames(fsi_ewp_2021_final) <- fsi_ewp_2021_final$Country
fsi_ewp_2021_final <- subset(fsi_ewp_2021_final, select = -c(1))

#now we make the heatmap of correlations. Columns 13 through 42 are EWP, columns 1 through 12 are FSI.
x <- fsi_ewp_2021_final[,1:12]
y <- fsi_ewp_2021_final[,13:42]
corr_2021 <- cor(x,y)
heatmap(corr_2021)

#And now the clustering
#Hierarchical clustering is iterative.
#In the first step, each row is its own cluster of one.
#The distance between each pair is calculated, and the pair with the smallest is joined into a cluster.
#Repeat. 
#To measure the distance between two clusters, there are multiple methods. The default, which we will use, is "complete"
#The "complete" method measures the distance between two clusters as the largest pairwise distance between pairs of observations, one in each cluster.
#Using this measure, the two clusters with the smallest distance are joined together in a single cluster.
#Note that there are several ways to measure distance between individual rows. The default, using dist(), is the Euclidean distance.

fsi_ewp_2021_final_std <- scale(fsi_ewp_2021_final) #have to standardize in order to do clustering - otherwise different scales will distort distances
fsi_ewp_2021_final_std <- t(fsi_ewp_2021_final_std) #Hclust clusters based on rows. Since we want to cluster the indicators, we need to make the indicators the rows using the transpose "t()" function.
#Note: the scale() function standardizes columns, and we need standardized rows for the clustering. So we had to use scale() first, then transpose.

clusters_2021 <- hclust(dist(fsi_ewp_2021_final_std))
plot(clusters_2021)