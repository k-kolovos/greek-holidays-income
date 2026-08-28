# Ερώτημα 1: εισόδημα και αδυναμία για διακοπές, Ελλάδα και ΕΕ
#
# Πηγές: Eurostat ilc_mdes02, ilc_di03, prc_hicp_aind
# Παράγει: q1_seira.csv, q1_eisodima_metavoli.csv, q1_vaseis.csv,
#          q1_ellada_seira.csv
#
# Τρεις παγίδες, αναλυτικά στο METHODOLOGIA.md:
#   1. Η EU-SILC του έτους T μετράει εισόδημα του T-1
#   2. Για χώρες εκτός ευρωζώνης χρειάζεται εθνικό νόμισμα
#   3. Η σημαία "b" σημαίνει διακοπή σειράς

import os
import pandas as pd

EXODOS = "../dedomena"
os.makedirs(EXODOS, exist_ok=True)

VASI = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"

# ------------------------------------------------------------
# 1. Κατέβασμα
# ------------------------------------------------------------

diakopes = pd.read_csv(VASI + "ILC_MDES02/?format=SDMX-CSV")
eisodima = pd.read_csv(VASI + "ILC_DI03/?format=SDMX-CSV")

# Το φίλτρο A.INX_A_AVG.CP00. είναι απαραίτητο, χωρίς αυτό ο πίνακας
# των τιμών είναι τεράστιος και το αίτημα λήγει.
times = pd.read_csv(VASI + "PRC_HICP_AIND/A.INX_A_AVG.CP00.?format=SDMX-CSV")

print("κατέβηκαν", len(diakopes), len(eisodima), len(times), "γραμμές")

# ------------------------------------------------------------
# 2. Καθάρισμα
# ------------------------------------------------------------

# Μόνο τα 27 κράτη μέλη και ο μέσος όρος τους. Οι υποψήφιες και οι χώρες
# του ΕΟΧ έχουν άλλο θεσμικό πλαίσιο και δεν συγκρίνονται.
kratimeli = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR",
             "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT",
             "RO", "SI", "SK", "FI", "SE"]
ee = kratimeli + ["EU27_2020"]

diakopes = diakopes[diakopes["geo"].isin(ee)]
eisodima = eisodima[eisodima["geo"].isin(ee)]

diakopes = diakopes[(diakopes["hhcomp"] == "TOTAL") & (diakopes["unit"] == "PC")]
diakopes = diakopes[["geo", "TIME_PERIOD", "rskpovth", "OBS_VALUE", "OBS_FLAG"]]
diakopes.columns = ["geo", "etos_erevnas", "omada_kod", "pososto", "simaia_ad"]

eisodima = eisodima[(eisodima["age"] == "TOTAL") & (eisodima["sex"] == "T")]
eisodima = eisodima[eisodima["statinfo"] == "MED_EI"]

# Παγίδα 2. Γράφουμε ποιες χώρες έχουν ευρώ, όχι ποιες δεν έχουν, ώστε
# κάθε νέα χώρα να παίρνει αυτόματα εθνικό νόμισμα. Λιθουανία και
# Κροατία μένουν σε ευρώ γιατί η σειρά τους σε εθνικό νόμισμα σπάει
# στην ένταξη.
evrozoni = ["AT", "BE", "CY", "DE", "EE", "ES", "FI", "FR", "EL", "HR",
            "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PT", "SI", "SK",
            "EU27_2020"]

se_eur = eisodima[(eisodima["unit"] == "EUR") & (eisodima["geo"].isin(evrozoni))]
se_nac = eisodima[(eisodima["unit"] == "NAC") & (~eisodima["geo"].isin(evrozoni))]
eisodima = pd.concat([se_eur, se_nac])

eisodima = eisodima[["geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG"]]
eisodima.columns = ["geo", "etos_erevnas", "onomastiko", "simaia_eis"]

# Παγίδα 1. Από εδώ και κάτω το "etos" είναι εισοδηματικό έτος.
# Η αδυναμία για διακοπές μένει στο έτος έρευνας, γιατί η ερώτηση
# αφορά τη στιγμή της συνέντευξης.
eisodima["etos"] = eisodima["etos_erevnas"] - 1

times = times[["geo", "TIME_PERIOD", "OBS_VALUE"]]
times.columns = ["geo", "etos", "deiktis"]

# ------------------------------------------------------------
# 3. Αποπληθωρισμός σε τιμές 2024
# ------------------------------------------------------------

olo = pd.merge(eisodima, times, on=["geo", "etos"])
olo = pd.merge(olo, diakopes[diakopes["omada_kod"] == "TOTAL"],
               on=["geo", "etos_erevnas"])

