#!/bin/python
# This draws a graph of weighted census score history for the requested nations
import census_maximizer as cm
import matplotlib.pyplot as plt # if not installed, run `pip install matplotlib`
import matplotlib.dates as md
from datetime import datetime

cm.init("<Input contact details here before running!!!>")

nations = [s.strip() for s in input("Nation(s) to inspect (comma-separated): ").split(",")]

plt.figure(figsize=(12, 6))
plt.title("Census score over time", fontsize=24)
# plt.xlabel("Time", fontsize=18)
plt.ylabel("Weigted census score", fontsize=18)
ax=plt.gca()
xfmt = md.DateFormatter("%Y-%m-%d")
ax.xaxis.set_major_formatter(xfmt)
plt.xticks(rotation = 30)
for nation in nations:
    print("plotting ", nation)
    solver = cm.CensusMaximizer(nation)
    x, y = solver.census_score_history()
    plt.plot([datetime.utcfromtimestamp(ts) for ts in x], y, label = nation)
plt.legend()
plt.show()
