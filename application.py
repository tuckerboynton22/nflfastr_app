import os
import datetime
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Create global filters
filters = {
    "epa":"Expected Points Added (EPA)",
    "cpoe": "Completion % Over Expected (CPOE)",
    "wpa": "Win Probability Added (WPA)",
    "success": "Success",
    "ydstogo": "Yards to Go",
    "yards_gained": "Yards Gained",
    "air_yards": "Air Yards",
    "yards_after_catch": "Yards After Catch (YAC)",
    "qb_epa": "QB EPA",
    "cp": "Completion Probability",
    "xpass": "Dropback Probability",
    "week": "Week",
    "play_clock": "Seconds on Play Clock",
    "yardline_100": "Yard Line (Distance from Off. EZ)",
    "score_differential": "Current Score Differential (Off-Def)",
    "kick_distance": "Kick Distance",
    "quarter_seconds_remaining": "Seconds Remaining in Quarter",
    "ep": "Expected Points",
    "comp_air_epa": "Completed Air EPA",
    "air_epa": "Air EPA",
    "comp_yac_epa": "Completed YAC EPA",
    "yac_epa": "YAC EPA",
    "vegas_wp": "Vegas-Adjusted Win Probability",
    "wp": "Non-Vegas Adjusted Win Probability",
    "comp_air_wpa": "Completed Air WPA",
    "comp_yac_wpa": "Completed YAC WPA",
    "total_line": "Vegas Total",
    "xyac_mean_yardage": "Mean Expected YAC",
    "xyac_epa": "Expected YAC EPA",
    "ydsnet": "Total Yards on Drive",
    "drive_play_count": "Total Plays on Drive",
    "drive_quarter_start": "Drive Quarter Start",
    "drive_quarter_end": "Drive Quarter End"
}

# Create global groupings
groupings = {
    "name": "Passer/Rusher",
    "passer": "Passer",
    "rusher": "Rusher",
    "receiver": "Receiver",
    "kicker_player_name": "Kicker",
    "punter_player_name": "Punter",
    "posteam": "Offense",
    "defteam": "Defense",
    "game_id": "Game",
    "season": "Season",
    "week": "Week",
    "drive": "Drive Number"
}

# Create global play types
play_types = {
    "pass": "Pass",
    "rush": "Rush",
    "kickoff": "Kickoff",
    "punt": "Punt",
    "field_goal": "FG",
    "extra_point": "PAT",
    "two_point_attempt": "2PAT",
    "no_play": "No Play"
}

# Create global quarters
quarters = {
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "4th",
    "5": "OT"
}

# Create global downs
downs = {
    "1": "1st",
    "2": "2nd",
    "3": "3rd",
    "4": "4th",
    "5": "None"
}

post_weeks = {
    "None": "None",
    "Any": "Any",
    "Wild Card": 18,
    "Divisional": 19,
    "Conf Champ": 20,
    "Super Bowl": 21
}

# indicators = {
#     "penalty": "Penalty",
#     "turnover": "Turnover",
#     "score": "Score"
# }

# Configure application
app = Flask(__name__)

# Update database
db = SQL(os.getenv("DATABASE_URL"))
# db = SQL("sqlite:///cleaned_pbp.db")
# db = SQL("sqlite:///pbp.db")

# passers = db.execute("SELECT DISTINCT passer_id, FIRST(DISTINCT CAST(passer AS TEXT), ', ') AS passer FROM nflfastR_pbp WHERE passer_id !='' GROUP BY passer_id ORDER BY passer")
# names = db.execute("SELECT DISTINCT id, FIRST(DISTINCT CAST(name AS TEXT), ', ') AS name FROM nflfastR_pbp WHERE id !='' GROUP BY id ORDER BY name")
# rushers = db.execute("SELECT DISTINCT rusher_id, FIRST(DISTINCT CAST(rusher AS TEXT), ', ') AS rusher FROM nflfastR_pbp WHERE rusher_id !='' GROUP BY rusher_id ORDER BY rusher")
# receivers = db.execute("SELECT DISTINCT receiver_id, FIRST(DISTINCT CAST(receiver AS TEXT), ', ') AS receiver FROM nflfastR_pbp WHERE receiver_id !='' GROUP BY receiver_id ORDER BY receiver")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Apology
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# Homepage
@app.route("/", methods=["GET"])
def homepage():
    return render_template("homepage.html")