vasi_2024 = times[times["etos"] == 2024][["geo", "deiktis"]]
vasi_2024.columns = ["geo", "deiktis_2024"]
olo = pd.merge(olo, vasi_2024, on="geo")

olo["pragmatiko"] = olo["onomastiko"] / olo["deiktis"] * olo["deiktis_2024"]

# ------------------------------------------------------------
# 4. Ονόματα και ομάδες
# ------------------------------------------------------------

xores = {
    "EL": "Ελλάδα", "ES": "Ισπανία", "PT": "Πορτογαλία", "IT": "Ιταλία",
    "HR": "Κροατία", "CY": "Κύπρος", "BG": "Βουλγαρία", "RO": "Ρουμανία",
    "DE": "Γερμανία", "FR": "Γαλλία", "NL": "Ολλανδία", "BE": "Βέλγιο",
    "AT": "Αυστρία", "PL": "Πολωνία", "CZ": "Τσεχία", "SK": "Σλοβακία",
    "SI": "Σλοβενία", "HU": "Ουγγαρία", "SE": "Σουηδία", "DK": "Δανία",
    "FI": "Φινλανδία", "IE": "Ιρλανδία", "LU": "Λουξεμβούργο", "MT": "Μάλτα",
    "EE": "Εσθονία", "LV": "Λετονία", "LT": "Λιθουανία",
    "EU27_2020": "Ευρωπαϊκή Ένωση (27)",
}

# Οι έξι χώρες που πέρασαν κρίση χρέους. Συμπληρώνουν τη σύγκριση με
# όλη την ΕΕ, δεν την αντικαθιστούν.
krisi = ["EL", "ES", "IT", "IE", "CY", "PT"]


def simane(df):
    """Ίδιες στήλες σε κάθε αρχείο, ώστε τα φίλτρα στο Tableau να είναι
    παντού τα ίδια."""
    df = df.copy()
    df["xora"] = df["geo"].map(xores).fillna(df["geo"])
    df["kratos_melos"] = df["geo"].isin(kratimeli)
    df["xora_krisis"] = df["geo"].isin(krisi)
    df["einai_ellada"] = df["geo"] == "EL"
    df["einai_ee"] = df["geo"] == "EU27_2020"
    df["omada_xrwmatos"] = "Υπόλοιπες"
    df.loc[df["einai_ee"], "omada_xrwmatos"] = "ΕΕ27"
    df.loc[df["einai_ellada"], "omada_xrwmatos"] = "Ελλάδα"
    return df


# ------------------------------------------------------------
# 5. Αρχείο 1, η χρονοσειρά της αδυναμίας
# ------------------------------------------------------------

seira = simane(diakopes[diakopes["etos_erevnas"] >= 2003].copy())

