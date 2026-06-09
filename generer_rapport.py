from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

OUTPUT = "rapport_capteurs.pdf"
MARGE_H = 2.2 * cm
MARGE_V = 1.8 * cm

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=MARGE_H, rightMargin=MARGE_H,
    topMargin=MARGE_V, bottomMargin=MARGE_V
)

# ── Styles (Times-Roman comme LaTeX) ────────────────────────────────────────

entete_gauche = ParagraphStyle(
    "entete_gauche",
    fontName="Times-Roman", fontSize=9,
    alignment=TA_LEFT, leading=13
)
entete_droit = ParagraphStyle(
    "entete_droit",
    fontName="Times-Roman", fontSize=9,
    alignment=TA_RIGHT, leading=13
)
titre = ParagraphStyle(
    "titre",
    fontName="Times-Bold", fontSize=13,
    alignment=TA_CENTER, spaceBefore=6, spaceAfter=8, leading=16
)
section = ParagraphStyle(
    "section",
    fontName="Times-Bold", fontSize=12,
    spaceBefore=10, spaceAfter=4, leading=15
)
sous_section = ParagraphStyle(
    "sous_section",
    fontName="Times-Bold", fontSize=10.5,
    spaceBefore=7, spaceAfter=3, leading=13
)
corps = ParagraphStyle(
    "corps",
    fontName="Times-Roman", fontSize=10.5,
    alignment=TA_JUSTIFY, spaceAfter=5, leading=14
)
corps_it = ParagraphStyle(
    "corps_it",
    fontName="Times-Italic", fontSize=9,
    alignment=TA_CENTER, spaceAfter=4, leading=12,
    textColor=colors.HexColor("#444444")
)

def style_tableau_latex():
    return TableStyle([
        ("LINEABOVE",    (0, 0), (-1, 0),  1.2, colors.black),
        ("LINEBELOW",    (0, 0), (-1, 0),  0.8, colors.black),
        ("LINEBELOW",    (0, -1), (-1, -1), 1.2, colors.black),
        ("LINEBEFORE",   (0, 0), (0, -1),  0.5, colors.black),
        ("LINEAFTER",    (-1, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME",     (0, 0), (-1, 0),  "Times-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("FONTNAME",     (0, 1), (-1, -1), "Times-Roman"),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("INNERGRID",    (0, 1), (-1, -1), 0.3, colors.HexColor("#888888")),
    ])

# ── Construction du document ─────────────────────────────────────────────────
story = []

W = A4[0] - 2 * MARGE_H
entete_data = [[
    Paragraph("I.U.T. Nord Franche-Comte<br/>Techniques d'optimisation - Karine Deschinkel", entete_gauche),
    Paragraph("2025-2026", entete_droit)
]]
entete_table = Table(entete_data, colWidths=[W * 0.7, W * 0.3])
entete_table.setStyle(TableStyle([
    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING",    (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("LEFTPADDING",   (0, 0), (-1, -1), 0),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
]))
story.append(entete_table)
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))

