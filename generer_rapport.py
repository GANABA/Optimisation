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
    """Tableau style LaTeX : bordures noires, pas de couleur."""
    return TableStyle([
        # Ligne double simulee en haut (deux lignes fines)
        ("LINEABOVE",    (0, 0), (-1, 0),  1.2, colors.black),
        # Ligne sous l'en-tete
        ("LINEBELOW",    (0, 0), (-1, 0),  0.8, colors.black),
        # Ligne double simulee en bas
        ("LINEBELOW",    (0, -1), (-1, -1), 1.2, colors.black),
        # Lignes verticales
        ("LINEBEFORE",   (0, 0), (0, -1),  0.5, colors.black),
        ("LINEAFTER",    (-1, 0), (-1, -1), 0.5, colors.black),
        # Police en-tete : gras
        ("FONTNAME",     (0, 0), (-1, 0),  "Times-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("FONTNAME",     (0, 1), (-1, -1), "Times-Roman"),
        # Alignement
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        # Padding
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        # Lignes internes legeres
        ("INNERGRID",    (0, 1), (-1, -1), 0.3, colors.HexColor("#888888")),
    ])

# ── Construction du document ─────────────────────────────────────────────────
story = []

# En-tete (institution + annee sur la meme ligne)
W = A4[0] - 2 * MARGE_H
entete_data = [[
    Paragraph("I.U.T. Nord Franche-Comte<br/>Techniques d'optimisation - Karine Deschinkel", entete_gauche),
    Paragraph("2025-2026", entete_droit)
]]
entete_table = Table(entete_data, colWidths=[W * 0.7, W * 0.3])
entete_table.setStyle(TableStyle([
    ("VALIGN",  (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING",   (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ("LEFTPADDING",  (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
story.append(entete_table)
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))

# Titre principal
story.append(Paragraph(
    "Rapport : Probleme d'activation de capteurs pour surveillance de zones",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("1  Construction des configurations elementaires", section))

story.append(Paragraph(
    "Une <b>configuration elementaire</b> est un ensemble minimal de capteurs couvrant "
    "toutes les zones de surveillance : aucun capteur ne peut etre retire sans laisser "
    "au moins une zone non couverte. Ces configurations constituent les variables du "
    "programme lineaire d'ordonnancement.",
    corps
))

story.append(Paragraph("Deux heuristiques ont ete implementees :", corps))

data_h = [
    ["Heuristique", "Principe de construction", "Avantage", "Reference"],
    ["Greedy\n(gloutonne)",
     "A chaque etape, selectionne le capteur\ncouvrant le plus grand nombre de zones\nnon encore couvertes.\nEn cas d'egalite, choix aleatoire.",
     "Configs de bonne\nqualite individuelle",
     "Cardei & Du\n(2005)"],
    ["HEF\n(High-Energy-\nFirst)",
     "A chaque etape, selectionne parmi les\ncapteurs utiles celui ayant la plus\ngrande duree de vie (energie) initiale.\nEn cas d'egalite, choix aleatoire.",
     "Favorise les\ncapteurs a longue\nduree de vie",
     "Manju &\nPujari\n(2011)"],
    ["Aleatoire",
     "Parcourt les zones dans un ordre\naleatoire. Pour chaque zone non\ncouverte, choisit un capteur\ncouvrant cette zone au hasard.",
     "Grande diversite\ndu pool de\nconfiguration",
     "Deschinkel\n(2011)"],
]
t_h = Table(data_h, colWidths=[2.6*cm, 6.8*cm, 3.2*cm, 2.6*cm])
t_h.setStyle(style_tableau_latex())
story.append(t_h)
story.append(Spacer(1, 4))

story.append(Paragraph(
    "Dans les deux cas, la configuration construite est ensuite rendue elementaire "
    "en testant la suppression de chaque capteur dans un ordre aleatoire : si la "
    "couverture totale est maintenue apres suppression, le capteur est retire "
    "definitivement.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("2  Solutions obtenues sur les instances", section))

story.append(Paragraph(
    "Le programme lineaire est formule et resolu avec la bibliotheque PuLP (solveur CBC). "
    "Les resultats suivants sont obtenus avec au plus 30 configurations elementaires "
    "generees par heuristique greedy (seed = 42). La borne superieure theorique est calculee "
    "par upper_bound() = min<sub>z</sub> &Sigma;<sub>k couvre z</sub> T<sub>k</sub> "
    "(Manju &amp; Pujari, 2011) :",
    corps
))

data_res = [
    ["Instance", "N", "M", "Configs\ngenerees", "Borne\nsup.", "Duree de vie\n(greedy)", "% borne", "Statut"],
    ["fichier-exemple",  "4",    "3",   "4",  "9.0",     "8.5000",    "94 %",  "Optimal"],
    ["moyen_test_2",     "20",   "10",  "3",  "104.0",   "15.0000",   "14 %",  "Optimal"],
    ["moyen_test_3",     "10",   "10",  "10", "463.0",   "358.0000",  "77 %",  "Optimal"],
    ["gros_test_1",      "100",  "200", "30", "3437.0",  "177.0000",  "5 %",   "Optimal"],
    ["maxi_test_1",      "1000", "500", "30", "27245.0", "506.0000",  "1 %",   "Optimal"],
]
t_res = Table(data_res, colWidths=[3.2*cm, 1.1*cm, 1.1*cm, 1.8*cm, 2.2*cm, 2.6*cm, 1.6*cm, 1.9*cm])
t_res.setStyle(style_tableau_latex())
story.append(t_res)
story.append(Spacer(1, 4))

story.append(Paragraph(
    "L'instance fichier-exemple atteint 8.5, coherent avec l'optimum prouve du sujet "
    "(borne sup. = 9.0). Sur les grandes instances, l'ecart a la borne superieure est "
    "considerable (5 % pour gros_test_1, 1 % pour maxi_test_1) : le greedy seul, limite "
    "a quelques configurations distinctes, ne suffit pas — ce phenomene est analyse en section 3.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2
# ═══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())

# En-tete page 2
story.append(entete_table)
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))
story.append(Paragraph(
    "Rapport : Probleme d'activation de capteurs — Analyse des resultats",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3
# ═══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3  Analyse des resultats", section))

story.append(Paragraph(
    "Pour un meme probleme, nous examinons l'influence du <b>nombre</b> et du <b>type</b> "
    "des configurations elementaires choisies sur la duree de vie du reseau.",
    corps
))

# 3.1
story.append(Paragraph("3.1  Influence du nombre de configurations", sous_section))

story.append(Paragraph(
    "Le tableau suivant presente la duree de vie obtenue sur moyen_test_3 (N=10, M=10, "
    "borne sup. = 463.0) en faisant varier le nombre de configurations pour les trois heuristiques :",
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
    "Tableau 1 - Duree de vie en fonction du nombre de configurations (moyen_test_3, borne = 463.0)",
    corps_it
))

story.append(Paragraph(
    "La duree de vie augmente significativement avec le nombre de configurations jusqu'a "
    "atteindre un plateau (10 configs pour greedy, 15 pour aleatoire). HEF stagne "
    "a 166.0 quelle que soit la demande : etant deterministe, il ne produit qu'une seule "
    "configuration distincte. L'amelioration entre 1 et 20 configs atteint +618 % pour "
    "l'aleatoire (55.0 -> 395.0). Au-dela du seuil de saturation, le LP ne progresse plus "
    "car toutes les configurations pertinentes ont ete trouvees.",
    corps
))

# 3.2
story.append(Paragraph("3.2  Influence du type d'heuristique", sous_section))

story.append(Paragraph(
    "Le tableau suivant compare les trois heuristiques (30 configurations demandees, seed=42) "
    "sur toutes les instances. Format : nb configs obtenues / duree de vie (% borne sup.) :",
    corps
))

data_type = [
    ["Instance",        "Greedy\ncfgs / duree (% borne)", "HEF\ncfgs / duree (% borne)", "Aleatoire\ncfgs / duree (% borne)"],
    ["fichier-exemple", "4 / 8.5 (94 %)",   "1 / 6.0 (66 %)",    "4 / 8.5 (94 %)"],
    ["moyen_test_2",    "3 / 15.0 (14 %)",  "2 / 19.0 (18 %)",   "30 / 104.0 (100 %)"],
    ["moyen_test_3",    "10 / 358.0 (77 %)", "1 / 166.0 (35 %)", "18 / 395.0 (85 %)"],
    ["gros_test_1",     "30 / 177.0 (5 %)", "1 / 196.0 (5 %)",   "30 / 992.0 (28 %)"],
    ["maxi_test_1",     "30 / 506.0 (1 %)", "3 / 197.0 (0 %)",   "30 / 1463.0 (5 %)"],
]
t_type = Table(data_type, colWidths=[3.4*cm, 4.7*cm, 4.2*cm, 4.2*cm])
t_type.setStyle(style_tableau_latex())
story.append(t_type)
story.append(Paragraph(
    "Tableau 2 - Comparaison des trois heuristiques sur toutes les instances (30 configs demandees)",
    corps_it
))

story.append(Paragraph(
    "L'aleatoire atteint 100 % de la borne superieure sur moyen_test_2 (104.0/104.0), "
    "grace a la diversite de ses 30 configurations. Sur les grandes instances, l'ecart "
    "reste important (28 % pour gros_test_1, 5 % pour maxi_test_1) : un pool de 30 configs "
    "est insuffisant a cette echelle. HEF produit 1 a 3 configurations distinctes seulement — "
    "deterministe par nature, il choisit toujours les memes capteurs a haute energie — "
    "ce qui plafonne la solution LP. L'aleatoire domine sur toutes les instances sauf "
    "fichier-exemple (egalite avec greedy). Ces resultats confirment qu'une <b>combinaison "
    "greedy + aleatoire</b> offre le meilleur compromis qualite/diversite.",
    corps
))

story.append(Spacer(1, 0.2*cm))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))

story.append(Paragraph(
    "<b>Conclusion.</b> "
    "La qualite de la solution depend directement de la richesse du pool de configurations. "
    "Sur les petites instances (N &lt; 20), 10 a 30 configurations suffisent pour s'approcher "
    "de la borne superieure. Sur les grandes instances (N = 100-1000), 30 configurations "
    "restent largement insuffisantes : l'ecart a la borne depasse 70 %. La strategie optimale "
    "consiste a combiner greedy et aleatoire pour maximiser la diversite tout en preservant "
    "la qualite individuelle de chaque configuration ; HEF seul est a eviter.",
    corps
))

story.append(Spacer(1, 0.15*cm))
story.append(Paragraph(
    "References : Cardei & Du (2005), Wireless Networks, vol. 11, pp. 333-340.  |  "
    "Manju & Pujari (2011), arXiv:1103.4769.  |  Deschinkel (2011), SENSORCOMM, Nice.",
    corps_it
))

# ── Generation ───────────────────────────────────────────────────────────────
doc.build(story)
print(f"Rapport genere : {OUTPUT}")
