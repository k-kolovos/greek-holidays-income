# Ερώτημα 2: πού μένουν όσοι κάνουν διακοπές
#
# Πηγές: Eurostat tour_dem_tttot, tour_dem_tntot, tour_dem_extot,
#        tour_dem_tnac, demo_gind
# Παράγει: q2_seira.csv, q2_2024.csv, q2_dapani.csv, q2_katalyma.csv
#
# Αν μετρήσεις μόνο ταξίδια, η Ελλάδα βγαίνει 66% κάτω από την ΕΕ.
# Αν μετρήσεις νύχτες, μόλις 15% κάτω. Ο λόγος είναι η διάρκεια:
# ένα ταξίδι δέκα νυχτών έναντι τεσσάρων ταξιδιών τεσσάρων νυχτών.
# Γι' αυτό βγάζουμε και τα τρία μεγέθη μαζί.

import os
import pandas as pd

EXODOS = "../dedomena"
os.makedirs(EXODOS, exist_ok=True)

VASI = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"

# ------------------------------------------------------------
# 1. Κατέβασμα
# ------------------------------------------------------------

taxidia = pd.read_csv(VASI + "TOUR_DEM_TTTOT/?format=SDMX-CSV", low_memory=False)
nyxtes = pd.read_csv(VASI + "TOUR_DEM_TNTOT/?format=SDMX-CSV", low_memory=False)
dapani = pd.read_csv(VASI + "TOUR_DEM_EXTOT/?format=SDMX-CSV", low_memory=False)
katalyma = pd.read_csv(VASI + "TOUR_DEM_TNAC/?format=SDMX-CSV", low_memory=False)
plithysmos = pd.read_csv(VASI + "DEMO_GIND/?format=SDMX-CSV", low_memory=False)

print("κατέβηκαν", len(taxidia), len(nyxtes), len(dapani),
      len(katalyma), len(plithysmos), "γραμμές")

# ------------------------------------------------------------
# 2. Καθάρισμα
# ------------------------------------------------------------
#
# purpose PER    προσωπικοί λόγοι, όχι επαγγελματικά ταξίδια
# duration N_GE1 τουλάχιστον μία διανυκτέρευση
# c_dest DOM     εντός της χώρας,  FOR εξωτερικό

taxidia = taxidia[(taxidia["purpose"] == "PER") & (taxidia["duration"] == "N_GE1")]
taxidia = taxidia[taxidia["c_dest"].isin(["DOM", "FOR"])]
taxidia = taxidia[["geo", "c_dest", "TIME_PERIOD", "OBS_VALUE"]]
taxidia.columns = ["geo", "proorismos", "etos", "taxidia"]

nyxtes = nyxtes[(nyxtes["purpose"] == "PER") & (nyxtes["duration"] == "N_GE1")]
nyxtes = nyxtes[nyxtes["c_dest"].isin(["DOM", "FOR"])]
nyxtes = nyxtes[["geo", "c_dest", "TIME_PERIOD", "OBS_VALUE"]]
nyxtes.columns = ["geo", "proorismos", "etos", "nyxtes"]

dapani = dapani[(dapani["purpose"] == "PER") & (dapani["duration"] == "N_GE1")]
dapani = dapani[(dapani["expend"] == "TOTXDUR") & dapani["c_dest"].isin(["DOM", "FOR"])]
dapani = dapani[["geo", "c_dest", "TIME_PERIOD", "statinfo", "OBS_VALUE"]]
dapani.columns = ["geo", "proorismos", "etos", "deiktis", "poso"]

ana_taxidi = dapani[dapani["deiktis"] == "AVG_TRP"][
    ["geo", "proorismos", "etos", "poso"]]
ana_taxidi.columns = ["geo", "proorismos", "etos", "evro_ana_taxidi"]

ana_nyxta = dapani[dapani["deiktis"] == "AVG_NGT"][
    ["geo", "proorismos", "etos", "poso"]]
ana_nyxta.columns = ["geo", "proorismos", "etos", "evro_ana_nyxta"]

plithysmos = plithysmos[plithysmos["indic_de"] == "AVG"]
plithysmos = plithysmos[["geo", "TIME_PERIOD", "OBS_VALUE"]]
plithysmos.columns = ["geo", "etos", "plithysmos"]

# ------------------------------------------------------------
# 3. Ένωση και υπολογισμοί
# ------------------------------------------------------------

olo = pd.merge(taxidia, nyxtes, on=["geo", "proorismos", "etos"])
olo = pd.merge(olo, plithysmos, on=["geo", "etos"])
olo = pd.merge(olo, ana_taxidi, on=["geo", "proorismos", "etos"], how="left")
olo = pd.merge(olo, ana_nyxta, on=["geo", "proorismos", "etos"], how="left")

