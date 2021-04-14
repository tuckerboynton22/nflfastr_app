R code used for downloading play-by-play data:

(Courtesy of nflfastR starter guide)

library(tidyverse)
library(ggrepel)
library(ggimage)
library(nflfastR)

options(scipen = 9999)

data <- readRDS(url("https://raw.githubusercontent.com/guga31bb/nflfastR-data/master/data/play_by_play_2020.rds"))
write.csv(data, "/Users/tuckerboynton/Desktop/sampledata.csv")

SQL code used for converting CSV to table:

(Courtesy of SQLite Tutorial)

sqlite> .mode csv
sqlite> .import sampledata.csv sample_plays