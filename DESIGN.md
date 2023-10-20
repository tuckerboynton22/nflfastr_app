    The implementation of this web application is based primarily around the use of SQL queries to search a SQLite database that stores all of the
information for each of almost 32,000 NFL plays that have occurred in 2020. I chose a single-table SQLite database because nflfastR stores the information
for each play in one observation and provides an R function called "update_db()" that automatically places all 22 years of data into a single
SQLite table. However, because the IDE couldn't handle nearly 1.5 GB of data uploaded at once, I had to settle for just 2020 data, which I downloaded into
a CSV and then used to create a table in my manually-generated SQLite database (see notebook.md for R and SQL code).
    Once I had the data, my primary concern was generating a form that covered all of my proverbial bases in terms of things a person might want to query.
Beyond choosing which variables to include, the major challenge here was translating user entries into SQLite queries, which required a lot of back-and-forth
between user-friendly language and actual database variable names. To manage this conversation, I used a global dictionary for the filters, groupings, play types,
and quarters. Once I had created these dictionaries with variable names as keys and display names as values (e.g., epa vs. Expected Points Added), I could
seamlessly pass the values from  the Python script to the index template and move from key to value or vice versa depending on whether I was communicating with
the database or the user. This choice helped abstract my code within the index template––instead of writing down every value, I could simply loop through the
dictionaries of key/value pairs and display the key (user-friendly) while assigning the value (actual variable name) to the name of the input. In particular,
this design choice––storing user responses in the variable names that corresponded to the variable names in the SQLite database––saved me a lot of time and
code on the back end as I was formulating SQLite queries and creating the string that would display the user's selections on the results page.
    After collecting user input and storing those inputs in variable names matching the database, the next issue was extracting the specified values and
combining them into a single SQLite query. I used for loops to pull information out of checkboxes, which required looping through all boxes, and if statements
to check for values (or lack thereof) before assigning variables. This was another issue I ran into: figuring out how to handle blank input boxes, particularly
when it came to team names, quarters, play types, and season types––where there would have to be multiple inputs for a single variable. In order to
overcome this hurdle, I relied heavily on the INSTR SQL command, which allowed me to search strings for substrings. Thus, instead of looping through some
elaborate network of if statements, all I had to do was create one string with all of the possible variable values and check if the variable for the play in
question was a substring of that initial string. I also used the INSTR command for the team issue––when no team was specified for a particular split, I just
plugged in a string with all team abbreviations, of which every team abbreviation was necessarily a substring.
    In creating my SQLite queries, I handled each row of my form separately. For the longer, more cumbersome ones (see teamquery), I created an entire string
with the portion of the SQLite query and simply plugged that variable into the ultimate query. For the simpler ones (see season_start), I stored user
input in a single variable and plugged into the SQL query using placeholders. Ultimately, I had to decide which portions needed to be abstracted prior to the
final SQL query, and I believe I did so effectively. This design choice kept my SQL queries relatively clean and much easier to follow/debug than would have
been the case if I had just plugged in every user entry as a placeholder in one long SQL query.
    Once I had written my two queries (one for grouped queries and one for ungrouped), all that remained was presentation of the results. Because the query
results were stored in lists of dictionaries, all I had to do was pass the list of plays to the results template, loop through it, and extract the desired values.
In displaying output, however, there was a high degree of inconsistent and displeasing formatting, which became a task in and of itself. Chief among these
formatting issues was the problem of how to display a variable that was represented in seconds as minutes:seconds. Instead of altering its value in the
database (which would have been problematic for future queries), I used Jinja math operators (// and %) to obtain minute and second values within the loop
within the template, changing the display of the variable while maintaining its value in the database.
    At the top of the results page, I also wanted to display a string with the search query in user-friendly terms, which was more difficult than it appeared.
Because most of the user input was stored in strings for the SQL query, I had to create a new set of variables––with the suffix "results"––that stored user
input in a user-friendly manner. In all occasions where it was acceptable to display the variable name as it was defined for the SQL query, I did not create
a new variable, attempting to minimize extra time, code, and memory, but this was not always the case. For example, I did not want to display every team name
if a user did not specify a team, so in that case, I set teamresults="any team" instead of ="ARI ATL BAL BUF..." In building this second set of variables, I
gained great advantage from my dictionaries, which allowed me to easily toggle from variable name to user-friendly display name.
    Overall, the most difficult design aspect of this project was the logic of how everything fit together, particularly for the SQL queries. Giving the user
freedom to fill out some parts of the form but not others forced me to consider edge cases (e.g., what if a user specifies that the team is on offense but
does not specify a team?). Moreover, I wanted to limit the amount of code I used, so instead of making separate SQL queries, I had to figure out how to
incorporate empty strings or strings that would not alter the results if a query was left blank. All in all, I felt good about my design and feel I took
a big step forward from the beginning of the semester.
