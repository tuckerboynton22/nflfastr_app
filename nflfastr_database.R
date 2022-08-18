library(tidyverse)
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

# quarterbacks <- pbp %>%
#   filter(down < 5, season_type == "REG", !is.na(qb_epa), pass == 1 | rush == 1) %>%
#   mutate(no_play = ifelse(play_type == "no_play", 1, 0)) %>%
#   group_by(name, id, season) %>%
#   summarize(
#     espn_plays = n() - sum(no_play),
#     plays = n(),
#     dropbacks = sum(pass),
#     epa = mean(qb_epa, na.rm = T),
#     cpoe = mean(cpoe, na.rm = T),
#     air_yards = mean(air_yards, na.rm = T),
#     sack_rate = sum(sack, na.rm = T) / dropbacks,
#     cp = mean(cp, na.rm = T),
#     wpa = mean(wpa, na.rm = T),
#     xpass = mean(xpass, na.rm = T)
#   ) %>%
#   ungroup() %>%
#   mutate(is_eligible = case_when(
#     # season == 2021 & espn_plays >= min_plays & Dropbacks >= min_plays ~ 1,
#     espn_plays >= 300 & dropbacks >= 250 ~ 1,
#     TRUE ~ 0
#   )) %>%
#   filter(is_eligible == 1) %>%
#   merge(roster, by.x=c("id","season"), by.y=c("gsis_id","season")) %>%
#   merge(qbrs, by.x=c("qbr_join","season"),by.y=c("qbr_join","season")) %>%
#   merge(pff, by.x=c("pff_id","season"), by.y=c("player_id","season")) %>%
#   merge(teams_colors_logos, by.x=c("team.x"), by.y=c("team_abbr")) %>%
#   merge(dvoa, by.x=c("name.x","season"), by.y=c("Player","Year")) %>%
#   left_join(caphits, by=c("full_name"="Player","season"="Year")) %>%
#   merge(pff_teams, by.x=c("team_name.y","season"), by.y=c("team","season"), all.x = T) %>%
#   left_join(num_games, by=c("team.x"="posteam","season"="season")) %>%
#   mutate(
#     pa = ifelse(is.na(team_games), team_pa / 16, team_pa / team_games),
#     PFF = grades_offense,
#     qbr_pct = percent_rank(qbr_total)*100,
#     DVOA_pct = percent_rank(DVOA)*100,
#     DYAR_pct = percent_rank(DYAR)*100,
#     PFF_pct = percent_rank(grades_offense)*100,
#     pa_pct = percent_rank(team_pa)*100,
#     pblk_pct = percent_rank(grades_pblk)*100,
#     recv_pct = percent_rank(grades_recv)*100
#   ) %>%
#   rename(
#     name = name.x,
#     team = team.x,
#     position = position.x,
#     team_name = team.y,
#     team_name_alt = team_name.x,
#     full_team_name = team_name.y
#   ) %>%
#   select(
#     headshot_url,
#     full_name,
#     season,
#     team_logo_espn,
#     Plays,
#     EPA_pct,
#     CPOE_pct,
#     DVOA_pct,
#     DYAR_pct,
#     PFF_pct,
#     qbr_pct,
#     sack_rate_pct,
#     air_yards_pct,
#     cp_pct,
#     recv_pct,
#     pblk_pct,
#     pa_pct,
#     EPA,
#     CPOE,
#     DVOA,
#     DYAR,
#     PFF,
#     qbr_total,
#     sack_rate,
#     air_yards,
#     cp,
#     grades_recv,
#     grades_pblk,
#     pa,
#     team_wordmark
#   ) %>%
#   distinct() %>%
#   arrange(full_name, season)

rosters <- nflreadr::load_rosters_weekly(seasons = 2002:2021)

season_rosters <- nflreadr::load_ff_playerids() %>%
  rename(full_name = name)

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

kickers <- pbp %>%
  select(kicker_player_id, kicker_player_name, posteam) %>%
  filter(!is.na(kicker_player_id)) %>%
  distinct() %>%
  group_by(kicker_player_id) %>%
  summarize(
    kicker_player_name = stringr::str_replace(last(kicker_player_name), " ", "")
  ) %>%
  arrange(kicker_player_name)

qbs <- read_csv("qb_comps.csv")

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
DBI::dbWriteTable(conn, "kickers", kickers, overwrite = T)
DBI::dbWriteTable(conn, "players", players, overwrite = T)
DBI::dbWriteTable(conn, "season_rosters", season_rosters, overwrite = T)

DBI::dbWriteTable(conn, "qbs", qbs, overwrite = T)

test <- nflreadr::load_ff_playerids()