# Το Tableau δείχνει το έτος ως "2.017" αν είναι ακέραιος. Στέλνουμε
# ημερομηνία και πετάμε τον αριθμό.
seira["imerominia"] = pd.to_datetime(seira["etos_erevnas"], format="%Y")
seira = seira.drop(columns=["etos_erevnas", "omada_kod"])
seira.to_csv(f"{EXODOS}/q1_seira.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 6. Αρχείο 2, εισόδημα και αδυναμία, 2009 προς 2024
# ------------------------------------------------------------

arxi = olo[olo["etos"] == 2009][["geo", "pragmatiko", "pososto"]]
arxi.columns = ["geo", "eisodima_2009", "adynamia_2009"]

telos = olo[olo["etos"] == 2024][["geo", "pragmatiko", "pososto"]]
telos.columns = ["geo", "eisodima_2024", "adynamia_2024"]

pinakas = pd.merge(arxi, telos, on="geo")
pinakas["eisodima_2009"] = pinakas["eisodima_2009"].round(0)
pinakas["eisodima_2024"] = pinakas["eisodima_2024"].round(0)
pinakas["metavoli_eisodimatos"] = (
    100 * (pinakas["eisodima_2024"] / pinakas["eisodima_2009"] - 1)).round(1)
pinakas["metavoli_adynamias"] = (
    pinakas["adynamia_2024"] - pinakas["adynamia_2009"]).round(1)
pinakas = simane(pinakas)

# Παγίδα 3. Σημειώνουμε αν υπάρχει διακοπή σειράς οπουδήποτε μέσα στο
# διάστημα, ώστε να ξέρουμε ποιες συγκρίσεις είναι ασφαλείς.
parathiro = olo[(olo["etos"] >= 2009) & (olo["etos"] <= 2024)]
simaies = []
for g in pinakas["geo"]:
    x = parathiro[parathiro["geo"] == g]
    simaies.append(x["simaia_eis"].fillna("").str.contains("b").any())
pinakas["diakopi_seiras"] = simaies

pinakas = pinakas.sort_values("metavoli_eisodimatos")
pinakas.to_csv(f"{EXODOS}/q1_eisodima_metavoli.csv", index=False,
               encoding="utf-8-sig")

# ------------------------------------------------------------
# 7. Αρχείο 3, η ίδια μεταβολή με τέσσερα έτη βάσης
# ------------------------------------------------------------
#
# Το έτος βάσης καθορίζει την απάντηση. Από το 2009 η Ελλάδα είναι
# βαθιά αρνητική, από το 2015 από τις καλύτερες στην Ευρώπη. Και τα
# δύο αληθεύουν. Τα βγάζουμε όλα μαζί.

vaseis = []
for etos_vasis in [2009, 2012, 2015, 2019]:
    v = olo[olo["etos"] == etos_vasis][["geo", "pragmatiko"]]
    v.columns = ["geo", "arxi"]
    t = pd.merge(v, telos[["geo", "eisodima_2024"]], on="geo")
    t["etos_vasis"] = etos_vasis
    t["metavoli"] = (100 * (t["eisodima_2024"] / t["arxi"] - 1)).round(1)
    vaseis.append(t)

vaseis = simane(pd.concat(vaseis))
vaseis.to_csv(f"{EXODOS}/q1_vaseis.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 8. Αρχείο 4, η ελληνική διαδρομή
# ------------------------------------------------------------

ell = olo[olo["geo"] == "EL"].copy()
ell = ell[(ell["etos"] >= 2009) & (ell["etos"] <= 2024)].sort_values("etos")
ell["pragmatiko"] = ell["pragmatiko"].round(0)
ell["imerominia"] = pd.to_datetime(ell["etos"], format="%Y")
ell = ell[["imerominia", "onomastiko", "deiktis", "pragmatiko", "pososto"]]
ell.columns = ["imerominia", "onomastiko", "deiktis_timwn", "pragmatiko",
               "adynamia"]
ell.to_csv(f"{EXODOS}/q1_ellada_seira.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 9. Έλεγχοι. Αν κάποιος δεν βγαίνει, μη συνεχίσεις.
# ------------------------------------------------------------

print("\nΕΛΕΓΧΟΙ")

el = pinakas[pinakas["geo"] == "EL"].iloc[0]
print("1. Ελλάδα εισόδημα:", el["eisodima_2009"], "->", el["eisodima_2024"],
      "ευρώ,", el["metavoli_eisodimatos"], "%   αναμενόμενο -22.3")

print("2. Ελλάδα αδυναμία:", el["adynamia_2009"], "->", el["adynamia_2024"],
      "  αναμενόμενο 46.3 -> 46.6")

melh = pinakas[pinakas["kratos_melos"]]
epesan = melh[melh["metavoli_eisodimatos"] < 0]
print("3. Κράτη μέλη κάτω από το 2009:", list(epesan["geo"]),
      "  αναμενόμενα EL και FR")

print("4. Διακοπή σειράς στην Ελλάδα:", el["diakopi_seiras"],
      "  αναμενόμενο False")

el19 = vaseis[(vaseis["geo"] == "EL") & (vaseis["etos_vasis"] == 2019)]
print("5. Ελλάδα 2019 -> 2024:", el19["metavoli"].values[0], "%",
      "  ΚΕΦΙΜ με εθνικούς λογαριασμούς +14.3")

# Ο έλεγχος που κλειδώνει τη μέθοδο: σύγκριση με τις πραγματικές
# μεταβολές που ανακοίνωσε επίσημα η Eurostat για το 2023 -> 2024.
print("6. Ταύτιση με την επίσημη ανακοίνωση της Eurostat")
anamenomena = {"EU27_2020": 3.6, "SK": 23.8, "HR": 17.3, "BE": -1.5, "RO": -0.8}
for g in anamenomena:
    x = olo[olo["geo"] == g].set_index("etos")["pragmatiko"]
    if 2023 in x.index and 2024 in x.index:
        diko = round(100 * (x[2024] / x[2023] - 1), 1)
        print("   ", g.ljust(10), "δικό μας", str(diko).rjust(6),
              " Eurostat", str(anamenomena[g]).rjust(6))

print("7. Έλεγχος νομίσματος σε κράτη μέλη εκτός ευρωζώνης")
for g, anam in [("HU", 49.9), ("RO", 160.2)]:
    x = pinakas[pinakas["geo"] == g]
    if len(x):
        print("   ", g, x["metavoli_eisodimatos"].values[0], "%",
              " αναμενόμενο", anam)
print("    αν δεις +6.3 και +121.8, η σειρά είναι σε ευρώ και το")
print("    νόμισμα είναι λάθος")

print("\nτα αρχεία γράφτηκαν στον φάκελο", EXODOS)
