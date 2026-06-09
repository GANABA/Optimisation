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
    "Le programme lineaire est formule et resolu avec la bibliotheque PuLP (solveur CBC, "
    "equivalent libre de GLPK). Les resultats suivants sont obtenus avec 10 configurations "
    "elementaires generees par heuristique greedy (graine aleatoire fixee : seed = 42) :",
    corps
))

data_res = [
    ["Instance", "N", "M", "Configs\ngenerees", "Duree de vie\nobtenue", "Temps (s)", "Statut"],
    ["fichier-exemple",  "4",   "3",   "4",  "8.5000",    "0.13", "Optimal"],
    ["moyen_test_2",     "20",  "10",  "3",  "15.0000",   "0.17", "Optimal"],
    ["moyen_test_3",     "10",  "10",  "10", "358.0000",  "0.06", "Optimal"],
    ["gros_test_1",      "100", "200", "10", "177.0000",  "0.20", "Optimal"],
]
t_res = Table(data_res, colWidths=[3.6*cm, 1.2*cm, 1.2*cm, 2.2*cm, 3.0*cm, 2.2*cm, 2.0*cm])
t_res.setStyle(style_tableau_latex())
story.append(t_res)
story.append(Spacer(1, 4))

story.append(Paragraph(
    "L'instance fichier-exemple atteint l'optimum prouve de 8.5 documente dans le sujet, "
    "ce qui valide l'implementation. Pour moyen_test_2, le greedy ne produit que 3 "
    "configurations distinctes, ce qui limite la qualite — ce phenomene est analyse "
    "en section 3.",
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
    "Le tableau suivant presente la duree de vie obtenue sur moyen_test_3 (N=10, M=10) "
    "en faisant varier le nombre de configurations pour chacune des deux heuristiques :",
    corps
))

data_nb = [
    ["Heuristique \\ Nb configs", "1", "2", "3", "5", "10", "15", "20"],
    ["Greedy",     "55.0", "127.0", "166.0", "268.5", "358.0", "358.0", "358.0"],
    ["Aleatoire",  "90.0", "109.0", "163.0", "235.0", "342.0", "395.0", "395.0"],
]
col_w = [3.8*cm] + [1.55*cm]*7
t_nb = Table(data_nb, colWidths=col_w)
t_nb.setStyle(style_tableau_latex())
story.append(t_nb)
story.append(Paragraph(
    "Tableau 1 - Duree de vie en fonction du nombre de configurations (instance moyen_test_3)",
    corps_it
))

story.append(Paragraph(
    "La duree de vie augmente significativement avec le nombre de configurations jusqu'a "
    "atteindre un plateau (a partir de 10 configs pour le greedy, 15 pour l'aleatoire). "
    "Avec une seule configuration, on obtient 55.0 contre 395.0 avec 20 configurations, "
    "soit une amelioration de +618 %. Au-dela du seuil de saturation, ajouter de nouvelles "
    "configurations n'apporte plus de gain : toutes les configurations pertinentes ont ete "
    "trouvees et le LP atteint sa solution optimale sur ce pool.",
    corps
))

# 3.2
story.append(Paragraph("3.2  Influence du type d'heuristique", sous_section))

story.append(Paragraph(
    "Le tableau suivant compare les deux heuristiques avec 10 configurations demandees "
    "sur chaque instance :",
    corps
))

data_type = [
    ["Instance",        "Heuristique", "Configs\nobtenues", "Duree de vie"],
    ["fichier-exemple", "Greedy",      "4",               "8.5000"],
    ["fichier-exemple", "HEF",         "1",               "6.0000"],
    ["fichier-exemple", "Aleatoire",   "4",               "8.5000"],
    ["moyen_test_2",    "Greedy",      "3",               "15.0000"],
    ["moyen_test_2",    "HEF",         "2",               "19.0000"],
    ["moyen_test_2",    "Aleatoire",   "10",              "58.0000"],
    ["moyen_test_3",    "Greedy",      "10",              "358.0000"],
    ["moyen_test_3",    "HEF",         "1",               "166.0000"],
    ["moyen_test_3",    "Aleatoire",   "10",              "342.0000"],
]
t_type = Table(data_type, colWidths=[4.0*cm, 3.2*cm, 3.0*cm, 3.8*cm])
t_type.setStyle(style_tableau_latex())
story.append(t_type)
story.append(Paragraph(
    "Tableau 2 - Comparaison des heuristiques avec 10 configurations demandees",
    corps_it
))

story.append(Paragraph(
    "L'aleatoire domine sur moyen_test_2 (58.0) grace a sa grande diversite (10 configs). "
    "Le greedy est meilleur sur moyen_test_3 (358.0 contre 342.0). "
    "HEF est tres deterministe : il produit 1 a 2 configs distinctes seulement, "
    "car il choisit toujours les memes capteurs a haute energie — ce qui limite fortement "
    "la qualite de la solution LP. Ces resultats suggerent qu'une <b>combinaison "
    "greedy + aleatoire</b> produit les meilleurs pools : qualite du greedy et diversite "
    "de l'aleatoire.",
    corps
))

story.append(Spacer(1, 0.2*cm))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))

story.append(Paragraph(
    "<b>Conclusion.</b> "
    "La qualite de la solution depend directement de la richesse du pool de configurations. "
    "Un pool trop petit ou trop homogene bride le programme lineaire. La strategie optimale "
    "consiste a generer au moins 10 configurations en alternant les deux heuristiques "
    "pour maximiser la diversite tout en preservant la qualite individuelle de chaque configuration.",
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
