import requests
import lxml.html as lh
import re
from enum import Enum

base_url = "http://www.mwq.dds.nl/ns/results/{issue_id}.html"
name_to_id = {'Civil Rights': 0, 'Economy': 1, 'Political Freedom': 2, 'Population': 3, 'Wealth Gaps': 4, 'Death Rate': 5, 'Compassion': 6, 'Eco-Friendliness': 7, 'Social Conservatism': 8, 'Nudity': 9, 'Industry: Automobile Manufacturing': 10, 'Industry: Cheese Exports': 11, 'Industry: Basket Weaving': 12, 'Industry: Information Technology': 13, 'Industry: Pizza Delivery': 14, 'Industry: Trout Fishing': 15, 'Industry: Arms Manufacturing': 16, 'Sector: Agriculture': 17, 'Industry: Beverage Sales': 18, 'Industry: Timber Woodchipping': 19, 'Industry: Mining': 20, 'Industry: Insurance': 21, 'Industry: Furniture Restoration': 22, 'Industry: Retail': 23, 'Industry: Book Publishing': 24, 'Industry: Gambling': 25, 'Sector: Manufacturing': 26, 'Government Size': 27, 'Welfare': 28, 'Public Healthcare': 29, 'Law Enforcement': 30, 'Business Subsidization': 31, 'Religiousness': 32, 'Income Equality': 33, 'Niceness': 34, 'Rudeness': 35, 'Intelligence': 36, 'Ignorance': 37, 'Political Apathy': 38, 'Health': 39, 'Cheerfulness': 40, 'Weather': 41, 'Compliance': 42, 'Safety': 43, 'Lifespan': 44, 'Ideological Radicality': 45, 'Defense Forces': 46, 'Pacifism': 47, 'Economic Freedom': 48, 'Taxation': 49, 'Freedom From Taxation': 50, 'Corruption': 51, 'Integrity': 52, 'Authoritarianism': 53, 'Youth Rebelliousness': 54, 'Culture': 55, 'Employment': 56, 'Public Transport': 57, 'Tourism': 58, 'Weaponization': 59, 'Recreational Drug Use': 60, 'Obesity': 61, 'Secularism': 62, 'Environmental Beauty': 63, 'Charmlessness': 64, 'Influence': 65, 'World Assembly Endorsements': 66, 'Averageness': 67, 'Human Development Index': 68, 'Primitiveness': 69, 'Scientific Advancement': 70, 'Inclusiveness': 71, 'Average Income': 72, 'Average Income of Poor': 73, 'Average Income of Rich': 74, 'Public Education': 75, 'Economic Output': 76, 'Crime': 77, 'Foreign Aid': 78, 'Black Market': 79, 'Residency': 80, 'Survivors': 81, 'Zombies': 82, 'Dead': 83, 'Percentage Zombies': 84, 'Average Disposable Income': 85, 'International Artwork': 86}
easter_eggs = (77, 78, 80, 215, 223, 256, 266, 375, 408, 430, 471, 622, 1122)
unhandlable = (78, 407)

class PolicyChange(Enum):
    """ Represents the addition or removal of a policy in issue outcome """
    ADDS = 1
    SOMETIMES_ADDS = 0.5
    MAY_GO_EITHER_WAY = 0
    SOMETIMES_REMOVES = -0.5
    REMOVES = -1

class Outcome:
    """ Contains issue outcomes for a specific option """
    census_changes : dict # mean predicted changes for world census stats
    policy_changes : dict # policies (potentially) added or removed by selecting an option

    @classmethod
    def from_result(cls, result):
        """ Parses issue outcome from the corresponding string in trotterdam's 'Result' column """
        out = cls()
        out.census_changes = dict()
        out.policy_changes = dict()

        lines = [line.strip() for line in result.strip().split("\n")]
        for line in lines:
            if any(unwanted in line for unwanted in ("leads to", "unknown effect", "World Assembly", "field", "chain")):
                continue
            if "policy" in line:
                sometimes = "sometimes" in line
                adds      = "adds" in line
                removes   = "removes" in line
                if (not adds and not removes) or (adds and removes):
                    continue
                policy = line.split(":")[-1].strip()

                if policy in out.policy_changes:
                    out.policy_changes[policy] = PolicyChange.MAY_GO_EITHER_WAY
                else:
                    out.policy_changes[policy] = PolicyChange((0.5 if sometimes else 1) * (1 if adds else -1))
            else:
                match = re.search('[A-Z][\w :-]+', line)
                if match:
                    c_name = match.group(0).strip()
                    c_id = name_to_id[c_name]
                else:
                    continue
                
                if "(mean " in line:
                    mean = line.split("(")[-1].lstrip("mean ").rstrip(")")
                else:
                    mean = line.split(" ")[0]
                mean = float(mean)

                out.census_changes[c_id] = mean
        return out

class Issue:
    """ Contains all info (raw and parsed) obtained from an issue's page on Trotterdam"""
    issue_id : int
    name     : str  # the issue's title/name
    status   : int  # status code of http request
    table    : list # raw data in trotterdam table
    outcomes : dict # maps option id (nationstates id is one less than what trotterdam shows) to Outcome object

    def __init__(self, issue_id:int):
        self.issue_id = issue_id
        self.table = list()
        self.outcomes = dict()

        page = requests.get(base_url.format(issue_id = issue_id))
        self.status = page.status_code
        if (self.status) != 200:
            return
        doc = lh.fromstring(page.content)
        self.name  = doc.findtext('.//title')
        tr_elements = doc.xpath('//tr')
        self.table = [[t.text_content().strip() for t in row] for row in tr_elements]

        for row in self.table[1:]:
            options = [int(i) - 1 for i in row[0].split(".")[0].split("/")]
            outcome = Outcome.from_result(row[1])
            for o in options:
                self.outcomes[o] = outcome
