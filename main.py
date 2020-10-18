import nationstates as ns
import trotterdam


# CONFIG
USER = "<Insert nation name here>"
PASSWORD = "<Insert password here>"
CONTACT = "<Nationstates demands that the User Agent contain a method of contacting the Script's owner. An email address is fine>"

api = ns.Nationstates("Instance of https://github.com/bekaertruben/ns-census-maximizer [contact: {}]".format(CONTACT))
world = api.world()
nation = api.nation(USER, password=PASSWORD)


# weight by world mean
census_means = dict()
for scale in world.get_shards(ns.Shard("census", scale="all", mode="score"))['census']['scale']:
    census_means[int(scale.id)] = float(scale.score)
weights = {key: 1/val for key, val in census_means.items()}
# adjust for negative stats
for c_name in ("Wealth Gaps", "Obesity", "Crime", "Charmlessness", "Primitiveness", "Averageness", "Death Rate", "Taxation"):
    c_id = trotterdam.name_to_id[c_name]
    weights[c_id] = -weights[c_id]
# adjust for stats we don't care about
for c_name in ("Rudeness", "Ignorance", "Corruption", "Government Size"):
    c_id = trotterdam.name_to_id[c_name]
    weights[c_id] = 0
# adjust for front page stats
for c_name in ("Civil Rights", "Economy", "Political Freedom"):
    c_id = trotterdam.name_to_id[c_name]
    weights[c_id] = 2 * weights[c_id]


def calc_results_score(results):
    """must pass parsed results!!!"""
    score = 0
    for result in results:
        if result:
            score += result[1] * weights[result[0]]
    return score


def handle_issue(issue):
    if not issue.id in trotterdam.unhandlable:
        table = trotterdam.get_table(issue.id)
        if not table:
            print("Was unable to load Trotterdam page for Issue #{}".format(issue.id))
            return

        option_scores = dict()
        for option in issue.option:
            option_id = int(option.id)
            results = trotterdam.get_option_results(table, option_id)
            option_scores[option_id] = calc_results_score(results)
            pass
        
        best_option = max(option_scores, key=option_scores.get)
        if option_scores[best_option] <= 0:
            nation.command("issue", issue=issue.id, option=-1)
            print("Dismissed issue #{}. All options are bad.".format(issue.id))
        else:
            response = nation.command("issue", issue=issue.id, option=best_option)
            ranking_changes = response.issue.rankings.rank
            if isinstance(ranking_changes, list):
                results = [(int(rank.id), float(rank.change)) for rank in ranking_changes]
            else:
                results = [(int(ranking_changes.id), float(ranking_changes.change)),]
            score_inc = calc_results_score(results)
            print(
                "Picked option {} for issue #{}. This gave a score increase of {} (estimate was {})"
                    .format(best_option, issue.id, score_inc, option_scores[best_option])
                )


issues = nation.get_shards("issues").issues
if not issues:
    print("No issues")
elif isinstance(issues.issue, dict):
    handle_issue(issues.issue)
else: # isinstance(issues.issue, list):
    for issue in issues.issue:
        handle_issue(issue)
