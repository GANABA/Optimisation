from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

OUTPUT = "rapport_capteurs.pdf"
W, H = A4
MARGE = 2 * cm

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=MARGE, rightMargin=MARGE,
    topMargin=1.5 * cm, bottomMargin=1.5 * cm
)

# ── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

titre_principal = ParagraphStyle(
    "titre_principal",
    fontSize=14, fontName="Helvetica-Bold",
    alignment=TA_CENTER, spaceAfter=4
)
sous_titre = ParagraphStyle(
    "sous_titre",
    fontSize=9, fontName="Helvetica",
    alignment=TA_CENTER, spaceAfter=2, textColor=colors.HexColor("#555555")
)
section = ParagraphStyle(
    "section",
    fontSize=11, fontName="Helvetica-Bold",
    spaceBefore=10, spaceAfter=4,
    textColor=colors.HexColor("#1a3a6b")
)
corps = ParagraphStyle(
    "corps",
    fontSize=8.5, fontName="Helvetica",
    alignment=TA_JUSTIFY, spaceAfter=4, leading=13
)
corps_bold = ParagraphStyle(
    "corps_bold",
    fontSize=8.5, fontName="Helvetica-Bold",
    spaceAfter=2, leading=13
)
legende = ParagraphStyle(
    "legende",
    fontSize=7.5, fontName="Helvetica-Oblique",
    alignment=TA_CENTER, spaceAfter=6,
    textColor=colors.HexColor("#555555")
)

# ── Couleurs tableau ────────────────────────────────────────────────────────
BLEU_HEADER = colors.HexColor("#1a3a6b")
BLEU_CLAIR  = colors.HexColor("#dce6f1")
GRIS_LIGNE  = colors.HexColor("#f5f5f5")

def style_tableau(nb_cols):
    return TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  BLEU_HEADER),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_LIGNE]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])

# ── Contenu ─────────────────────────────────────────────────────────────────
story = []

# En-tête
story.append(Paragraph("Probleme d'activation de capteurs pour surveillance de zones", titre_principal))
story.append(Paragraph("IUT Nord Franche-Comte  |  Techniques d'optimisation  |  Karine Deschinkel  |  2023-2024", sous_titre))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_HEADER, spaceAfter=8))

# ── SECTION 1 ────────────────────────────────────────────────────────────────
story.append(Paragraph("1. Construction des configurations elementaires", section))

story.append(Paragraph(
    "Une <b>configuration elementaire</b> est un ensemble minimal de capteurs couvrant toutes les zones : "
    "aucun capteur ne peut etre retire sans laisser une zone non surveillee. "
    "Ces configurations constituent les variables du programme lineaire.",
    corps
))

story.append(Paragraph("Deux heuristiques ont ete implementees :", corps_bold))

# Tableau heuristiques
data_h = [
    ["Heuristique", "Principe", "Avantage", "Source"],
    ["Greedy\n(gloutonne)",
     "A chaque etape, choisit le capteur\ncouvrant le plus de zones non\nencore couvertes. En cas d'egalite,\nchoix aleatoire.",
     "Configs de bonne\nqualite individuelle",
     "Cardei & Du\n(2005)"],
    ["Aleatoire",
     "Parcourt les zones dans un ordre\naleatoire, choisit n'importe quel\ncapteur couvrant la zone courante.",
     "Grande diversite\nde configurations",
     "Deschinkel\n(2011)"],
]
t_h = Table(data_h, colWidths=[2.8*cm, 6.5*cm, 3.5*cm, 2.8*cm])
t_h.setStyle(style_tableau(4))
story.append(t_h)
story.append(Paragraph(
    "Dans les deux cas, la configuration est ensuite rendue elementaire en testant "
    "la suppression de chaque capteur (ordre aleatoire) : si la suppression maintient "
    "la couverture totale, le capteur est retire.",
    corps
))

# ── SECTION 2 ────────────────────────────────────────────────────────────────
story.append(Paragraph("2. Solutions obtenues sur les instances (Partie 4)", section))

story.append(Paragraph(
    "Le programme lineaire est resolu avec le solveur CBC (via PuLP, equivalent Python de GLPK). "
    "Les resultats suivants sont obtenus avec 10 configurations elementaires generees par l'heuristique greedy (seed=42) :",
    corps
))

data_res = [
    ["Instance", "N capteurs", "M zones", "Configs\ngenerees", "Duree de vie\nobtenue", "Temps (s)", "Statut"],
    ["fichier-exemple",  "4",   "3",   "4",  "8.5000",    "0.13", "Optimal"],
    ["moyen_test_2",     "20",  "10",  "3",  "15.0000",   "0.17", "Optimal"],
    ["moyen_test_3",     "10",  "10",  "10", "358.0000",  "0.06", "Optimal"],
    ["gros_test_1",      "100", "200", "10", "177.0000",  "0.20", "Optimal"],
]
t_res = Table(data_res, colWidths=[3.5*cm, 2*cm, 1.8*cm, 2*cm, 2.8*cm, 2*cm, 1.8*cm])
t_res.setStyle(style_tableau(7))
story.append(t_res)

