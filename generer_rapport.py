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
    Paragraph("I.U.T. Nord Franche-Comt&#233;<br/>Techniques d'optimisation - Karine Deschinkel", entete_gauche),
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
    "Rapport : Probl&#232;me d'activation de capteurs pour la surveillance de zones",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("1  Construction des configurations &#233;l&#233;mentaires", section))

story.append(Paragraph(
    "Une <b>configuration &#233;l&#233;mentaire</b> est un ensemble minimal de capteurs couvrant "
    "toutes les zones de surveillance : aucun capteur ne peut &#234;tre retir&#233; sans laisser "
    "au moins une zone non couverte. Ces configurations constituent les variables du "
    "programme lin&#233;aire d'ordonnancement.",
    corps
))

story.append(Paragraph("Trois heuristiques ont &#233;t&#233; impl&#233;ment&#233;es :", corps))

data_h = [
    ["Heuristique", "Principe de construction", "Avantage", "R&#233;f&#233;rence"],
    ["Greedy\n(gloutonne)",
     "&#192; chaque &#233;tape, s&#233;lectionne le capteur\ncouvrant le plus grand nombre de zones\nnon encore couvertes.\nEn cas d'&#233;galit&#233;, choix al&#233;atoire.",
     "Configs de bonne\nqualit&#233; individuelle",
     "Cardei & Du\n(2005)"],
    ["HEF\n(High-Energy-\nFirst)",
     "&#192; chaque &#233;tape, s&#233;lectionne parmi les\ncapteurs utiles celui ayant la plus\ngrande dur&#233;e de vie (&#233;nergie) initiale.\nEn cas d'&#233;galit&#233;, choix al&#233;atoire.",
     "Favorise les\ncapteurs &#224; longue\ndur&#233;e de vie",
     "Manju &\nPujari\n(2011)"],
    ["Al&#233;atoire",
     "Parcourt les zones dans un ordre\nal&#233;atoire. Pour chaque zone non\ncouverte, choisit un capteur\ncouvrant cette zone au hasard.",
     "Grande diversit&#233;\ndu pool de\nconfiguration",
     "Deschinkel\n(2011)"],
]
t_h = Table(data_h, colWidths=[2.6*cm, 6.8*cm, 3.2*cm, 2.6*cm])
t_h.setStyle(style_tableau_latex())
story.append(t_h)
story.append(Spacer(1, 4))

story.append(Paragraph(
    "Dans les trois cas, la configuration construite est ensuite rendue &#233;l&#233;mentaire "
    "en testant la suppression de chaque capteur dans un ordre al&#233;atoire : si la "
    "couverture totale est maintenue apr&#232;s suppression, le capteur est retir&#233; "
    "d&#233;finitivement.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("2  Solutions obtenues sur les instances", section))

story.append(Paragraph(
    "Le programme lin&#233;aire est formul&#233; et r&#233;solu avec la biblioth&#232;que PuLP (solveur CBC). "
    "Les r&#233;sultats suivants sont obtenus avec au plus 30 configurations &#233;l&#233;mentaires "
    "g&#233;n&#233;r&#233;es par heuristique greedy (seed = 42). La borne sup&#233;rieure th&#233;orique est calcul&#233;e "
    "par upper_bound() = min<sub>z</sub> &Sigma;<sub>k couvre z</sub> T<sub>k</sub> "
    "(Manju &amp; Pujari, 2011) :",
    corps
))

data_res = [
    ["Instance", "N", "M", "Configs\ng&#233;n&#233;r&#233;es", "Borne\nsup.", "Dur&#233;e de vie\n(greedy)", "% borne", "Statut"],
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
    "L'instance fichier-exemple atteint 8.5, coh&#233;rent avec l'optimum prouv&#233; du sujet "
    "(borne sup. = 9.0). Sur les grandes instances, l'&#233;cart &#224; la borne sup&#233;rieure est "
    "consid&#233;rable (5 % pour gros_test_1, 1 % pour maxi_test_1) : le greedy seul, limit&#233; "
    "&#224; quelques configurations distinctes, ne suffit pas ; ce ph&#233;nom&#232;ne est analys&#233; en section 3.",
    corps
))

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2
# ═══════════════════════════════════════════════════════════════════════════
story.append(PageBreak())

story.append(entete_table)
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4))
story.append(Paragraph(
    "Rapport : Probl&#232;me d'activation de capteurs : Analyse des r&#233;sultats",
    titre
))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3
# ═══════════════════════════════════════════════════════════════════════════
story.append(Paragraph("3  Analyse des r&#233;sultats", section))

