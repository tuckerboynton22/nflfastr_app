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
    "game_id": "Game"
}

# Create global play types
play_types = {
    "pass": "Pass",
    "run": "Run",
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
    "5, 6": "OT"
}

# Configure application
app = Flask(__name__)

# Update database
db = SQL(os.getenv("postgres://pcmubvdkvxbofz:4fccabe77593c8a539011e5a57c7e52f4813beb0f17c7eb0a1d5a69ec241018d@ec2-52-5-176-53.compute-1.amazonaws.com:5432/dcjbh8a08udlft"))

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

        teams = db.execute("SELECT DISTINCT posteam FROM sample_plays WHERE posteam!='posteam' AND posteam!='NA' ORDER BY posteam")
        inequalities = ["=", ">", "<"]
        seasons = db.execute("SELECT DISTINCT season FROM sample_plays WHERE season!='season' ORDER BY season")

        return render_template("index.html", teams=teams, groupings=groupings, filters=filters,
                                inequalities=inequalities, seasons=seasons, play_types=play_types,
                                quarters=quarters, NUMFILTERS=5)

    # Provide search results
    else:
        """

        Note: all variables with 'results' suffix are created for front-facing search description to be displayed
        along with search results.

        """

        ALLTEAMS = "ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX \
                    KC LA LAC LV MIA MIN NE NO NYG NYJ PHI PIT SEA SF TB TEN WAS"

        # Set team
        if request.form.get("team") != "":
            team = request.form.get("team")
            teamresults = request.form.get("team")
        else:
            team = ALLTEAMS
            teamresults = "any team"

        # Set opponent
        if request.form.get("opp") != "":
            opp = request.form.get("opp")
            oppresults = request.form.get("opp")
        else:
            opp = ALLTEAMS
            oppresults = "any team"

        # Set offense/defense
        if request.form.get("offense") == "offense":
            posteam = team
            defteam = opp
            posteamresults = teamresults
            defteamresults = oppresults
        elif request.form.get("offense") == "defense":
            posteam = opp
            defteam = team
            posteamresults = oppresults
            defteamresults = teamresults
        else:
            posteam = ALLTEAMS
            defteam = ALLTEAMS
            posteamresults = "any team"
            defteamresults = "any team"

        # Set home/away
        if request.form.get("home") == "home":
            home_team = team
            away_team = opp
            home_teamresults = teamresults
            away_teamresults = oppresults
        elif request.form.get("home") == "away":
            home_team = opp
            away_team = team
            away_teamresults = oppresults
            home_teamresults = teamresults
        else:
            home_team = ALLTEAMS
            away_team = ALLTEAMS
            home_teamresults = "any team"
            away_teamresults = "any team"

        # Create team query
        if posteam == "LAC":
            teamquery =  " posteam='LAC' "
        else:
            teamquery = " INSTR('" + posteam + "', posteam)!=0 "
        if defteam == "LAC":
            teamquery = teamquery + "AND defteam='LAC' "
        else:
            teamquery = teamquery + "AND INSTR('" + defteam + "', defteam)!=0 "
        if team == "LAC":
            teamquery = teamquery + "AND (posteam='LAC' or defteam='LAC') "
        else:
            teamquery = teamquery + "AND (INSTR('" + team + "', posteam)!=0 OR INSTR('" + team + "', defteam)!=0) "
        if opp == "LAC":
            teamquery = teamquery + "AND (posteam='LAC' or defteam='LAC') "
        else:
            teamquery = teamquery + "AND (INSTR('" + opp + "', posteam)!=0 OR INSTR('" + opp + "', defteam)!=0) "
        if home_team == "LAC":
            teamquery = teamquery + "AND home_team='LAC' "
        else:
            teamquery = teamquery + "AND (INSTR('" + home_team + "', home_team)!=0) "
        if away_team == "LAC":
            teamquery = teamquery + "AND away_team='LAC' "
        else:
            teamquery = teamquery + "AND (INSTR('" + away_team + "', away_team)!=0) "



        # Identify start and end seasons
        season_start = str(request.form.get("start"))
        season_end = str(request.form.get("end"))

        # Create string with selected season type(s)
        if request.form.get("season_type") != "both":
            season_type = request.form.get("season_type")
        else:
            season_type = "REG or POST"

        # Create string with selected quarter(s)
        qtrs = ""
        for quarter in quarters:
            if str(request.form.get(quarter)) in quarters:
                if qtrs == "":
                    qtrs = str(request.form.get(quarter))
                else:
                    qtrs = qtrs + ", " + str(request.form.get(quarter))

        # Create string with selected play type(s)
        play_type = ""
        play_type2 = ""
        play_typeresults = ""
        for play in play_types:
            if str(request.form.get(play)) != 'run' and str(request.form.get(play)) != 'pass':
                play_type = play_type + str(request.form.get(play))
            if str(request.form.get(play)) in play_types.keys():
                if play_typeresults == "":
                    play_typeresults = " "  + play_types[str(request.form.get(play))]
                else:
                    play_typeresults = play_typeresults + ", " + play_types[str(request.form.get(play))]
            if str(request.form.get(play)) == "pass":
                play_type2 = play_type2 + " OR pass=1 "
            if str(request.form.get(play)) == "run":
                play_type2 = play_type2 + " OR rush=1 "
            if str(request.form.get(play)) == "two_point_attempt":
                play_type2 = play_type2 + " OR two_point_attempt=1 "
        play_type2 = play_type2 + ") "


        # Create filter query and dictionary for column titles on results page
        filterquery = ""
        filterdict = {}
        filterresults = ""
        NUMFILTERS = 5
        for i in range(NUMFILTERS):
            filt = "filter"+str(i)
            inequal = "inequality"+str(i)
            filtval = "filtervalue"+str(i)

            if request.form.get(filt) != "" and request.form.get(inequal) != "" and request.form.get(filtval) != "":
                filterquery = filterquery + "AND CAST(" + str(request.form.get(filt)) + " AS float)" + str(request.form.get(inequal)) \
                                + str(request.form.get(filtval)) + " AND " + str(request.form.get(filt)) + "!='NA' "
                filterdict[request.form.get(filt)] = filters[request.form.get(filt)]

                if filterresults == "":
                    filterresults = ", " + str(filters[request.form.get(filt)]) + str(request.form.get(inequal)) + str(request.form.get(filtval))
                else:
                    filterresults = filterresults + ", " + str(filters[request.form.get(filt)]) + str(request.form.get(inequal)) + str(request.form.get(filtval))

        # Set desired sorting mechanism
        sort = [request.form.get("sort"), filters[request.form.get("sort")]]
        order = request.form.get("order")

        # Create penalty query
        if request.form.get("penalty") != "either":
            penaltyindicator = "AND penalty=" + request.form.get("penalty") + " "
            if request.form.get("penalty") == "1":
                penaltyresults = "A penalty, "
            else:
                penaltyresults = "No penalties, "
        else:
            penaltyindicator = ""
            penaltyresults = "Either penalty or no penalty, "

        # Create turnover query
        if request.form.get("turnover") == "1":
            turnoverindicator = "AND (interception=1 OR fumble_lost=1) "
            turnoverresults = "a turnover, "
        elif request.form.get("turnover") == "0":
            turnoverindicator = "AND interception=0 AND fumble_lost=0 "
            turnoverresults = "no turnover, "
        else:
            turnoverindicator = ""
            turnoverresults = "either turnover or no turnover, "

        # Create score query
        if request.form.get("score") != "either":
            scoreindicator = "AND sp=" + request.form.get("score") + " "
            if request.form.get("score") == "1":
                scoreresults = "a score"
            else:
                scoreresults = "no score"
        else:
            scoreindicator = ""
            scoreresults = "either score or no score"

        # Combine penalty, turnover, and score queries for single indicator query
        indicators = penaltyindicator + turnoverindicator + scoreindicator
        indicatorresults = penaltyresults + turnoverresults + scoreresults

        # Set grouping
        grouping = request.form.get("grouping")

        if grouping == "name":
            grouping2 = ", id"
        elif grouping == "kicker_player_name":
            grouping2 = ", kicker_player_id"
        elif grouping == "punter_player_name":
            grouping2 = ", punter_player_id"
        elif grouping == "receiver_player_name":
            grouping2 = ", receiver_player_id"
        else:
            grouping2 = ""

        if grouping != "":
            groupingresults = "Grouped by " + groupings[grouping] + "."
        else:
            groupingresults = ""

        # Create minimum description
        minplays = int(request.form.get("minimum"))
        if minplays > 0 and grouping != "":
            minplayresults = " Min. " + str(minplays) + " plays."
        else:
            minplayresults = ""

        # Create description of search for results page
        searchdesc = str(season_start) + "-" + str(season_end) + ", " + season_type + " season, " + teamresults \
                    + " vs. " + oppresults + ", " + posteamresults + " on offense, " + defteamresults + " on defense, " \
                    + home_teamresults + " at home, " + away_teamresults + " on the road. Quarters: " + qtrs + ". Play types: " \
                    + play_typeresults + ". " + indicatorresults + filterresults + ". " + groupingresults + minplayresults


        # If no grouping, pass list of plays to plays.html
        if grouping == "":
            plays = db.execute("SELECT * FROM sample_plays WHERE " \
                                + teamquery + filterquery + indicators + \
                                " AND season>=? AND season<=? AND INSTR(?, season_type)!=0 \
                                AND INSTR(?, qtr)!=0 AND (INSTR(?, play_type)!=0" + play_type2 + \
                                "AND " + sort[0] + "!='NA' \
                                ORDER BY CAST(" + sort[0] + " AS float) " \
                                + order + " LIMIT 1000",
                                season_start, season_end, season_type, qtrs, play_type)

            return render_template("plays.html", plays=plays, filterdict=filterdict, order=order, sort=sort, searchdesc=searchdesc)


        elif grouping == "posteam" or grouping == "defteam" or grouping == "game_id":

            groupingquery = " AND epa!='NA' AND success!='NA' AND " + grouping + "!='NA'"

            plays = db.execute("SELECT " + grouping + grouping2 + ", COUNT(*) AS total, \
                                AVG(CAST(epa AS float)) AS epa, \
                                AVG(CAST(success AS float)) AS success, \
                                AVG(CAST(" + sort[0] + " AS float)) AS " + sort[0] +  \
                                " FROM sample_plays WHERE " \
                                + teamquery + groupingquery + filterquery + indicators + \
                                " AND season>=? AND season<=? AND INSTR(?, season_type)!=0 \
                                AND INSTR(?, qtr)!=0 AND (INSTR(?, play_type)!=0" + play_type2 + \
                                "AND " + sort[0] + "!='NA' GROUP BY " + grouping + grouping2 + \
                                " ORDER BY " + sort[0] + " " + order + " LIMIT 1000",
                                season_start, season_end, season_type, qtrs, play_type)

            return render_template("teams.html", plays=plays, filterdict=filterdict, order=order, sort=sort,
                                    grouping=grouping, groupings=groupings, searchdesc=searchdesc, minplays=minplays)

        else:

            groupingquery = " AND epa!='NA' AND success!='NA' AND " + grouping + "!='NA'"

            plays = db.execute("SELECT " + grouping + grouping2 + ", posteam, COUNT(*) AS total, \
                                AVG(CAST(epa AS float)) AS epa, \
                                AVG(CAST(success AS float)) AS success, \
                                AVG(CAST(" + sort[0] + " AS float)) AS " + sort[0] +  \
                                " FROM sample_plays WHERE " \
                                + teamquery + groupingquery + filterquery + indicators + \
                                " AND season>=? AND season<=? AND INSTR(?, season_type)!=0 \
                                AND INSTR(?, qtr)!=0 AND (INSTR(?, play_type)!=0" + play_type2 + \
                                "AND " + sort[0] + "!='NA' GROUP BY " + grouping + grouping2 + \
                                " ORDER BY " + sort[0] + " " + order + " LIMIT 1000",
                                season_start, season_end, season_type, qtrs, play_type)

            return render_template("players.html", plays=plays, filterdict=filterdict, order=order, sort=sort,
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