import os
import datetime

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
    "down": "Down",
    "ydstogo": "Yards to Go",
    "yards_gained": "Yards Gained",
    "air_yards": "Air Yards",
    "yards_after_catch": "Yards After Catch (YAC)",
    "qb_epa": "QB EPA",
    "cp": "Completion Probability",
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
    "vegas_wp": "Win Probability",
    "comp_air_wpa": "Completed Air WPA",
    "comp_yac_wpa": "Completed YAC WPA",
    "total_line": "Vegas Total",
    "xyac_mean_yardage": "Mean Expected YAC",
    "xyac_epa": "Expected YAC EPA"
}

# Create global groupings
groupings = {
    "name": "Passer/Rusher",
    "receiver_player_name": "Receiver",
    "kicker_player_name": "Kicker",
    "punter_player_name": "Punter",
    "posteam": "Offense",
    "defteam": "Defense",
    "game_id": "Game",
    "season": "Season"
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
@app.route("/index", methods=["GET", "POST"])
def index():

    # Provide form for query
    if request.method == "GET":
        teams = db.execute("SELECT DISTINCT posteam FROM nflfastR_pbp WHERE posteam!='' ORDER BY posteam")
        inequalities = ["=", ">", "<"]
        seasons = db.execute("SELECT DISTINCT season FROM nflfastR_pbp ORDER BY season")

        return render_template("index.html", teams=teams, groupings=groupings, filters=filters,
                                inequalities=inequalities, seasons=seasons, play_types=play_types,
                                quarters=quarters, NUMFILTERS=5)

    # Provide search results
    else:
        """

        Note: all variables with 'results' suffix are created for front-facing search description to be displayed
        along with search results.

        """

        # Create team query
        team_query = ""
        team_results = ""
        opp_results = ""

        team = request.form.get("team")
        opp = request.form.get("opp")
        home = request.form.get("home")
        offense = request.form.get("offense")

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

        elif request.form.get("team") != "" and request.form.get("opp") != "":
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
        if request.form.get("offense") == "posteam":
            posteam_results = team_results
            defteam_results = opp_results
        elif request.form.get("offense") == "defteam":
            posteam_results = opp_results
            defteam_results = team_results
        else:
            posteam_results = "any team"
            defteam_results = "any team"

        # Set home/away results
        home_team_results = ""
        away_team_results = ""
        if request.form.get("home") == "home_team":
            home_team_results = team_results
            away_team_results = opp_results
        elif request.form.get("home") == "away_team":
            away_team_results = opp_results
            home_team_results = team_results
        else:
            home_team_results = "any team"
            away_team_results = "any team"
                
        # Identify start and end seasons
        season_start = int(request.form.get("start"))
        season_end = int(request.form.get("end"))

        # Create season type query
        if request.form.get("season_type") != "both":
            season_type_query = " AND season_type='" + request.form.get("season_type") + "' "
            season_type = request.form.get("season_type")
        else:
            season_type_query = ""
            season_type = "REG or POST"

        # Create quarter query
        qtr_query = ""
        for quarter in quarters:
            if str(request.form.get(quarter)) in quarters:
                if qtr_query == "":
                    if str(request.form.get(quarter)) == "5":
                        qtr_query = " AND(qtr=5 OR qtr=6"
                        qtrs = "OT"
                    else:
                        qtr_query = " AND(qtr=" + str(request.form.get(quarter))
                        qtrs = str(request.form.get(quarter))
                else:
                    if str(request.form.get(quarter)) == "5":
                        qtr_query = qtr_query + " OR qtr=5 OR qtr=6"
                        qtrs = qtrs + ", OT"
                    else:
                        qtr_query = qtr_query + " OR qtr=" + str(request.form.get(quarter))
                        qtrs = qtrs + ", " + str(request.form.get(quarter))
        if qtr_query != "":
            qtr_query = qtr_query + ") "

        # Create play type query
        play_type_query = ""
        play_type_results = ""
        for play in play_types:
            playtype = str(request.form.get(play))
            if playtype != "rush" and playtype != "pass" and playtype != "two_point_attempt" and playtype in play_types.keys():
                if play_type_query == "":
                    play_type_query = "AND(play_type='" + str(request.form.get(play)) + "' "
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

            if request.form.get(filt) != "" and request.form.get(inequal) != "" and request.form.get(filtval) != "":
                filter_query = filter_query + " AND " + str(request.form.get(filt)) + str(request.form.get(inequal)) \
                                + str(request.form.get(filtval)) + " AND " + str(request.form.get(filt)) + " IS NOT NULL "
                select = select + str(request.form.get(filt)) + ", "
                filter_dict[request.form.get(filt)] = filters[request.form.get(filt)]
                filter_results = filter_results + ", " + str(filters[request.form.get(filt)]) + str(request.form.get(inequal)) + str(request.form.get(filtval))

        # Set desired sorting mechanism
        sort = [request.form.get("sort"), filters[request.form.get("sort")]]
        select = select + request.form.get("sort") + ", "
        order = request.form.get("order")

        # Create penalty query
        if request.form.get("penalty") != "either":
            penaltyindicator = " AND penalty=" + request.form.get("penalty") + " "
            if request.form.get("penalty") == "1":
                penaltyresults = "A penalty, "
            else:
                penaltyresults = "No penalties, "
        else:
            penaltyindicator = ""
            penaltyresults = "Either penalty or no penalty, "

        # Create turnover query
        if request.form.get("turnover") == "1":
            turnoverindicator = " AND (interception=1 OR fumble_lost=1) "
            turnoverresults = "a turnover, "
        elif request.form.get("turnover") == "0":
            turnoverindicator = " AND interception=0 AND fumble_lost=0 "
            turnoverresults = "no turnover, "
        else:
            turnoverindicator = ""
            turnoverresults = "either turnover or no turnover, "

        # Create score query
        if request.form.get("score") != "either":
            scoreindicator = " AND sp=" + request.form.get("score") + " "
            if request.form.get("score") == "1":
                scoreresults = "a score"
            else:
                scoreresults = "no score"
        else:
            scoreindicator = ""
            scoreresults = "either score or no score"

        # Combine penalty, turnover, and score queries for single indicator query
        indicators = penaltyindicator + turnoverindicator + scoreindicator
        indicator_results = penaltyresults + turnoverresults + scoreresults

        # Set groupings
        grouping = ""
        group = request.form.get("grouping")
        group2 = request.form.get("grouping2")

        if group == "name":
            grouping = group + ", id"
        elif group == "kicker_player_name":
            grouping = group + ", kicker_player_id"
        elif group == "punter_player_name":
            grouping = group + ", punter_player_id"
        elif group == "receiver_player_name":
            grouping = group + ", receiver_player_id"
        else:
            grouping = group
        
        if group2 == "name":
            grouping = grouping + group2 + ", id"
        elif group2 == "kicker_player_name":
            grouping = grouping + group2 + ", kicker_player_id"
        elif group2 == "punter_player_name":
            grouping = grouping + group2 + ", punter_player_id"
        elif group2 == "receiver_player_name":
            grouping = grouping + group2 + ", receiver_player_id"
        else:
            grouping = grouping + group2

        if group != "":
            grouping_results = "Grouped by " + groupings[group]
            if group2 != "":
                grouping_results = grouping_results + ", " + groupings[group2]
        elif group2 != "":
            grouping_results = "Grouped by " + groupings[group2]
        else:    
            grouping_results = ""

        # Create minimum description
        if request.form.get("minimum") != "":
            minplays = int(request.form.get("minimum"))
        else:
            minplays = 0
    
        if minplays > 0 and grouping != "":
            minplay_results = " Min. " + str(minplays) + " plays."
        else:
            minplay_results = ""

        # Create description of search for results page
        searchdesc = str(season_start) + "-" + str(season_end) + ", " + season_type + " season, " + team_results \
                    + " vs. " + opp_results + ", " + posteam_results + " on offense, " + defteam_results + " on defense, " \
                    + home_team_results + " at home, " + away_team_results + " on the road. Quarters: " + qtrs + ". Play types: " \
                    + play_type_results + ". " + indicator_results + filter_results + ". " + grouping_results + minplay_results

        select = select + ' season_type, season, home_team, away_team, posteam, defteam, week, game_date, qtr, quarter_seconds_remaining, down, ydstogo, "desc" '

        # If no grouping, pass list of plays to plays.html
        if grouping == "":
    
            plays = db.execute("SELECT " + select + " FROM nflfastR_pbp WHERE \
                                season>=? AND season<=?"
                                + team_query + filter_query + indicators \
                                + play_type_query + qtr_query + season_type_query \
                                + " AND " + sort[0] + " IS NOT NULL ORDER BY " + sort[0] + " " \
                                + order + " LIMIT 1000",
                                season_start, season_end)

            return render_template("plays.html", plays=plays, filter_dict=filter_dict, order=order, sort=sort, searchdesc=searchdesc)


        else:
            plays = db.execute("SELECT " + grouping + ", COUNT(id) AS total, \
                                AVG(epa) AS epa, \
                                AVG(success) AS success, \
                                AVG(" + sort[0] + ") AS " + sort[0]  \
                                + ", STRING_AGG(DISTINCT posteam, ', ') as posteam"
                                + " FROM nflfastR_pbp WHERE season>=? AND season<=?" \
                                + " AND " + sort[0] + " IS NOT NULL AND success IS NOT NULL and epa IS NOT NULL" \
                                + " AND " + group + "!='None'  AND " + group + " IS NOT NULL " \
                                + " AND " + group2 + "!='None'  AND " + group2 + " IS NOT NULL " \
                                + team_query + filter_query + indicators \
                                + play_type_query + qtr_query + season_type_query \
                                + "GROUP BY " + grouping \
                                + " ORDER BY " + sort[0] + " " + order + " LIMIT 1000",
                                season_start, season_end)
            

            if grouping == "posteam" or grouping == "defteam" or grouping == "game_id" or grouping == "season":
                return render_template("teams.html", plays=plays, order=order, sort=sort,
                                        grouping=grouping, groupings=groupings, searchdesc=searchdesc, minplays=minplays)

            else:
                return render_template("players.html", plays=plays, order=order, sort=sort,
                                        grouping=grouping, groupings=groupings, searchdesc=searchdesc, minplays=minplays)

# Render about page
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

# Render glossary
@app.route("/glossary", methods=["GET"])
def glossary():
    return render_template("glossary.html")

# Handle error
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)