story.append(Paragraph(
    "Pour un m&#234;me probl&#232;me, nous examinons l'influence du <b>nombre</b> et du <b>type</b> "
    "des configurations &#233;l&#233;mentaires choisies sur la dur&#233;e de vie du r&#233;seau.",
    corps
))

# 3.1
story.append(Paragraph("3.1  Influence du nombre de configurations", sous_section))

story.append(Paragraph(
    "Le tableau suivant pr&#233;sente la dur&#233;e de vie obtenue sur moyen_test_3 (N=10, M=10, "
    "borne sup. = 463.0) en faisant varier le nombre de configurations pour les trois heuristiques :",
    corps
))

data_nb = [
    ["Heuristique \\ Nb configs", "1", "2", "3", "5", "10", "15", "20"],
    ["Greedy",       "55.0",  "127.0", "166.0", "268.5", "358.0", "358.0", "358.0"],
    ["HEF",          "166.0", "166.0", "166.0", "166.0", "166.0", "166.0", "166.0"],
    ["Al&#233;atoire","90.0",  "109.0", "163.0", "235.0", "342.0", "395.0", "395.0"],
]
col_w = [3.4*cm] + [1.44*cm]*7
t_nb = Table(data_nb, colWidths=col_w)
t_nb.setStyle(style_tableau_latex())
story.append(t_nb)
story.append(Paragraph(
    "Tableau 1 - Dur&#233;e de vie en fonction du nombre de configurations (moyen_test_3, borne = 463.0)",
    corps_it
))

story.append(Paragraph(
    "La dur&#233;e de vie augmente jusqu'&#224; un plateau (10 configs pour greedy, 15 pour al&#233;atoire). "
    "HEF stagne &#224; 166.0 quelle que soit la demande : d&#233;terministe, il ne produit qu'une "
    "configuration distincte. L'am&#233;lioration greedy 1 -&gt; 20 configs : 55.0 -&gt; 358.0 (+551 %) ; "
    "al&#233;atoire : 90.0 -&gt; 395.0 (+339 %).",
    corps
))

# 3.2
story.append(Paragraph("3.2  Influence du type d'heuristique", sous_section))

story.append(Paragraph(
    "Le tableau suivant compare les trois heuristiques (30 configurations demand&#233;es, seed=42) "
    "sur toutes les instances. Format : nb configs obtenues / dur&#233;e de vie (% borne sup.) :",
    corps
))

data_type = [
    ["Instance",        "Greedy\ncfgs / dur&#233;e (% borne)", "HEF\ncfgs / dur&#233;e (% borne)", "Al&#233;atoire\ncfgs / dur&#233;e (% borne)"],
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
    "Tableau 2 - Comparaison des trois heuristiques sur toutes les instances (30 configs demand&#233;es)",
    corps_it
))

story.append(Paragraph(
    "L'al&#233;atoire atteint 100 % de la borne sur moyen_test_2 et domine sur toutes les grandes "
    "instances. HEF ne produit que 1 &#224; 3 configs distinctes (toujours les m&#234;mes capteurs &#224; "
    "haute &#233;nergie) : il plafonne syst&#233;matiquement. Sur gros_test_1 et maxi_test_1, "
    "30 configs restent insuffisantes (28 % et 5 % de la borne), montrant les limites de "
    "l'approche &#224; grande &#233;chelle. La <b>combinaison greedy + al&#233;atoire</b> offre le meilleur "
    "compromis qualit&#233;/diversit&#233;.",
    corps
))

story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=4, spaceAfter=4))

story.append(Paragraph(
    "<b>Conclusion.</b> "
    "Sur les petites instances (N &lt; 20), 30 configs suffisent pour atteindre la borne. "
    "Sur les grandes (N = 100-1000), l'&#233;cart d&#233;passe 70 % : il faudrait un pool bien plus "
    "large. La strat&#233;gie optimale combine greedy et al&#233;atoire ; HEF seul est &#224; &#233;viter.",
    corps
))

story.append(Paragraph(
    "R&#233;f&#233;rences : Cardei &amp; Du (2005), Wireless Networks, vol. 11, pp. 333-340.  |  "
    "Manju &amp; Pujari (2011), arXiv:1103.4769.  |  Deschinkel (2011), SENSORCOMM, Nice.",
    corps_it
))

# ── Generation ───────────────────────────────────────────────────────────────
doc.build(story)
print(f"Rapport genere : {OUTPUT}")
