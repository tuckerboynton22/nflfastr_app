options(remove(list=ls()))

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

rosters <- nflreadr::load_rosters(seasons = 1999:2021)

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

kickers <- pbp %>%
  select(kicker_player_id, kicker_player_name, posteam) %>%
  filter(!is.na(kicker_player_id)) %>%
  distinct() %>%
  group_by(kicker_player_id) %>%
  summarize(
    kicker_player_name = stringr::str_replace(last(kicker_player_name), " ", "")
  ) %>%
  arrange(kicker_player_name)

players <- rosters %>%
  mutate(player = paste0(substr(first_name,1,1), ".", last_name)) %>%
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
DBI::dbWriteTable(conn, "kickers", kickers, overwrite = T)
DBI::dbWriteTable(conn, "players", players, overwrite = T)
DBI::dbWriteTable(conn, "season_rosters", season_rosters, overwrite = T)

## CREATE TABLE FOR QB PAGE

quarterbacks <- pbp %>%
  filter(down < 5, season_type == "REG", !is.na(qb_epa), pass == 1 | rush == 1, !is.na(id)) %>%
  mutate(no_play = ifelse(play_type == "no_play", 1, 0)) %>%
  group_by(name, id, season) %>%
  summarize(
    espn_plays = n() - sum(no_play, na.rm = T),
    plays = n(),
    dropbacks = sum(pass, na.rm = T),
    epa = mean(qb_epa, na.rm = T),
    t_epa = sum(qb_epa, na.rm = T),
    cpoe = mean(cpoe, na.rm = T),
    air_yards = mean(air_yards, na.rm = T),
    sack_rate = sum(sack, na.rm = T) / dropbacks,
    cp = mean(cp, na.rm = T),
    wpa = mean(wpa, na.rm = T),
    xpass = mean(xpass, na.rm = T),
    posteam = first(posteam)
  ) %>%
  ungroup() %>%
  mutate(is_eligible = case_when(
    # season == 2022 & espn_plays >= min_plays & dropbacks >= min_plays ~ 1,
    espn_plays >= 300 & dropbacks >= 250 ~ 1,
    TRUE ~ 0
  )) %>%
  filter(is_eligible == 1)

any_att <- pbp %>%
  filter(down < 5, season_type == "REG", pass == 1 | qb_spike == 1, play_type != "no_play" | qb_spike == 1, play_type != "run") %>%
  group_by(name, id, season) %>%
  summarize(
    n = n(),
    sack_yards = sum(yards_gained*sack, na.rm = T),
    sacks = sum(sack, na.rm = T),
    pass_yards = sum(yards_gained*complete_pass, na.rm = T),
    pass_att = sum(pass_attempt-sack, na.rm = T),
    pass_tds = sum(pass_touchdown, na.rm = T),
    interceptions = sum(interception, na.rm = T),
    any_att = (pass_yards + sack_yards + 20*pass_tds - 45*interceptions)/(pass_att + sacks),
    spikes = sum(qb_spike, na.rm = T)
  ) %>%
  filter(n > 99) %>%
  ungroup() %>%
  select(id, season, any_att)

dvoa <- readxl::read_excel("Data/dvoa.xlsx") %>%
  select(-QBR)

full_rosters <- nflreadr::load_rosters(seasons = 1999:2021) %>%
  filter(position == "QB") %>%
  rename(espn_id_roster = espn_id) %>%
  filter(!is.na(gsis_id)) %>%
  left_join(nflreadr::load_ff_playerids() %>% select(-c(pff_id)), by="gsis_id") %>%
  mutate(
    espn_id = case_when(
      season == 2010 & full_name == "Jay Cutler" ~ "9597",
      !is.na(espn_id) ~ as.character(espn_id),
      !is.na(espn_id_roster) ~ as.character(espn_id_roster),
      TRUE ~ NA_character_),
    qbr_join = ifelse(is.na(espn_id), full_name, espn_id)) %>%
  mutate(pff_id = as.numeric(pff_id)) %>%
  rename(team = team.x) %>%
  select(full_name, qbr_join, season, team, gsis_id, pff_id, espn_id, headshot_url) %>%
  distinct()

donovan_missing <- full_rosters %>%
  filter(full_name == "Donovan McNabb", season == 2005) %>%
  mutate(season = 2006)

