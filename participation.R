library(nflreadr)

participation <- load_participation(seasons = 2016:2021)

write.csv(participation, "/Users/tuckerboynton/Desktop/R/App/nflfastr_app/participation.csv", row.names = F)
