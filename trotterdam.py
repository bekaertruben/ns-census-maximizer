import requests
import lxml.html as lh
import re

base_url = "http://www.mwq.dds.nl/ns/results/{issue_id}.html"
name_to_id = {'Civil Rights': 0, 'Economy': 1, 'Political Freedom': 2, 'Population': 3, 'Wealth Gaps': 4, 'Death Rate': 5, 'Compassion': 6, 'Eco-Friendliness': 7, 'Social Conservatism': 8, 'Nudity': 9, 'Industry: Automobile Manufacturing': 10, 'Industry: Cheese Exports': 11, 'Industry: Basket Weaving': 12, 'Industry: Information Technology': 13, 'Industry: Pizza Delivery': 14, 'Industry: Trout Fishing': 15, 'Industry: Arms Manufacturing': 16, 'Sector: Agriculture': 17, 'Industry: Beverage Sales': 18, 'Industry: Timber Woodchipping': 19, 'Industry: Mining': 20, 'Industry: Insurance': 21, 'Industry: Furniture Restoration': 22, 'Industry: Retail': 23, 'Industry: Book Publishing': 24, 'Industry: Gambling': 25, 'Sector: Manufacturing': 26, 'Government Size': 27, 'Welfare': 28, 'Public Healthcare': 29, 'Law Enforcement': 30, 'Business Subsidization': 31, 'Religiousness': 32, 'Income Equality': 33, 'Niceness': 34, 'Rudeness': 35, 'Intelligence': 36, 'Ignorance': 37, 'Political Apathy': 38, 'Health': 39, 'Cheerfulness': 40, 'Weather': 41, 'Compliance': 42, 'Safety': 43, 'Lifespan': 44, 'Ideological Radicality': 45, 'Defense Forces': 46, 'Pacifism': 47, 'Economic Freedom': 48, 'Taxation': 49, 'Freedom From Taxation': 50, 'Corruption': 51, 'Integrity': 52, 'Authoritarianism': 53, 'Youth Rebelliousness': 54, 'Culture': 55, 'Employment': 56, 'Public Transport': 57, 'Tourism': 58, 'Weaponization': 59, 'Recreational Drug Use': 60, 'Obesity': 61, 'Secularism': 62, 'Environmental Beauty': 63, 'Charmlessness': 64, 'Influence': 65, 'World Assembly Endorsements': 66, 'Averageness': 67, 'Human Development Index': 68, 'Primitiveness': 69, 'Scientific Advancement': 70, 'Inclusiveness': 71, 'Average Income': 72, 'Average Income of Poor': 73, 'Average Income of Rich': 74, 'Public Education': 75, 'Economic Output': 76, 'Crime': 77, 'Foreign Aid': 78, 'Black Market': 79, 'Residency': 80, 'Survivors': 81, 'Zombies': 82, 'Dead': 83, 'Percentage Zombies': 84, 'Average Disposable Income': 85, 'International Artwork': 86}
easter_eggs = (77, 78, 80, 215, 223, 256, 266, 375, 408, 430, 471, 622, 1122)
unhandlable = (78, 407)


def get_table(issue_id):
    # https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059
    page = requests.get(base_url.format(issue_id = issue_id))
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')

    return [[t.text_content().strip() for t in row] for row in tr_elements]


def parse_result(result):
    for unwanted in ("policy", "leads to", "unknown effect", "World Assembly", "field", "chain"):
        if unwanted in result:
            return None

    # determine census scale
    match = re.search('([A-Z])[\w : -]+', result)
    if match:
        c_name = match.group(0).strip()
        c_id = name_to_id[c_name]
    else:
        return None
    
    # calculate mean
    if "(mean " in result:
        mean = result.split("(")[-1].lstrip("mean ").rstrip(")")
    else:
        mean = result.split(" ")[0]
    mean = float(mean)

    return c_id, mean


def search_option(table, option_id):
    """returns the row number corresponding to an option"""
    option = str(option_id + 1)
    for row_i in range(1, len(table)):
        row = table[row_i]
        outcome_str = row[0].strip()
        i = 0
        while outcome_str[i+1] == "/" and not option == outcome_str[i]:
            i+=2
        if option == outcome_str[i]:
            return row_i


def get_option_results(table, option_id):
    row_i = search_option(table, option_id)
    return [
        parse_result(result.strip())
        for result in table[row_i][1].strip().split("\n")
    ]