# Play index
@app.route("/index", methods=["GET"])
def index():

    # Provide form for query
    # teams = db.execute("SELECT DISTINCT posteam FROM nflfastR_pbp WHERE posteam!='' ORDER BY posteam")
    teams = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
                "LA", "LAC", "LV", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"]

    inequalities = ["=", ">", "<"]

    seasons = [x for x in range(2021, 1998, -1)]

    reg_weeks = ["Any", "None", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

    return render_template("index.html", teams=teams, groupings=groupings, filters=filters,
                            inequalities=inequalities, seasons=seasons, play_types=play_types,
                            quarters=quarters, reg_weeks=reg_weeks, post_weeks=post_weeks, downs=downs,
                            # passers=passers, names=names, rushers=rushers, receivers=receivers,
                            NUMFILTERS=5)

# Provide search results
@app.route("/results", methods=["GET", "POST"])
def results():
    """

    Note: all variables with 'results' suffix are created for front-facing search description to be displayed
    along with search results.

    """

    # Create player query
    player_query = ""
    player_results = ""

    passer = ""
    receiver = ""
    rusher = ""
    name = ""

    # if request.args.get("passer") != "":
        # passer = request.args.get("passer").split('(')[1][:-1]
    # if request.args.get("receiver") != "":
        # receiver = request.args.get("receiver").split('(')[1][:-1]
    # if request.args.get("rusher") != "":
        # rusher = request.args.get("rusher").split('(')[1][:-1]
    # if request.args.get("name") != "":
        # name = request.args.get("name").split('(')[1][:-1]

    # if passer != "":
        # player_query = " AND passer_id = '" + passer + "' "
    # if receiver != "":
        # player_query = player_query + " AND receiver_id = '" + receiver + "' "
    # if rusher != "":
        # player_query = player_query + " AND rusher_id = '" + rusher + "' "
    # if name != "":
        # player_query = player_query + " AND id = '" + name + "' "

    # Create team query
    team_query = ""
    team_results = ""
    opp_results = ""

    team = request.args.get("team")
    opp = request.args.get("opp")
    home = request.args.get("home")
    offense = request.args.get("offense")

    if team != "" and opp == "":
        team_results = team
        opp_results = "any team"
        if home != "":
            team_query = team_query + " AND " + home + "='" + team + "' "
        if offense != "":
            team_query = team_query + " AND " + offense + "='" + team + "' "
        elif offense == "" and home == "":
            team_query = team_query + " AND(posteam='" + team + "' OR defteam='" + team + "') "

    elif team == "" and opp != "":
        team_results = "any team"
        opp_results = opp
        team_query = team_query + " AND(posteam='" + opp + "' OR defteam='" + opp + "') "
        if home != "":
            team_query = team_query + " AND " + home + "!='" + opp + "' "
        if offense != "":
            team_query = team_query + " AND " + offense + "!='" + opp + "' "

    elif request.args.get("team") != "" and request.args.get("opp") != "":
        team_results = team
        opp_results = opp
        team_query = team_query + " AND((posteam='" + opp + "' AND defteam='" + team + "') OR (posteam='" + team + "' AND defteam='" + opp + "')) "
        if home != "":
            team_query = team_query + " AND " + home + "='" + team + "' "
        if offense != "":
            team_query = team_query + " AND " + offense + "='" + team + "' "

    else:
        team_results = "any team"
        opp_results = "any team"
    
    # Set offense/defense results
    posteam_results = ""
    defteam_results = ""
    if request.args.get("offense") == "posteam":
        posteam_results = team_results
        defteam_results = opp_results
    elif request.args.get("offense") == "defteam":
        posteam_results = opp_results
        defteam_results = team_results
    else:
        posteam_results = "any team"
        defteam_results = "any team"

    # Set home/away results
    home_team_results = ""
    away_team_results = ""
    if request.args.get("home") == "home_team":
        home_team_results = team_results
        away_team_results = opp_results
    elif request.args.get("home") == "away_team":
        away_team_results = opp_results
        home_team_results = team_results
    else:
        home_team_results = "any team"
        away_team_results = "any team"
            
    # Identify start and end seasons
    season_start = int(request.args.get("start"))
    season_end = int(request.args.get("end"))

    # Create week query
    if request.args.get("start_reg_week") != "Any":
        start_reg_week = str(request.args.get("start_reg_week"))
    else:
        start_reg_week = "1"

    if request.args.get("end_reg_week") != "Any":
        end_reg_week = str(request.args.get("end_reg_week"))
    else:
        end_reg_week = "18"
    
    if request.args.get("start_post_week") != "Any":
        start_post_week = str(request.args.get("start_post_week"))
    else:
        start_post_week = "18"

    if request.args.get("end_post_week") != "Any":
        end_post_week = str(request.args.get("end_post_week"))
    else:
        end_post_week = "22"
    
    if start_reg_week != "None" and end_reg_week != "None":
        reg_week_query = " (season_type = 'REG' AND week <= " + end_reg_week + " AND week >= " + start_reg_week + ") "
    else:
        reg_week_query = ""

    if start_post_week != "None" and end_post_week != "None":
        post_week_query = " ((season_type = 'POST' AND week <= " + end_post_week + " AND week >= " + start_post_week + " AND season <= 2020) OR " \
                            "(season_type = 'POST' AND week <= " + str(int(end_post_week)+1) + " AND week >= " + str(int(start_post_week)+1) + " AND season >= 2021))"
    else:
        post_week_query = ""
    
    if reg_week_query != "" and post_week_query != "":
        week_query = " AND(" + reg_week_query + " OR " + post_week_query + ") "
        week_results = "REG Wks: " + start_reg_week + "-" + end_reg_week + ", POST Wks: " \
                         + str(int(start_post_week)-17) + "-" + str(int(end_post_week)-17) + ". "
    elif reg_week_query != "":
        week_query = " AND" + reg_week_query
        week_results = "REG Wks: " + start_reg_week + "-" + end_reg_week + ", POST Wks: None. "
    elif post_week_query != "":
        week_query = " AND" + post_week_query
        week_results = "REG Wks: None, POST Wks: " + str(int(start_post_week)-17) + "-" + str(int(end_post_week)-17) + ". "
    else:
        week_query = ""
        week_results = "REG Wks: None, POST Wks: None. "

    # Create quarter query
    qtr_query = ""
    for quarter in quarters:
        if str(request.args.get(quarter)) in quarters:
            if qtr_query == "":
                if str(request.args.get(quarter)) == "5":
                    qtr_query = " AND(qtr=5 OR qtr=6"
                    qtrs = "OT"
                else:
                    qtr_query = " AND(qtr=" + str(request.args.get(quarter))
                    qtrs = str(request.args.get(quarter))
            else:
                if str(request.args.get(quarter)) == "5":
                    qtr_query = qtr_query + " OR qtr=5 OR qtr=6"
                    qtrs = qtrs + ", OT"
                else:
                    qtr_query = qtr_query + " OR qtr=" + str(request.args.get(quarter))
                    qtrs = qtrs + ", " + str(request.args.get(quarter))
    if qtr_query != "":
        qtr_query = qtr_query + ") "
    
    # Create down query
    down_query = ""
    for down in downs:
        if str(request.args.get(down + '_down')) in downs:
            if down_query == "":
                if str(request.args.get(down + '_down')) == "5":
                    down_query = " AND(down IS NULL"
                    dwns = "None"
                else:
                    down_query = " AND(down=" + str(request.args.get(down + '_down'))
                    dwns = str(request.args.get(down + '_down'))
            else:
                if str(request.args.get(down + '_down')) == "5":
                    down_query = down_query + " OR down IS NULL"
                    dwns = dwns + ", None"
                else:
                    down_query = down_query + " OR down=" + str(request.args.get(down + '_down'))
                    dwns = dwns + ", " + str(request.args.get(down + '_down'))
    if down_query != "":
        down_query = down_query + ") "

    # Create play type query
    play_type_query = ""
    play_type_results = ""
    for play in play_types:
        playtype = str(request.args.get(play))
        if playtype != "rush" and playtype != "pass" and playtype != "two_point_attempt" and playtype in play_types.keys():
            if play_type_query == "":
                play_type_query = "AND(play_type='" + str(request.args.get(play)) + "' "
                play_type_results = " " + str(play_types[playtype])
            else:
                play_type_query = play_type_query + "OR play_type='" + playtype + "' "
                play_type_results = play_type_results + ", " + play_types[playtype]
        elif (playtype == "pass" or playtype == "rush" or playtype == "two_point_attempt") and playtype in play_types.keys():
            if play_type_query == "":
                play_type_query = " AND(" + playtype + "=1 "
                play_type_results = " "  + play_types[playtype]
            else:
                play_type_query = play_type_query + " OR " + play + "=1 "
                play_type_results = play_type_results + ", " + play_types[playtype]

    if play_type_query != "":
        play_type_query = play_type_query + ") "

    # Create filter query and dictionary for column titles on results page
    filter_query = ""
    filter_dict = {}
    filter_results = ""
    select = ""
    NUMFILTERS = 5
    for i in range(NUMFILTERS):
        # Set variables to iterate over filter, inequality, and filter value for all filters
        filt = "filter"+str(i)
        inequal = "inequality"+str(i)
        filtval = "filtervalue"+str(i)

        if request.args.get(filt) != "" and request.args.get(inequal) != "" and request.args.get(filtval) != "":
            filter_query = filter_query + " AND " + str(request.args.get(filt)) + str(request.args.get(inequal)) \
                            + str(request.args.get(filtval)) + " AND " + str(request.args.get(filt)) + " IS NOT NULL "
            select = select + str(request.args.get(filt)) + ", "
            filter_dict[request.args.get(filt)] = filters[request.args.get(filt)]
            filter_results = filter_results + ", " + str(filters[request.args.get(filt)]) + str(request.args.get(inequal)) + str(request.args.get(filtval))

    # Set desired sorting mechanism
    sort = [request.args.get("sort"), filters[request.args.get("sort")]]
    select = select + request.args.get("sort") + ", "
    order = request.args.get("order")

    # Create penalty query
    if request.args.get("penalty") != "either":
        penaltyindicator = " AND penalty=" + request.args.get("penalty") + " "
        if request.args.get("penalty") == "1":
            penaltyresults = "A penalty, "
        else:
            penaltyresults = "No penalties, "
    else:
        penaltyindicator = ""
        penaltyresults = "Either penalty or no penalty, "

    # Create turnover query
    if request.args.get("turnover") == "1":
        turnoverindicator = " AND (interception=1 OR fumble_lost=1) "
        turnoverresults = "a turnover, "
    elif request.args.get("turnover") == "0":
        turnoverindicator = " AND interception=0 AND fumble_lost=0 "
        turnoverresults = "no turnover, "
    else:
        turnoverindicator = ""
        turnoverresults = ""
    
    # Create completion query
    if request.args.get("complete_pass") == "1":
        completionindicator = " AND complete_pass = 1 "
        completionresults = "a complete pass, "
    elif request.args.get("complete_pass") == "0":
        completionindicator = " AND complete_pass = 0 "
        completionresults = "no complete pass, "
    else:
        completionindicator = ""
        completionresults = ""

    # Create score query
    if request.args.get("score") != "either":
        scoreindicator = " AND sp=" + request.args.get("score") + " "
        if request.args.get("score") == "1":
            scoreresults = "a score, "
        else:
            scoreresults = "no score, "
    else:
        scoreindicator = ""
        scoreresults = ""

    # Create sack query
    if request.args.get("sack") != "either":
        sackindicator = " AND sack=" + request.args.get("sack") + " "
        if request.args.get("sack") == "1":
            sackresults = "a sack, "
        else:
            sackresults = "no sack, "
    else:
        sackindicator = ""
        sackresults = ""
    
    # Create interception query
    if request.args.get("interception") != "either":
        intindicator = " AND interception=" + request.args.get("interception") + " "
        if request.args.get("interception") == "1":
            intresults = "an interception, "
        else:
            intresults = "not an interception, "
    else:
        intindicator = ""
        intresults = ""

    # Create no-huddle query
    if request.args.get("no_huddle") != "either":
        nohuddleindicator = " AND no_huddle=" + request.args.get("no_huddle") + " "
        if request.args.get("no_huddle") == "1":
            nohuddleresults = "offense in no-huddle, "
        else:
            nohuddleresults = "offense huddled, "
    else:
        nohuddleindicator = ""
        nohuddleresults = ""

    # Create pass location query
    if request.args.get("pass_location") != "any":
        passlocquery = " AND pass_location='" + request.args.get("pass_location") + "' "
        if request.args.get("pass_location") == "left":
            passlocresults = "pass to the left, "
        elif request.args.get("pass_location") == "right":
            passlocresults = "pass to the right, "
        else:
            passlocresults = "pass to the middle, "
    else:
        passlocquery = ""
        passlocresults = ""

    # Create roof query
    if request.args.get("roof") != "any":
        roofindicator = " AND roof='" + request.args.get("roof") + "' "
        if request.args.get("roof") == "dome":
            roofresults = "game in dome"
        elif request.args.get("roof") == "outdoors":
            roofresults = "game outdoors"
        elif request.args.get("roof") == "closed":
            roofresults = "game in closed retroof"
        else:
            roofresults = "game in open retroof"
    else:
        roofindicator = ""
        roofresults = "game in any stadium"

    # Combine penalty, turnover, score, sack, interception, and roof queries for single indicator query
    indicators = penaltyindicator + passlocquery + turnoverindicator + scoreindicator + completionindicator + intindicator + sackindicator + nohuddleindicator + roofindicator
    indicator_results = penaltyresults + passlocresults + turnoverresults + scoreresults + completionresults + intresults + sackresults + nohuddleresults + roofresults

    # Create game-winner query
    winner = request.args.get("win")
    win_query = ""
    win_results = ""

    if winner == "won":
        win_query = " AND ((posteam = home_team AND home_score > away_score) OR (posteam = away_team AND home_score < away_score)) "
        win_results = ", possession team won"
    elif winner == "lost":
        win_query = " AND ((posteam = home_team AND home_score < away_score) OR (posteam = away_team AND home_score > away_score)) "
        win_results = ", possession team lost"
    elif winner == "tied":
        win_query = " AND home_score = away_score "
        win_results = ", game was a tie"

    # Create drive result query
    drive_result = request.args.get("drive_result")
    drive_result_query = ""
    drive_result_results = ""

    if int(drive_result) == 1:
        drive_result_query = " AND (drive_ended_with_score = 1) "
        drive_result_results = ", drive ended with score"
    elif int(drive_result) == 0:
        drive_result_query = " AND (drive_ended_with_score = 0) "
        drive_result_results = ", drive didn't end with score"

    # Set groupings
    grouping = ""
    grouping_id = ""
    grouping_null = ""
    group = request.args.get("grouping")
    group2 = request.args.get("grouping2")
    grouping_aggregator = ""

    if group == "name":
        grouping = group + ", id"
        grouping_id = "id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "passer":
        grouping = group + ", passer_id"
        grouping_id = "passer_id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "rusher":
        grouping = group + ", rusher_id"
        grouping_id = "rusher_id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "kicker_player_name":
        grouping = group + ", kicker_player_id"
        grouping_id = "kicker_player_id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "punter_player_name":
        grouping = group + ", punter_player_id"
        grouping_id = "punter_player_id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "receiver":
        grouping = group + ", receiver_id"
        grouping_id = "receiver_id"
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    elif group == "week":
        grouping = group + ", 'week'"
        grouping_id = "week"
        grouping_null = " AND '" + group + "' IS NOT NULL " + " AND LENGTH(CAST('" + group + "' AS TEXT))>0 "
    elif group != "":
        grouping = group
        grouping_id = group
        grouping_null = " AND " + group + " IS NOT NULL " + " AND LENGTH(CAST(" + group + " AS TEXT))>0 "
    
    if group != "" and group2 != "":
        grouping = grouping + ", "
        grouping_id = grouping_id + ", "
        grouping_aggregator =  "FIRST(DISTINCT CAST(" + group + " AS TEXT), ', ') AS " + group + ", FIRST(DISTINCT CAST(" + group2 + " AS TEXT), ', ') AS " + group2
    elif group != "" and group2 == "":
        grouping_aggregator =  "FIRST(DISTINCT CAST(" + group + " AS TEXT), ', ') AS " + group
    elif group == "" and group2 != "":
        grouping_aggregator =  "FIRST(DISTINCT CAST(" + group2 + " AS TEXT), ', ') AS " + group2

    if group2 == "name":
        grouping = grouping + group2 + ", id"
        grouping_id = grouping_id + "id"
        grouping_null = grouping_null + " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "passer":
        grouping = grouping + group2 + ", passer_id"
        grouping_id = grouping_id + "passer_id"
        grouping_null = " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "rusher":
        grouping = grouping + group2 + ", rusher_id"
        grouping_id = grouping_id + "rusher_id"
        grouping_null = " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "kicker_player_name":
        grouping = grouping + group2 + ", kicker_player_id"
        grouping_id = grouping_id + "kicker_player_id"
        grouping_null = grouping_null + " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "punter_player_name":
        grouping = grouping + group2 + ", punter_player_id"
        grouping_id = grouping_id + "punter_player)id"
        grouping_null = grouping_null + " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "receiver":
        grouping = grouping + group2 + ", receiver_id"
        grouping_id = grouping_id + "receiver_id"
        grouping_null = grouping_null + " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "
    elif group2 == "week":
        grouping = grouping + group2 + ", 'week'"
        grouping_id = grouping_id + "week"
        grouping_null = grouping_null + " AND '" + group2 + "' IS NOT NULL " + " AND LENGTH(CAST('" + group2 + "' AS TEXT))>0 "
    elif group2 != "":
        grouping = grouping + group2
        grouping_id = grouping_id + group2
        grouping_null = grouping_null + " AND " + group2 + " IS NOT NULL " + " AND LENGTH(CAST(" + group2 + " AS TEXT))>0 "

    if group != "":
        grouping_results = "Grouped by " + groupings[group]
        if group2 != "":
            grouping_results = grouping_results + ", " + groupings[group2] + "."
        else:
            grouping_results = grouping_results + "."
    elif group2 != "":
        grouping_results = "Grouped by " + groupings[group2] + "."
    else:    
        grouping_results = ""

    # Create minimum description
    if request.args.get("minimum") != "":
        minplays = int(request.args.get("minimum"))
        minplay_query = " HAVING COUNT(*) >=" + str(request.args.get("minimum")) + " "
    else:
        minplays = 0
        minplay_query = ""

    if minplay_query != "" and grouping != "":
        minplay_results = " Min. " + str(minplays) + " plays."
    else:
        minplay_results = ""

    total = request.args.get("total")

    # Create description of search for results page
    searchdesc = str(season_start) + "-" + str(season_end) + ", " + team_results \
                + " vs. " + opp_results + ", " + posteam_results + " on offense, " + defteam_results + " on defense, " \
                + home_team_results + " at home, " + away_team_results + " on the road. Quarters: " + qtrs + ". Downs: " + dwns + ". Play types: " \
                + play_type_results + ". " + indicator_results + filter_results + win_results + drive_result_results + ". " \
                + week_results + grouping_results + minplay_results

    select = select + ' season_type, season, home_team, away_team, posteam, defteam, "week", game_date, qtr, quarter_seconds_remaining, down, ydstogo, "desc" '

    # limit = request.args.get("limit")

    # If no grouping, pass list of plays to plays.html
    if grouping == "":    
        plays = db.execute("SELECT " + select + " FROM nflfastR_pbp WHERE \
                            season>=? AND season<=?"
                            + team_query + filter_query + indicators + win_query + drive_result_query \
                            + play_type_query + qtr_query + down_query + week_query + player_query \
                            + " AND " + sort[0] + " IS NOT NULL ORDER BY " + sort[0] + " " \
                            + order + " LIMIT 1000",
                            season_start, season_end)

        return render_template("plays.html", plays=plays, filter_dict=filter_dict, order=order, sort=sort, searchdesc=searchdesc, url=url)


    else:
        plays = db.execute("SELECT " + grouping_id + ", COUNT(*) AS total, \
                            AVG(epa) AS epa, " + grouping_aggregator \
                            + ", AVG(success) AS success, " \
                            + total + "(" + sort[0] + ") AS total_" + sort[0]  \
                            + ", FIRST(DISTINCT posteam, ', ') AS posteam"
                            + " FROM nflfastR_pbp WHERE season>=? AND season<=?" \
                            + " AND " + sort[0] + " IS NOT NULL AND success IS NOT NULL \
                            and epa IS NOT NULL" + grouping_null \
                            + team_query + filter_query + indicators + win_query + drive_result_query \
                            + play_type_query + qtr_query + down_query + week_query + player_query \
                            + "GROUP BY " + grouping_id + minplay_query \
                            + " ORDER BY total_" + sort[0] + " " + order + " LIMIT 1000",
                            season_start, season_end)
        
        url = request.url
        url = re.sub(r'grouping=[^&]*', 'grouping=', url)
        url = re.sub(r'grouping2=[^&]*', 'grouping2=', url)

        if group != "name" and group != "kicker_player_name" and group != "punter_player_name" and group != "receiver" \
            and group != "passer" and group != "rusher" and group2 != "passer" and group2 != "rusher" \
            and group2 != "name" and group2 != "kicker_player_name" and group2 != "punter_player_name" \
            and group2 != "receiver_player_name" and group2 != "week" and group != "week":

            return render_template("teams.html", plays=plays, order=order, sort=sort, group=group,
                                    group2=group2, groupings=groupings, searchdesc=searchdesc, url=url)

        else:
            return render_template("players.html", plays=plays, order=order, sort=sort, group=group,
                                    group2=group2, groupings=groupings, searchdesc=searchdesc)
    # elif limit == "Yes":
    #     plays = db.execute("SELECT " + grouping_id + ", COUNT(*) AS total, \
    #                             AVG(epa) AS epa, " + grouping_aggregator \
    #                             + ", AVG(success) AS success, " \
    #                             + total + "(" + sort[0] + ") AS total_" + sort[0]  \
    #                             + ", FIRST(DISTINCT posteam, ', ') AS posteam" \
    #                             + " FROM (" + "SELECT " + grouping_id + ", COUNT(*) AS total, \
    #                             AVG(epa) AS epa, " + grouping_aggregator \
    #                             + ", ROW_NUMBER() OVER(PARTITION BY " + grouping_id \
    #                             + ") as rownum, AVG(success) AS success, season, " \
    #                             + total + "(" + sort[0] + ") AS total_" + sort[0]  \
    #                             + ", FIRST(DISTINCT posteam, ', ') AS posteam" \
    #                             + " FROM nflfastR_pbp" \
    #                             + " WHERE season>=? AND season<=?" \
    #                             + " AND " + sort[0] + " IS NOT NULL AND success IS NOT NULL" \
    #                             + " AND epa IS NOT NULL" + grouping_null \
    #                             + team_query + filter_query + indicators + win_query \
    #                             + play_type_query + qtr_query + week_query \
    #                             + "GROUP BY " + grouping_id + minplay_query \
    #                             + ") q " \
    #                             + " WHERE season>=? AND season<=?" \
    #                             + " AND rownum <= 100 " \
    #                             + " AND " + sort[0] + " IS NOT NULL AND success IS NOT NULL" \
    #                             + " AND epa IS NOT NULL" + grouping_null \
    #                             + team_query + filter_query + indicators + win_query \
    #                             + play_type_query + qtr_query + week_query \
    #                             + "GROUP BY " + grouping_id + minplay_query \
    #                             + " ORDER BY total_" + sort[0] + " " + order + " LIMIT 1000",
    #                             season_start, season_end, season_start, season_end)
    #                                 
    #     if group != "name" and group != "kicker_player_name" and group != "punter_player_name" and group != "receiver" \
    #         and group != "passer" and group != "rusher" and group2 != "passer" and group2 != "rusher" \
    #         and group2 != "name" and group2 != "kicker_player_name" and group2 != "punter_player_name" \
    #         and group2 != "receiver_player_name" and group2 != "week" and group != "week":
    #         return render_template("teams.html", plays=plays, order=order, sort=sort, group=group,
    #                                 group2=group2, groupings=groupings, searchdesc=searchdesc)

    #     else:
    #         return render_template("players.html", plays=plays, order=order, sort=sort, group=group,
    #                                 group2=group2, groupings=groupings, searchdesc=searchdesc)
                                    
# Render about page
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

# Render glossary
@app.route("/glossary", methods=["GET"])
def glossary():
    return render_template("glossary.html")

@app.route("/viz", methods=["GET"])
def viz():
    return render_template("viz.html")

@app.route("/yellowpages", methods=["GET"])
def yellowpages():
    return render_template("yellowpages.html")

@app.route("/cards", methods=["GET"])
def cards():
    return render_template("cards.html")

# Handle error
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
