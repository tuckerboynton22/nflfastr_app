library(tidyverse)
future::plan("multisession")

participation <- nflreadr::load_participation(seasons = 2016:2021)

pbp <- nflreadr::load_pbp(seasons = 1999:2021)

receivers <- pbp %>%
  select(receiver_id, receiver, posteam) %>%
  filter(!is.na(receiver_id)) %>%
  distinct() %>%
  group_by(receiver_id) %>%
  summarize(
    receiver = stringr::str_replace(last(receiver), " ", ""),
    posteam = paste0(posteam, collapse = ", ")
  ) %>%
  arrange(receiver)

rushers <- pbp %>%
  select(rusher_id, rusher, posteam) %>%
  filter(!is.na(rusher_id)) %>%
  distinct() %>%
  group_by(rusher_id) %>%
  summarize(
    rusher = stringr::str_replace(last(rusher), " ", ""),
    posteam = paste0(unique(posteam), collapse = ", ")
  ) %>%
  arrange(rusher)

names <- pbp %>%
  select(id, name, posteam) %>%
  filter(!is.na(id)) %>%
  distinct() %>%
  group_by(id) %>%
  summarize(
    name = stringr::str_replace(last(name), " ", ""),
    posteam = paste0(unique(posteam), collapse = ", ")
  ) %>%
  arrange(name)

passers <- pbp %>%
  select(passer_id, passer, posteam) %>%
  filter(!is.na(passer_id)) %>%
  distinct() %>%
  group_by(passer_id) %>%
  summarize(
    passer = stringr::str_replace(last(passer), " ", ""),
    posteam = paste0(unique(posteam), collapse = ", ")
  ) %>%
  arrange(passer)

conn <- DBI::dbConnect(RPostgres::Postgres(),
                       dbname = Sys.getenv("DB_NAME"),
                       host = Sys.getenv("DB_HOST"),
                       port = Sys.getenv("DB_PORT"),
                       user = Sys.getenv("DB_USER"),
                       password = Sys.getenv("DB_PASSWORD"))

nflfastR::update_db(db_connection = conn, tblname = "nflfastr_pbp", force_rebuild = FALSE)

DBI::dbWriteTable(conn, "participation", participation, overwrite = T)
DBI::dbWriteTable(conn, "receivers", receivers, overwrite = T)
DBI::dbWriteTable(conn, "rushers", rushers, overwrite = T)
DBI::dbWriteTable(conn, "names", names, overwrite = T)
DBI::dbWriteTable(conn, "passers", passers, overwrite = T)