story.append(Paragraph(
    "L'instance fichier-exemple atteint l'optimum prouve (8.5) documente dans le sujet. "
    "Pour moyen_test_2, seulement 3 configurations distinctes sont trouvees par le greedy, "
    "ce qui limite la qualite de la solution — l'impact du nombre de configurations est analyse en Partie 5.",
    corps
))

# ── PAGE 2 ───────────────────────────────────────────────────────────────────
story.append(PageBreak())

story.append(Paragraph("Probleme d'activation de capteurs — Analyse des resultats", titre_principal))
story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_HEADER, spaceAfter=8))

# ── SECTION 3 ────────────────────────────────────────────────────────────────
story.append(Paragraph("3. Analyse des resultats (Partie 5)", section))

story.append(Paragraph(
    "Pour un meme probleme, nous examinons l'influence du <b>nombre</b> et du <b>type</b> "
    "des configurations elementaires sur la duree de vie du reseau.",
    corps
))

# 3a - Influence du nombre
story.append(Paragraph("3.1  Influence du nombre de configurations", corps_bold))
story.append(Paragraph(
    "Resultats sur moyen_test_3 (N=10, M=10) avec l'heuristique greedy :",
    corps
))

data_nb = [
    ["Nb configs", "1", "2", "3", "5", "10", "15", "20"],
    ["Greedy",     "55.0", "127.0", "166.0", "268.5", "358.0", "358.0", "358.0"],
    ["Aleatoire",  "90.0", "109.0", "163.0", "235.0", "342.0", "395.0", "395.0"],
]
t_nb = Table(data_nb, colWidths=[2.8*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm])
t_nb.setStyle(TableStyle([
    ("BACKGROUND",  (0, 0), (-1, 0),  BLEU_HEADER),
    ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
    ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
    ("BACKGROUND",  (0, 1), (0, -1),  BLEU_CLAIR),
    ("FONTNAME",    (0, 1), (0, -1),  "Helvetica-Bold"),
    ("FONTSIZE",    (0, 0), (-1, -1), 8),
    ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
    ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
    ("TOPPADDING",  (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t_nb)
story.append(Paragraph(
    "Tableau 1 — Duree de vie en fonction du nombre de configurations (instance moyen_test_3)",
    legende
))

story.append(Paragraph(
    "<b>Observation :</b> la duree de vie augmente significativement avec le nombre de configurations "
    "jusqu'a saturation (plateau a partir de 10-15 configs). Avec 1 seule configuration, on obtient "
    "seulement 55.0 contre 395.0 avec 20 configs, soit une amelioration de +618%. "
    "Au-dela d'un certain seuil, ajouter des configurations n'apporte plus de gain : "
    "toutes les configurations pertinentes ont ete trouvees.",
    corps
))

# 3b - Influence du type
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("3.2  Influence du type d'heuristique", corps_bold))

data_type = [
    ["Instance",        "Heuristique", "Configs reelles", "Duree de vie"],
    ["fichier-exemple", "Greedy",      "4",               "8.5000"],
    ["fichier-exemple", "Aleatoire",   "4",               "8.5000"],
    ["moyen_test_2",    "Greedy",      "3",               "15.0000"],
    ["moyen_test_2",    "Aleatoire",   "10",              "58.0000"],
    ["moyen_test_3",    "Greedy",      "10",              "358.0000"],
    ["moyen_test_3",    "Aleatoire",   "10",              "342.0000"],
]
t_type = Table(data_type, colWidths=[4*cm, 3*cm, 3.5*cm, 3.5*cm])
t_type.setStyle(style_tableau(4))
story.append(t_type)
story.append(Paragraph(
    "Tableau 2 — Comparaison des deux heuristiques avec 10 configurations demandees",
    legende
))

story.append(Paragraph(
    "<b>Observation :</b> aucune heuristique ne domine l'autre systematiquement. "
    "Sur moyen_test_2, l'aleatoire est nettement superieur (58.0 vs 15.0) car le greedy converge "
    "toujours vers les memes capteurs dominants et ne produit que 3 configs distinctes. "
    "Sur moyen_test_3, le greedy prend l'avantage (358.0 vs 342.0) car ses configs sont "
    "individuellement de meilleure qualite. "
    "Ces resultats suggerent qu'une <b>combinaison des deux heuristiques</b> produirait "
    "les meilleurs pools : diversite de l'aleatoire + qualite du greedy.",
    corps
))

# Conclusion
story.append(Spacer(1, 0.3*cm))
story.append(HRFlowable(width="100%", thickness=0.8, color=BLEU_HEADER, spaceAfter=6))
story.append(Paragraph("Conclusion", corps_bold))
story.append(Paragraph(
    "La qualite de la solution depend directement de la richesse du pool de configurations. "
    "Un pool trop petit ou trop homogene bride le programme lineaire. "
    "La strategie optimale consiste a generer un nombre suffisant de configurations (>= 10) "
    "en alternant les deux heuristiques pour maximiser la diversite tout en conservant la qualite.",
    corps
))

story.append(Spacer(1, 0.4*cm))
story.append(Paragraph(
    "References : Cardei &amp; Du (2005) — Wireless Networks | "
    "Manju &amp; Pujari (2011) — arXiv:1103.4769 | "
    "Deschinkel (2011) — SENSORCOMM",
    legende
))

# ── Build ────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"Rapport genere : {OUTPUT}")
