# Why half of Greece cannot afford a week away

Data analysis of holiday-taking by residents of Greece, using Eurostat and
ELSTAT sources, 2009 to 2025.

**Στα ελληνικά:** [README-GR.md](README-GR.md)

**Interactive charts:** [Tableau Public](https://public.tableau.com/app/profile/konstantinos.kolovos5903/viz/WhyhalfofGreekscannotaffordaweekaway)

---

## The question

**46,6%** of residents of Greece say they cannot afford one week of
holiday a year away from home. The EU average is **27,5%**.

The Eurostat definition counts a second home, a stay with friends or
relatives, and subsidised accommodation as ways of affording it. Time and
health do not count. So a "no" means two things at once: no money to pay,
and no free roof anywhere.

Both show up in the data. How many people did not in fact go, and for
what reason in each case, is published nowhere. So this work looks first
at the typical household and then at the people who did go.

## What the data shows

**Money.** Real median household income is **−22,3%** since 2009, the
worst performance in the EU. Together with France, Greece is the only
country that has not returned to its 2009 level.

The six countries that went through the debt crisis started together and
ended up in very different places. Real median income, 2009 to 2024:

| | this project | KEFiM |
|---|---|---|
| Ireland | +40,3% | +21% |
| Portugal | +25,5% | +16% |
| Cyprus | +8,0% | +14% |
| Spain | +4,2% | +6,5% |
| Italy | +2,9% | −0,7% |
| **Greece** | **−22,3%** | **−15%** |

Two different measures, same ranking. This project uses the income of the
household **in the middle** of the distribution, after taxes and
transfers, adjusted for household size and for prices. KEFiM uses real
household income from national accounts. The first was chosen because it
comes from the same survey as the 46,6%, so both numbers describe the
same people. Details in [METHODOLOGIA.md](METHODOLOGIA.md) (Greek).
Greece comes last on both.

**Housing.** **52,4%** of domestic nights are spent in an owned dwelling,
the highest share in the EU against an average of **17,5%**. Abroad, free
accommodation still accounts for 52%. Only the owner of the house
changes.

**15% of trips produce half the country's nights.** Trips of two weeks or
more are **15,3%** of trips, **50,7%** of nights and only **21,2%** of
spending. A night on those trips costs **21 euro**, against **107** on a
short trip.

**Paid accommodation is moving to the mainland.** In 2025 the islands
grew **+1,1%** and mainland Greece **+6,0%**. All thirteen regions gained
foreign visitors. Four lost residents of Greece, and they are the four
with the highest foreign demand: Crete, the Ionian Islands, Attica, the
South Aegean.

**Trips abroad are growing faster.** In five of the six years from 2020
to 2025. In 2025, **+18,8%** against **+12,8%** for domestic trips.

**Trips are getting shorter.** From 2024 to 2025 the 1 to 3 night band
went from **23,9%** to **26,7%** of trips, while the 15 nights and over
band fell from **17,2%** to **15,3%**. One year, so a direction rather
than a conclusion.

---

## Sources

| source | what it provides |
|---|---|
| Eurostat `ilc_mdes02` | inability to afford one week of holiday |
| Eurostat `ilc_di03` | median equivalised disposable income |
| Eurostat `prc_hicp_aind` | harmonised index of consumer prices |
| Eurostat `tour_dem_*` | trips, nights, accommodation, expenditure |
| ELSTAT **STO15** | holiday survey, 2024 and 2025 press releases |
| ELSTAT **STO12** | accommodation occupancy by region, 2025 |
| ELSTAT **STO18** | experimental statistics on short-term rentals |

Eurostat data is downloaded from the API. The 2025 ELSTAT tables are not
published as xlsx, only inside the press releases, so they are typed into
the code. **Every script contains checks verifying that the totals match
the published figures exactly.** If a number was mistyped, the check
fails.

---

## What this work does not claim

**It does not answer whether prices are to blame.** The hypothesis was
tested against average spending per night from INSETE and no clear
pattern emerged, but that measure covers **accommodation only**. The cost
of a holiday also includes food, sunbeds, transport and shopping. Prices
by region for the domestic tourist are published nowhere, so the question
stays open rather than answered.

**It does not claim Greeks abandoned the islands.** This was checked
against mode of transport: trips requiring a ferry or a plane held a
stable share, 25,1% to 25,2%.

**That long trips happen in an owned or a friend's house is a very strong
indication, not a cross-tabulation.** 21 euro a night does not pay for
accommodation anywhere in Greece, and 52,4% of domestic nights are spent
in an owned dwelling. The two point the same way from two directions. But
ELSTAT does not cross duration bands with accommodation type, so it
remains an indication.

**It does not claim the 46,6% means no holiday at all.** The indicator is
about **one week away from home**. Residents of Greece made 7,9 million
trips in 2025.

**Nothing is subtracted from the 46,6%.** It is a statement of capacity,
not a measurement of behaviour, and nowhere is it published how many
people actually left for a week. The finest duration band at the level of
**individuals** stops at four nights.

**The 2025 regional series compare a single year.** One year is not a
trend.

Full record in [METHODOLOGIA.md](METHODOLOGIA.md), including the
hypotheses that were **tested and rejected**.

---

## Structure

```
kwdikas/
  01_eisodima.py       income and deprivation, Eurostat
  02_katalymata.py     where people stay, Eurostat
  03_taxidia.py        duration and spending, ELSTAT STO15
  04_perifereies.py    regions 2025, ELSTAT STO12 and STO18
dedomena/              the CSV files produced
pdf/                   the ELSTAT press releases
METHODOLOGIA.md        decisions, traps, what was rejected
```

Code comments and the methodology are in Greek, matching the sources.

## Running it

```bash
pip install -r requirements.txt
cd kwdikas
python 01_eisodima.py
python 02_katalymata.py
python 03_taxidia.py
python 04_perifereies.py
```

The first two need a connection, they download from the Eurostat API. The
last two run offline.

Each script prints its checks. **If a check does not return the expected
value, the data must not go into a chart.**

---

Konstantinos Kolovos
