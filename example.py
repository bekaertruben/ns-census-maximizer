import census_maximizer as cm
import matplotlib.pyplot as plt # if not installed, run `pip install matplotlib`

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

# solve issues for the nation:
solver.solve_issues()

# plot overall weighted census score over time (password is not required for this)
plt.plot(*solver.census_score_history())
plt.show()