story.append(Paragraph(
    "Rapport : Probleme d'activation de capteurs pour surveillance de zones",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Configurations elementaires
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("1  Construction des configurations elementaires", section))

story.append(Paragraph(
    "Une <b>configuration elementaire</b> est un ensemble minimal de capteurs couvrant "
    "toutes les zones : aucun capteur ne peut etre retire sans laisser une zone non couverte. "
    "Ces configurations sont les variables du programme lineaire.",
    corps
))

story.append(Paragraph("Trois heuristiques ont ete implementees :", corps))

data_h = [
    ["Heuristique", "Principe de construction", "Avantage", "Reference"],
    ["Greedy\n(gloutonne)",
     "A chaque etape, selectionne le capteur\ncouvrant le plus grand nombre de zones\nnon encore couvertes. En cas d'egalite,\nchoix aleatoire.",
     "Configs de bonne\nqualite individuelle",
     "Cardei & Du\n(2005)"],
    ["HEF\n(High-Energy-\nFirst)",
     "A chaque etape, selectionne parmi les\ncapteurs utiles celui ayant la plus\ngrande duree de vie initiale.\nEn cas d'egalite, choix aleatoire.",
     "Favorise les\ncapteurs a longue\nduree de vie",
     "Manju &\nPujari\n(2011)"],
    ["Aleatoire",
     "Parcourt les zones dans un ordre\naleatoire. Pour chaque zone non\ncouverte, choisit un capteur au hasard.",
     "Grande diversite\ndu pool de\nconfiguration",
     "Deschinkel\n(2011)"],
]
t_h = Table(data_h, colWidths=[2.6*cm, 6.8*cm, 3.2*cm, 2.6*cm])
t_h.setStyle(style_tableau_latex())
story.append(t_h)
story.append(Spacer(1, 4))

story.append(Paragraph(
    "Dans les trois cas, la configuration construite est ensuite rendue elementaire "
    "en testant la suppression de chaque capteur dans un ordre aleatoire.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Resultats V1
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("2  Solutions obtenues par heuristiques (V1)", section))

story.append(Paragraph(
    "Le programme lineaire est resolu avec PuLP/CBC. La borne superieure theorique est "
    "upper_bound() = min<sub>z</sub> &Sigma; T<sub>k</sub> (Manju &amp; Pujari, 2011). "
    "Resultats obtenus avec 30 configurations par heuristique (seed = 42) :",
    corps
))

data_type = [
    ["Instance", "Greedy\ncfgs / duree (% borne)", "HEF\ncfgs / duree (% borne)", "Aleatoire\ncfgs / duree (% borne)"],
    ["fichier-exemple", "4 / 8.5 (94 %)",    "1 / 6.0 (66 %)",    "4 / 8.5 (94 %)"],
    ["moyen_test_2",    "3 / 15.0 (14 %)",   "2 / 19.0 (18 %)",   "30 / 104.0 (100 %)"],
    ["moyen_test_3",    "10 / 358.0 (77 %)", "1 / 166.0 (35 %)",  "18 / 395.0 (85 %)"],
    ["gros_test_1",     "30 / 177.0 (5 %)",  "1 / 196.0 (5 %)",   "30 / 992.0 (28 %)"],
    ["maxi_test_1",     "30 / 506.0 (1 %)",  "3 / 197.0 (0 %)",   "30 / 1463.0 (5 %)"],
]
t_type = Table(data_type, colWidths=[3.4*cm, 4.7*cm, 4.2*cm, 4.2*cm])
t_type.setStyle(style_tableau_latex())
story.append(t_type)
story.append(Paragraph(
    "Tableau 1 - Comparaison des trois heuristiques sur toutes les instances (30 configs demandees)",
    corps_it
))

story.append(Paragraph(
    "L'aleatoire domine sur toutes les grandes instances et atteint 100 % de la borne "
    "sur moyen_test_2. HEF, tres deterministe (1 a 3 configs), plafonne systematiquement. "
    "Sur gros_test_1 et maxi_test_1, l'ecart a la borne reste tres important (5 % max) "
    ": 30 configurations heuristiques sont insuffisantes a cette echelle.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2
# ═══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())

story.append(entete_table)
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))
story.append(Paragraph(
    "Rapport : Probleme d'activation de capteurs — Generation de colonnes et analyse",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Generation de colonnes (V2)
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3  Generation de colonnes — methode exacte (V2)", section))

story.append(Paragraph(
    "La generation de colonnes (Deschinkel, 2011) est une methode <b>exacte</b> qui alterne "
    "un <i>programme maitre</i> (LP sur le pool courant, donne les prix duaux pi_k) et un "
    "<i>probleme de pricing</i> (PLNE : cherche la configuration minimisant sum(pi_k)). "
    "Si le cout reduit 1 - sum(pi_k) &lt;= 0, l'optimum est prouve mathematiquement. "
    "Comparaison V1 (meilleure heuristique) vs V2 :",
    corps
))

data_cmp = [
    ["Instance",        "V1 - Aleatoire\n(30 configs)", "V2 - Gen. colonnes\n(pool initial 30)", "Iterations\nV2", "Temps\nV2"],
    ["fichier-exemple", "8.5 (94 %)",     "8.5 (94 %)",     "1",   "0.04 s"],
    ["moyen_test_2",    "104.0 (100 %)",  "104.0 (100 %)",  "1",   "0.05 s"],
    ["moyen_test_3",    "395.0 (85 %)",   "395.0 (85 %)",   "1",   "0.04 s"],
    ["gros_test_1",     "992.0 (28 %)",   "3096.1 (90 %)",  "487", "1135 s"],
    ["maxi_test_1",     "1463.0 (5 %)",   "—",              "—",   "—"],
]
t_cmp = Table(data_cmp, colWidths=[3.4*cm, 3.8*cm, 4.0*cm, 2.2*cm, 2.1*cm])
t_cmp.setStyle(style_tableau_latex())
story.append(t_cmp)
story.append(Paragraph(
    "Tableau 2 - Comparaison V1 vs V2 (bornes : fichier-exemple=9.0, moyen_test_2=104.0, moyen_test_3=463.0, gros_test_1=3437.0)",
    corps_it
))

story.append(Paragraph(
    "Sur les petites instances, V2 termine en <b>1 iteration</b> : le pool aleatoire initial "
    "contient deja toutes les configurations necessaires. Sur gros_test_1, V2 passe de "
    "<b>28 % a 90 %</b> de la borne en 487 iterations (516 configurations, 1135 s), "
    "illustrant la puissance de la methode exacte mais aussi son cout en temps de calcul. "
    "maxi_test_1 (N=1000) reste hors de portee : le pricing PLNE, NP-difficile, "
    "ne passe pas a cette echelle.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Influence du nombre de configurations
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("4  Influence du nombre de configurations", sous_section))

story.append(Paragraph(
    "Sur moyen_test_3 (N=10, M=10, borne = 463.0) en faisant varier le nombre de configs :",
    corps
))

data_nb = [
    ["Heuristique \\ Nb configs", "1", "2", "3", "5", "10", "15", "20"],
    ["Greedy",    "55.0",  "127.0", "166.0", "268.5", "358.0", "358.0", "358.0"],
    ["HEF",       "166.0", "166.0", "166.0", "166.0", "166.0", "166.0", "166.0"],
    ["Aleatoire", "90.0",  "109.0", "163.0", "235.0", "342.0", "395.0", "395.0"],
]
col_w = [3.4*cm] + [1.44*cm]*7
t_nb = Table(data_nb, colWidths=col_w)
t_nb.setStyle(style_tableau_latex())
story.append(t_nb)
story.append(Paragraph(
    "Tableau 3 - Duree de vie selon le nombre de configurations (moyen_test_3, borne = 463.0)",
    corps_it
))

story.append(Paragraph(
    "La duree de vie progresse jusqu'a saturation (10 configs greedy, 15 aleatoire). "
    "HEF stagne a 166.0 quelle que soit la demande : deterministe, il ne produit "
    "qu'une seule configuration. La combinaison greedy + aleatoire est optimale.",
    corps
))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=4, spaceAfter=4))

story.append(Paragraph(
    "<b>Conclusion.</b> "
    "Les heuristiques V1 sont rapides mais limitees sur les grandes instances (ecart > 70 %). "
    "La generation de colonnes V2 prouve l'optimalite mais son oracle exact devient "
    "prohibitif pour N &gt; 100. Une piste : remplacer le pricing exact (PLNE) par une "
    "heuristique de pricing pour passer a l'echelle.",
    corps
))

story.append(Paragraph(
    "References : Cardei &amp; Du (2005), Wireless Networks, vol. 11, pp. 333-340.  |  "
    "Manju &amp; Pujari (2011), arXiv:1103.4769.  |  Deschinkel (2011), SENSORCOMM, Nice.",
    corps_it
))

# ── Generation ───────────────────────────────────────────────────────────
doc.build(story)
print(f"Rapport genere : {OUTPUT}")