olo["taxidia_ana_katoiko"] = (olo["taxidia"] / olo["plithysmos"]).round(2)
olo["nyxtes_ana_katoiko"] = (olo["nyxtes"] / olo["plithysmos"]).round(2)
olo["nyxtes_ana_taxidi"] = (olo["nyxtes"] / olo["taxidia"]).round(1)

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
kratimeli = [k for k in xores if k != "EU27_2020"]
krisi = ["EL", "ES", "IT", "IE", "CY", "PT"]

olo["xora"] = olo["geo"].map(xores).fillna(olo["geo"])
olo["kratos_melos"] = olo["geo"].isin(kratimeli)
olo["xora_krisis"] = olo["geo"].isin(krisi)
olo["einai_ellada"] = olo["geo"] == "EL"
olo["einai_ee"] = olo["geo"] == "EU27_2020"
olo["omada_xrwmatos"] = "Υπόλοιπες"
olo.loc[olo["einai_ee"], "omada_xrwmatos"] = "ΕΕ27"
olo.loc[olo["einai_ellada"], "omada_xrwmatos"] = "Ελλάδα"

onomata_proorismou = {"DOM": "Εντός της χώρας", "FOR": "Εξωτερικό"}
olo["proorismos_onoma"] = olo["proorismos"].map(onomata_proorismou)

# ------------------------------------------------------------
# 5. Αρχείο 1, η χρονοσειρά
# ------------------------------------------------------------

