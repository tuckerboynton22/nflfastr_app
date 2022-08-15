library(tidyverse)
library(sjmisc)
future::plan("multisession")

participation <- nflreadr::load_participation(seasons = 2016:2021) %>%
  mutate(
    o_personnel = case_when(
      stringr::str_detect(offense_personnel, "0 RB") & stringr::str_detect(offense_personnel, "0 TE") ~ "00",
      stringr::str_detect(offense_personnel, "0 RB") & stringr::str_detect(offense_personnel, "1 TE") ~ "01",
      stringr::str_detect(offense_personnel, "0 RB") & stringr::str_detect(offense_personnel, "2 TE") ~ "02",
      stringr::str_detect(offense_personnel, "1 RB") & stringr::str_detect(offense_personnel, "0 TE") ~ "10",
      stringr::str_detect(offense_personnel, "1 RB") & stringr::str_detect(offense_personnel, "1 TE") ~ "11",
      stringr::str_detect(offense_personnel, "1 RB") & stringr::str_detect(offense_personnel, "2 TE") ~ "12",
      stringr::str_detect(offense_personnel, "1 RB") & stringr::str_detect(offense_personnel, "3 TE") ~ "13",
      stringr::str_detect(offense_personnel, "2 RB") & stringr::str_detect(offense_personnel, "0 TE") ~ "20",
      stringr::str_detect(offense_personnel, "2 RB") & stringr::str_detect(offense_personnel, "1 TE") ~ "21",
      stringr::str_detect(offense_personnel, "2 RB") & stringr::str_detect(offense_personnel, "2 TE") ~ "22",
      stringr::str_detect(offense_personnel, "2 RB") & stringr::str_detect(offense_personnel, "3 TE") ~ "23"
    ),
    dl = substr(stringr::str_extract(defense_personnel, regex('([1-9]*) DL')),1,1),
    lb = substr(stringr::str_extract(defense_personnel, regex('([1-9]*) LB')),1,1)
  )

pbp <- nflreadr::load_pbp(seasons = 1999:2021)

snap_counts <- nflreadr::load_snap_counts(seasons = 2013:2021)

rosters <- nflreadr::load_rosters_weekly(seasons = 2016:2021)

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

players <- rosters %>%
  mutate(player = paste0(substr(first_name,1,1), ".", last_name),
         team = team_abbr) %>%
  filter(!is.na(gsis_id)) %>%
  select(gsis_id, player, team) %>%
  distinct() %>%
  group_by(gsis_id) %>%
  summarize(
    player = last(player),
    team = paste0(team, collapse = ", ")
  ) %>%
  arrange(player)

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
DBI::dbWriteTable(conn, "players", players, overwrite = T)