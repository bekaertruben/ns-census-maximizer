import nationstates as ns
import census_maximizer as cm

# CONFIG
USER     = "<Insert nation name here>"
PASSWORD = "<Insert password here>"
CONTACT  = "<Nationstates demands that the User Agent contain a method of contacting the Script's owner. An email address is fine>"

cm.init(CONTACT)
solver = cm.CensusMaximizer(USER, PASSWORD)
solver.adjust_weights(census = {
    -1 : ("Wealth Gaps", "Obesity", "Crime", "Charmlessness", "Primitiveness", "Averageness", "Death Rate", "Taxation"),
    0  : ("Rudeness", "Ignorance", "Corruption", "Government Size", "Political Apathy", "Authoritarianism"),
    2  : ("Economy", "Political Freedom"),
    3  : ("Civil Rights",),
}, policy={
    "No Internet": -10
})
solver.solve_issues()