schaub_missing <- full_rosters %>%
  filter(full_name == "Matt Schaub", season == 2010) %>%
  mutate(season = 2011)

full_rosters <- rbind(full_rosters, donovan_missing) %>%
  rbind(schaub_missing)

no_espn_id <- full_rosters %>%
  filter(is.na(espn_id)) %>%
  select(full_name, season, gsis_id) %>%
  rename(name_display = full_name) %>%
  mutate(missing_espn = 1) %>%
  distinct()

qbrs <- nflreadr::load_espn_qbr(seasons = 2006:2021) %>%
  filter(season_type == "Regular") %>%
  left_join(no_espn_id, by=c("name_display","season")) %>%
  mutate(qbr_join = ifelse(is.na(missing_espn), player_id, name_display))

quarterbacks_enriched <- quarterbacks %>%
  left_join(full_rosters, by=c("id"="gsis_id", "season")) %>%
  left_join(qbrs, by=c("qbr_join","season")) %>%
  # left_join(pff, by=c("pff_id"="player_id", "season")) %>%
  left_join(dvoa, by=c("name"="Player","season"="Year")) %>%
  # left_join(caphits, by=c("full_name"="Player","season"="Year")) %>%
  left_join(nflreadr::load_teams(), by=c("posteam"="team_abbr")) %>%
  left_join(any_att, by=c("id", "season")) %>%
  mutate(
    # pff = grades_offense,
    # qbr_pct = percent_rank(qbr_total)*100,
    # DVOA_pct = percent_rank(DVOA)*100,
    # DYAR_pct = percent_rank(DYAR)*100,
    # PFF_pct = percent_rank(grades_offense)*100,
    # pa_pct = percent_rank(team_pa)*100,
    # pblk_pct = percent_rank(grades_pblk)*100,
    # recv_pct = percent_rank(grades_recv)*100
  ) %>%
  rename(
    team = team.x,
    dvoa = DVOA,
    dyar = DYAR,
    num_plays = plays
  ) %>%
  mutate(
    dvoa = dvoa*100,
    sack_rate = sack_rate*100
  ) %>%
  select(
    headshot_url,
    full_name,
    team_wordmark,
    season,
    team,
    num_plays,
    epa,
    t_epa,
    cpoe,
    dvoa,
    dyar,
    # pff,
    qbr_total,
    sack_rate,
    any_att,
    air_yards
  ) %>%
  distinct() %>%
  arrange(full_name, season)

DBI::dbWriteTable(conn, "qbs", quarterbacks_enriched, overwrite = T)

## GET QB GAME LOG

qb_gamelog <- pbp %>%
  filter(down < 5, season_type == "REG", !is.na(qb_epa), pass == 1 | rush == 1, !is.na(id)) %>%
  mutate(no_play = ifelse(play_type == "no_play", 1, 0)) %>%
  group_by(name, id, season, game_id) %>%
  summarize(
    posteam = first(posteam),
    espn_plays = n() - sum(no_play, na.rm = T),
    tot_plays = n(),
    dropbacks = sum(pass, na.rm = T),
    cmp = sum(complete_pass, na.rm = T),
    att = sum(pass_attempt-sack, na.rm = T),
    cpoe = mean(cpoe, na.rm = T),
    tds = sum(pass_touchdown, na.rm = T) + sum(rush_touchdown, na.rm = T),
    epa = mean(qb_epa, na.rm = T),
    t_epa = sum(qb_epa, na.rm = T),
    sack_epa = sum(qb_epa*sack, na.rm = T),
    pass_epa = sum(qb_epa*(pass_attempt-sack), na.rm = T),
    rush_epa = sum(qb_epa*rush_attempt, na.rm = T),
    air_yards = mean(air_yards, na.rm = T),
    cmp_air_yards = sum(air_yards*complete_pass, na.rm = T),
    wpa = sum(wpa, na.rm = T)
  ) %>%
  ungroup() %>%
  filter(espn_plays >= 20, dropbacks >= 10) %>%
  left_join(full_rosters, by=c("id"="gsis_id", "season"))

DBI::dbWriteTable(conn, "qb_gamelog", qb_gamelog, overwrite = T)