seira = olo[olo["etos"] >= 2012].copy()
seira["imerominia"] = pd.to_datetime(seira["etos"], format="%Y")
seira = seira.drop(columns=["etos", "taxidia", "nyxtes", "plithysmos"])
seira.to_csv(f"{EXODOS}/q2_seira.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 6. Αρχείο 2, το 2024 σε μία γραμμή ανά χώρα
# ------------------------------------------------------------
# Εγχώρια και εξωτερικού σε ξεχωριστές στήλες, για διαγράμματα διασποράς.

t24 = olo[olo["etos"] == 2024]

dom = t24[t24["proorismos"] == "DOM"][
    ["geo", "xora", "taxidia_ana_katoiko", "nyxtes_ana_katoiko",
     "nyxtes_ana_taxidi", "evro_ana_nyxta", "evro_ana_taxidi"]]
dom.columns = ["geo", "xora", "egxwria_taxidia", "egxwries_nyxtes",
               "egxwries_nyxtes_ana_taxidi", "egxwria_evro_nyxta",
               "egxwria_evro_taxidi"]

xen = t24[t24["proorismos"] == "FOR"][
    ["geo", "taxidia_ana_katoiko", "nyxtes_ana_katoiko",
     "nyxtes_ana_taxidi", "evro_ana_nyxta", "evro_ana_taxidi"]]
xen.columns = ["geo", "ekswt_taxidia", "ekswt_nyxtes",
               "ekswt_nyxtes_ana_taxidi", "ekswt_evro_nyxta",
               "ekswt_evro_taxidi"]

p24 = pd.merge(dom, xen, on="geo")
p24["synolo_taxidia"] = (p24["egxwria_taxidia"] + p24["ekswt_taxidia"]).round(2)
p24["synolo_nyxtes"] = (p24["egxwries_nyxtes"] + p24["ekswt_nyxtes"]).round(2)
p24["pososto_ekswterikou"] = (
    100 * p24["ekswt_taxidia"] / p24["synolo_taxidia"]).round(1)

p24["kratos_melos"] = p24["geo"].isin(kratimeli)
p24["xora_krisis"] = p24["geo"].isin(krisi)
p24["einai_ellada"] = p24["geo"] == "EL"
p24["einai_ee"] = p24["geo"] == "EU27_2020"
p24["omada_xrwmatos"] = "Υπόλοιπες"
p24.loc[p24["einai_ee"], "omada_xrwmatos"] = "ΕΕ27"
p24.loc[p24["einai_ellada"], "omada_xrwmatos"] = "Ελλάδα"

p24 = p24.sort_values("egxwries_nyxtes", ascending=False)
p24.to_csv(f"{EXODOS}/q2_2024.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 7. Αρχείο 3, η δαπάνη
# ------------------------------------------------------------

dap = olo[(olo["etos"] >= 2012) & (olo["evro_ana_nyxta"].notna())].copy()
dap["imerominia"] = pd.to_datetime(dap["etos"], format="%Y")
dap = dap[["geo", "xora", "proorismos", "proorismos_onoma", "imerominia",
           "evro_ana_taxidi", "evro_ana_nyxta", "nyxtes_ana_taxidi",
           "kratos_melos", "xora_krisis", "einai_ellada", "einai_ee",
           "omada_xrwmatos"]]
dap.to_csv(f"{EXODOS}/q2_dapani.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 8. Αρχείο 4, το κατάλυμα. Εδώ βγαίνει το κεντρικό εύρημα.
# ------------------------------------------------------------

kat = katalyma[(katalyma["purpose"] == "PER") & (katalyma["duration"] == "N_GE1")]
kat = kat[kat["c_dest"].isin(["DOM", "FOR"]) & (kat["TIME_PERIOD"] == 2024)]
kat = kat[["geo", "c_dest", "accommod", "OBS_VALUE"]]
kat.columns = ["geo", "proorismos", "typos", "nyxtes"]

synola = kat[kat["typos"] == "TOTAL"][["geo", "proorismos", "nyxtes"]]
synola.columns = ["geo", "proorismos", "synolo"]
kat = pd.merge(kat, synola, on=["geo", "proorismos"])
kat["pososto"] = (100 * kat["nyxtes"] / kat["synolo"]).round(1)

onomata_typwn = {
    "NR_OWN": "Δικό τους σπίτι",
    "NR_RF": "Συγγενείς και φίλοι",
    "NR_OTH": "Άλλο μη πληρωμένο",
    "R_HOT": "Ξενοδοχείο",
    "R_APT": "Ενοικιαζόμενο διαμέρισμα",
    "R_CAMP": "Κάμπινγκ",
    "R_OTH": "Άλλο πληρωμένο",
    "TOT_NR": "ΣΥΝΟΛΟ μη πληρωμένο",
    "TOT_R": "ΣΥΝΟΛΟ πληρωμένο",
    "TOTAL": "ΣΥΝΟΛΟ",
}
kat["typos_onoma"] = kat["typos"].map(onomata_typwn)
kat["proorismos_onoma"] = kat["proorismos"].map(onomata_proorismou)

# Στις στοιβαγμένες μπάρες χρειάζονται μόνο οι επτά επιμέρους
# κατηγορίες. Χωρίς αυτό το φίλτρο το ποσοστό βγαίνει 200%.
kat["einai_athroisma"] = kat["typos"].isin(["TOTAL", "TOT_NR", "TOT_R"])

kat["xora"] = kat["geo"].map(xores).fillna(kat["geo"])
kat["kratos_melos"] = kat["geo"].isin(kratimeli)
kat["xora_krisis"] = kat["geo"].isin(krisi)
kat["einai_ellada"] = kat["geo"] == "EL"
kat["einai_ee"] = kat["geo"] == "EU27_2020"

kat = kat.drop(columns=["synolo"])
kat.to_csv(f"{EXODOS}/q2_katalyma.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# 9. Έλεγχοι
# ------------------------------------------------------------

print("\nΕΛΕΓΧΟΙ")

el = p24[p24["geo"] == "EL"].iloc[0]
ee = p24[p24["geo"] == "EU27_2020"].iloc[0]

print("1. Ελλάδα εγχώρια:", el["egxwria_taxidia"], "ταξίδια,",
      el["egxwries_nyxtes_ana_taxidi"], "νύχτες,",
      el["egxwries_nyxtes"], "συνολικά   αναμενόμενα 0.58, 10.1, 5.83")

print("2. ΕΕ27 εγχώρια:", ee["egxwria_taxidia"], "ταξίδια,",
      ee["egxwries_nyxtes_ana_taxidi"], "νύχτες,",
      ee["egxwries_nyxtes"], "συνολικά   αναμενόμενα 1.69, 4.0, 6.82")

d_tax = 100 * (el["egxwria_taxidia"] / ee["egxwria_taxidia"] - 1)
d_nyx = 100 * (el["egxwries_nyxtes"] / ee["egxwries_nyxtes"] - 1)
print("3. Ελλάδα έναντι ΕΕ27: σε ταξίδια", round(d_tax, 1),
      "%   σε νύχτες", round(d_nyx, 1), "%   αναμενόμενα -66 και -15")

print("4. Δαπάνη ανά νύχτα εντός χώρας: Ελλάδα", el["egxwria_evro_nyxta"],
      "ΕΕ27", ee["egxwria_evro_nyxta"], "  αναμενόμενα 40 και 72")

print("\nτα αρχεία γράφτηκαν στον φάκελο", EXODOS)
