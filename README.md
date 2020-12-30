NOTE: My sample database (pbp_db.db) and zip file were both too large to submit to Gradescope, so I've uploaded both to Google Drive and shared with my project
advisor as well as the course heads.

Compiling & Running:

    To run the nflfastR Play Index, unzip the "project" folder and change your directory to the "nflfastr" folder therein. Once in the proper directory,
run the command-line argument "flask run"and your IDE should generate a URL where the Play Index is located. Opening the URL will bring you to the
homepage, where you will have access to all nflfastR Play Index features. Importantly, the Play Index will only run so long as you are running the code;
if you quit out of your IDE, the URL will no longer return the Play Index.

Navigating:

    Once you've arrived at the homepage, there are four main pages to which you can toggle by using the menu located at the top of the page: homepage, about,
index, and glossary. Clicking the words "nflfastR Play Index" and "Homepage" will both bring you to the homepage, where you will find the nflfastR logo and
a short description of the application's functionality. The "About" tab offers background on the goal and uses of the website (as well as a little bit about
me, and all tabs have a footer with hyperlinks to the CS50 homepage, my contact info, and the nflfastR website. If you're ever confused by technical jargon,
navigate to the glossary, which defines all technical terms in the Play Index, via the "Glossary" tab. Finally, the index, which you can access using either
the "Index" option in the menu at the top of the page or the "Go to Play Index" button on the homepage, is where you go to actually search for NFL plays based
on your desired specifications. Let's go there now.

Querying the Database:

    The index page is a dynamic form that you can use to query the nflfastR database. The first row of options has "Team" and "Opp" dropdown menus, which let
you designate which teams are involved in the play(s) that you are seeking. These dropdowns have team abbreviations for all NFL teams, and you can specify
one team, both teams, or neither. The next row includes two more dropdown menus, one for whether the specified team is playing at their home stadium or away,
and one for whether the specified team is on offense or defense. Once again, you can specify one of those options, both, or neither. For all plays, the
offensive team is the one with possession of the football. Note that if you do not specify a team or opponent in the first set of dropdown menus, the second
set of menus will have no impact on the search––you are essentially saying you don't care who is involved in the game, but one team is home and one team is
on offense, which applies to every play in the database. The third row provides dropdowns for a range of seasons and season type. Due to storage limitations,
only 2020 plays are available on the Play Index, but the site is updated through Week 12 of the regular season. The season type indicator allows you to
specify whether you would like to look at plays from the regular season, postseason, or both––it is set to regular season by default. Note that the postseason
has not yet happened for the 2020 season, so if you specify postseason, you will get no results.
    The fourth row allows you to determine during which quarter(s) of the game the play occurred, and it includes all quarters unless you specify otherwise.
Similarly, the fifth row allows you to specify which play type(s) you want to search for, where "No Play" is the case where a penalty occurs or a timeout
is called. Next, you can add any filters you want, from simple factors like down and distance (down, yards to go) to more complicated ones such as EPA or CPOE.
If you're confused about any of the technical terms in the dropdown menu, simply tab over to the "Glossary," where you can find a definition for the more
complicated terms. EPA is one of the more commonly-used phrases and denotes the value that a particular play has for the team possessing the football.
In the penultimate row, there are three indicator variables for common occurrences during the game: penalty, turnover, or score. If you want to look at plays
strictly with or without one of these happenings, you can specify in the corresponding dropdown menu.
    Finally, you can choose how you want your results to be sorted and grouped. The default option is ungrouped (i.e., display all individual plays) and sorted
by descending Expected Points Added (i.e., most impactful offensive plays first). The "Sort by:" menu allows you to change the order in which the data are
presented by altering "descending" to "ascending" and changing the variable used to sort the data (i.e., the sort value). This sort variable has the same
options as the filters. The "Group by:" dropdown menu is where you can indicate that you'd like to see results grouped by offensive teams, defensive teams,
passers, rushers, and receivers for plays that match a particular set of criteria. Choosing one of these options will give you the total number of plays,
average EPA, average success rate, and average sort value for each rusher/receiver/passer/team on plays matching your specified criteria. The default settings
are such that if you press submit without entering any filters or changing any of the checkboxes/dropdown menus, you will search for every play in 2020,
ungrouped and in order of descending EPA. Thus, you will get the 1,000 highest EPA plays of 2020, listed in descending order.

Viewing Results:

    Once you hit submit, you will get one of two things depending on whether you decide to group your results. If you choose not to group your results, you
will get a table with up to 1,000 plays matching your criteria. Here, you can find the sort value (selected by you), offensive team, defensive team, week of
season, game date, quarter of game, time remaining, down, distance, play description, and any filter values (also selected by you) for each play. Additionally,
in the rightmost column is a hyperlink to Ben Baldwin's rbsdm.com box scores if you're interested in exploring the game further. If you choose to group your
results, you'll get the average sort value (selected by you), the grouping (also selected by you), the number of plays, the average EPA, and average success
rate of those plays. An important difference between the grouped and non-grouped results is that the former displays average values for that group,
whereas the latter only has one observation.
    In either case, although your results will initially be ordered by the sort value you selected in the query, you can sort your results by any value in
the table by clicking on the row header (click twice for descending). You can also search for keywords using the search box and adjust the number of rows
per page. Additionally, if you forget what you searched for, don't fret––your query is written at the top of the page, and if you want to alter it and search
again, simply hit the "back" button on your browser to return to the form you just filled out. If you want to start a new search instead, press the "Index"
button at the top of the page, and you'll be returned to a clean index form. Once again, if you have any questions about technical terminology, toggle over
to the "Glossary" page, where you'll find a list of analytical phrases used on the website.

URL: https://www.youtube.com/watch?v=fs0r1SaTN1Q&feature=youtu.be