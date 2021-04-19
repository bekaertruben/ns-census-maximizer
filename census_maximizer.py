import nationstates as ns
import trotterdam
import copy
import numpy as np

api = None
world = None

census_weights_by_world_mean = None

def init(contact):
    """ Sets up connection to the nationstates api """
    global api, world, census_weights_by_world_mean
    api = ns.Nationstates("Instance of https://github.com/bekaertruben/ns-census-maximizer [contact: {}]".format(contact))
    world = api.world()
    census_means = dict()
    for scale in world.get_shards(ns.Shard("census", scale="all", mode="score")).census.scale:
        census_means[int(scale.id)] = float(scale.score)
    census_weights_by_world_mean = {key: 1/val for key, val in census_means.items()}

class CensusMaximizer:
    """ Solves issues by calculation maximum world census score increases """
    user : str
    password : str
    policies : list
    census_weights: dict
    policy_weights: dict

    def __init__(self, user, password=None):
        self.user = user
        self.password = password
        self.nation = api.nation(user, password=password)

        self.census_weights = census_weights_by_world_mean
        self.policy_weights = dict()
        self.load_policies()

    def load_policies(self):
        """ Retrieves the nation's policies from nationstates api """
        policies = self.nation.get_shards("policies").policies.policy
        self.policies = [p.name for p in (policies if isinstance(policies, list) else [policies,])]

    def adjust_weights(self, census:dict=dict(), policy:dict=dict()):
        """ 1) Sets the solver's census weights according to world means, adjusted by custom values in the following format:
            census = {0 : ("Nudity",), -1 : ("Death Rate", "Taxation"), 3: ("Civil Rights",)}
            This makes the solver ignore Nudity, minimise Death Rate and Taxation, and weigh Civil Rights more in its calclation of scores
            2) Sets the policy weights. For example:
            policy = {"No Internet": -10}
            would lower an outcome's score by 10 if it adds this policy"""
        self.census_weights = copy.copy(census_weights_by_world_mean)
        for adjustment in census:
            for c_name in census[adjustment]:
                c_id = trotterdam.name_to_id[c_name]
                self.census_weights[c_id] = adjustment * census_weights_by_world_mean[c_id]
        self.policy_weights = policy
    
    def calc_outcome_score(self, outcome:trotterdam.Outcome):
        """ Calculates an outcome score according to census_weights and policy_weights """
        score = 0
        for c_id, change in outcome.census_changes.items():
            score += change * self.census_weights[c_id]
        for policy, change in outcome.policy_changes.items():
            if policy not in self.policy_weights:
                continue
            if policy in self.policies and change.value > 0:
                continue # can't add a policy if you already have it
            if policy not in self.policies and change.value < 0:
                continue # can't remove a policy if you don't have it
            score += self.policy_weights[policy] * change.value
        return score
    
    def solve_issue(self, issue, log = True):
        """ Solves an issue and returns option picked, outcome """
        if issue.id in trotterdam.unhandlable:
            return -1, None
        trotterdam_issue = trotterdam.Issue(issue.id)
        if not trotterdam_issue.table:
            if log:
                print("Was unable to load Trotterdam page for Issue #{}".format(issue.id))
            return -1, None

        option_scores = dict()
        for option in issue.option:
            option_id = int(option.id)
            option_scores[option_id] = self.calc_outcome_score(trotterdam_issue.outcomes[option_id])
        best_option = max(option_scores, key=option_scores.get)

        if option_scores[best_option] <= 0:
            self.nation.command("issue", issue=issue.id, option=-1)
            if log:
                print("Dismissed issue #{}. All options are bad.".format(issue.id))
            return -1, None
        else:
            response = self.nation.command("issue", issue=issue.id, option=best_option).issue
            rankings = response.rankings.rank if "rankings" in response else []
            new_policies = response.new_policies.policy if "new_policies" in response else []
            removed_policies = response.removed_policies.policy if "removed_policies" in response else []

            outcome = trotterdam.Outcome()
            outcome.census_changes = {
                int(rank.id): float(rank.change)
                for rank in (rankings if isinstance(rankings, list) else [rankings,])
            }
            outcome.policy_changes = dict()
            for p in (new_policies if isinstance(new_policies, list) else [new_policies,]):
                outcome.policy_changes[p.name] = trotterdam.PolicyChange.ADDS
            for p in (removed_policies if isinstance(removed_policies, list) else [removed_policies,]):
                outcome.policy_changes[p.name] = trotterdam.PolicyChange.REMOVES

            if log:
                print(
                    "Picked option {} for issue #{}. This gave a score increase of {} (prediction was {})"
                        .format(best_option, issue.id, self.calc_outcome_score(outcome), option_scores[best_option])
                )
            for p in (new_policies if isinstance(new_policies, list) else [new_policies,]):
                self.policies.append(p.name)
                if log:
                    print("-> This added the policy '{}'".format(p.name))
            for p in (removed_policies if isinstance(removed_policies, list) else [removed_policies,]):
                self.policies.remove(p.name)
                if log:
                    print("-> This removed the policy '{}'".format(p.name))
            
            return best_option, outcome
    
    def solve_issues(self, log = True):
        """ Solves all issues """
        if not self.password:
            raise ValueError("Can't solve issues if the CensusMaximizer isn't initialised with a password")

        if log:
            print("Solving issues for {}".format(self.user))

        issues = self.nation.get_shards("issues").issues
        if not issues:
            if log:
                print("No issues")
        else:
            issues = issues.issue
            if not isinstance(issues, list): # only one issue
                issues = [issues,]
            for issue in issues:
                option_picked, outcome = self.solve_issue(issue, log = log)
            print("{} is now gloriously issue-free".format(self.user))
    
    def census_score_history(self, scales=None):
        """ Returns the history of weighted census scores for the nation. Return format is (timestamp, scores)
            where timestamp is a list of unix timestamp and scores a list of scores.
            these can be plotted using a module like matplotlib to view trends in the nation's score"""
        if not scales:
            scales = list(range(65)) + list(range(67, 80)) # Z-day and WA-stats as well as Residency removed as these make the data really unclear
        response = self.nation.get_shards(ns.Shard("census", scale=scales, mode="history"))
        min_ts = 1e100
        max_ts = 0
        for scale in response.census.scale:
            for point in scale.point:
                ts = int(point.timestamp)
                if ts < min_ts:
                    min_ts = ts
                if ts > max_ts:
                    max_ts = ts
        if max_ts == 0:
            return # something went wrong
        x = np.arange(min_ts, max_ts, 24*60**2)
        y = np.array([0. for o in x])
        for scale in response.census.scale:
            c_id = int(scale.id)
            # we must use interpolation as the timestamps aren't always the same for all scales
            interp_x = np.array([int(p.timestamp) for p in scale.point])
            interp_y = self.census_weights[c_id] * np.array([float(p.score) for p in scale.point])
            y += np.interp(x, interp_x, interp_y)
        return x, y
