# -*- coding: utf-8 -*-
__title__ = "Fix Worksets"
__doc__ = """This manually assigns correct worksets to all existing elements in the project."""

# Manual Workset Assignment Script
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Transaction,
    FilteredElementCollector,
)

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# Workset mapping based on Assembly Code
WORKSET_MAPPING = {
    # Grids and Levels
    # Ground Facilites (Bodemvoorzieningen)
    # "11":,	    # Bodemvoorzieningen	2	-2001340
    # "11.00":,	# bodemvoorzieningen; algemeen 	3	-2001340
    # "11.10":,	# bodemvoorzieningen - grond, algemeen (verzamelniveau)	4	-2001340
    # "11.11":,   # bodemvoorzieningen - grond, ontgravingen	4	-2001340
    # "11.12":,   # bodemvoorzieningen - grond, aanvullingen	4	-2001340
    # "11.13":,	# bodemvoorzieningen - grond, sloop- en rooiwerkzaamheden	4	-2001340
    # "11.15":,	# bodemvoorzieningen, grond, damwanden	4	-2001340
    # "11.20":,	# bodemvoorzieningen - water, algemeen (verzamelniveau)	4	-2001340
    # "11.24":,	# bodemvoorzieningen - water, bemalingen	4	-2001340
    # "11.25":,	# bodemvoorzieningen - water, damwanden	4	-2001340
    # Foundation Floors (Vloeren op grondlag)
    "13": 1161,  # Vloeren op grondslag	2	-2000032
    "13.10": 1161,  # vloeren op grondslag - niet constructief, algemeen (verzamelniveau)	4	-2000032
    "13.00": 1161,  # vloeren op grondslag; algemeen	3	-2000032
    "13.11": 1161,  # vloeren op grondslag - niet constructief, bodemafsluitingen	4	-2000032
    "13.12": 1161,  # vloeren op grondslag - niet constructief, vloeren als gebouwonderdeel	4	-2000032
    "13.13": 1161,  # vloeren op grondslag - niet constructief, vloeren als bestrating	4	-2000032
    "13.20": 1161,  # vloeren op grondslag - constructief, algemeen (verzamelniveau)	4	-2000032
    "13.21": 1161,  # vloeren op grondslag - constructief, bodemafsluitingen	4	-2000032
    "13.22": 1161,  # vloeren op grondslag - constructief, vloeren als gebouwonderdeel	4	-2000032
    "13.25": 1161,  # vloeren op grondslag - constructief, grondverbeteringen	4	-2000032
    # Foundation Structures (Funderingsconstructies)
    "16": 1161,  # Funderingsconstructies	2	-2001300
    "16.00": 1161,  # funderingsconstructies; algemeen	3	-2001300
    "16.10": 1161,  # funderingsconstructies - voeten en balken, algemeen (verzamelniveau)	4	-2001300
    "16.11": 1161,  # funderingsconstructies - voeten en balken, fundatie voeten	4	-2001300
    "16.12": 1161,  # funderingsconstructies - voeten en balken, fundatie balken	4	-2001300
    "16.13": 1161,  # funderingsconstructies - voeten en balken, fundatie poeren	4	-2001300
    "16.14": 1161,  # funderingsconstructies - voeten en balken, gevelwanden (-200)	4	-2001300
    "16.15": 1161,  # funderingsconstructies - voeten en balken, grondverbeteringen	4	-2001300
    "16.20": 1161,  # funderingsconstructies - keerwanden, algemeen (verzamelniveau)	4	-2001300
    "16.21": 1161,  # funderingsconstructies - keerwanden, grondkerende wanden	4	-2001300
    "16.22": 1161,  # funderingsconstructies - keerwanden, waterkerende wanden	4	-2001300
    "16.23": 1161,  # funderingsconstructies - keerwanden, gevelwanden (-200)	4	-2001300
    "16.25": 1161,  # funderingsconstructies - keerwanden, grondverbeteringen	4	-2001300
    # Foundation Piles (PaalFundering)
    "17": 1160,  # Paalfunderingen	2	-2001300
    "17.00": 1160,  # paalfunderingen; algemeen	3	-2001300
    "17.10": 1160,  # paalfunderingen - niet geheid, algemeen (verzamelniveau)	4	-2001300
    "17.11": 1160,  # paalfunderingen - niet geheid, dragend palen - geboord	4	-2001300
    "17.12": 1160,  # paalfunderingen - niet geheid, dragende palen - geschroefd	4	-2001300
    "17.13": 1160,  # paalfunderingen - niet geheid, trekverankeringen	4	-2001300
    "17.14": 1160,  # paalfunderingen - niet geheid, pijler-putring funderingen	4	-2001300
    "17.15": 1160,  # paalfunderingen - niet geheid, bodeminjecties	4	-2001300
    "17.20": 1160,  # paalfunderingen - geheid, algemeen (verzamelniveau)	4	-2001300
    "17.21": 1160,  # paalfunderingen - geheid, dragende palen	4	-2001300
    "17.22": 1160,  # paalfunderingen - geheid, palen - ingeheide bekisting	4	-2001300
    "17.23": 1160,  # paalfunderingen - geheid, trekverankeringen	4	-2001300
    "17.25": 1160,  # paalfunderingen - geheid, damwanden funderingen	4	-2001300
    # Walls Exterior (Buitenwanden)
    "21": 1164,  # Buitenwanden	2	-2000011
    "21.00": 1164,  # buitenwanden; algemeen 	3	-2000011
    "21.10": 1164,  # buitenwanden - niet constructief, algemeen (verzamelniveau)	4	-2000011
    "21.11": 1164,  # buitenwanden - niet constructief, massieve wanden	4	-2000011
    "21.12": 1164,  # buitenwanden - niet constructief, spouwwanden	4	-2000011
    "21.13": 1164,  # buitenwanden - niet constructief, systeemwanden	4	-2000011
    "21.14": 1164,  # buitenwanden - niet constructief, vlieswanden	4	-2000011
    "21.15": 1164,  # buitenwanden - niet constructief, borstweringen	4	-2000011
    "21.16": 1164,  # buitenwanden - niet constructief, boeiboorden	4	-2000011
    "21.20": 1164,  # buitenwanden - constructief, algemeen (verzamelniveau)	4	-2000011
    "21.21": 1164,  # buitenwanden - constructief, massieve wanden	4	-2000011
    "21.22": 1164,  # buitenwanden - constructief, spouwwanden	4	-2000011
    "21.23": 1164,  # buitenwanden - constructief, systeemwanden	4	-2000011
    "21.25": 1164,  # buitenwanden - constructief, borstweringen	4	-2000011
    # Walls Interior (Binnenwanden)
    "22": 1165,  # Binnenwanden 2    -2000011
    "22.00": 1165,  # binnenwanden; algemeen 	3	-2000011
    "22.10": 1165,  # binnenwanden - niet constructief, algemeen (verzamelniveau)	4	-2000011
    "22.11": 1165,  # binnenwanden - niet constructief, massieve wanden	4	-2000011
    "22.12": 1165,  # binnenwanden - niet constructief, spouwwanden	4	-2000011
    "22.13": 1165,  # binnenwanden - niet constructief, systeemwanden - vast	4	-2000011
    "22.14": 1165,  # binnenwanden - niet constructief, systeemwanden - verplaatsbaar	4	-2000011
    "22.20": 1165,  # binnenwanden - constructief, algemeen (verzamelniveau)	4	-2000011
    "22.21": 1165,  # binnenwanden - constructief, massieve wanden	4	-2000011
    "22.22": 1165,  # binnenwanden - constructief, spouwwanden	4	-2000011
    "22.23": 1165,  # binnenwanden - constructief, systeemwanden - vast	4	-2000011
    # Floors (Vloeren)
    "23": 1162,  # Vloeren 2	    -2000032
    "23.00": 1162,  # vloeren; algemeen 	3	-2000032
    "23.10": 1162,  # vloeren - niet constructief 	4	-2000032
    # "23.10": 1162,  # vloeren - niet constructief, algemeen (verzamelniveau)	4	-2000032
    "23.11": 1162,  # vloeren - niet constructief, vrijdragende Vloeren	4	-2000032
    "23.12": 1162,  # vloeren - niet constructief, balkons	4	-2000032
    "23.13": 1162,  # vloeren - niet constructief, galerijen	4	-2000032
    "23.14": 1162,  # vloeren - niet constructief, bordessen	4	-2000032
    "23.15": 1162,  # vloeren - niet constructief, vloeren t.b.v. technische voorziengen	4	-2000032
    "23.20": 1162,  # vloeren - constructief, algemeen (verzamelniveau)	4	-2000032
    "23.21": 1162,  # vloeren - constructief, vrijdragende vloeren	4	-2000032
    "23.22": 1162,  # vloeren - constructief, balkons	4	-2000032
    "23.23": 1162,  # vloeren - constructief, galerijen	4	-2000032
    "23.24": 1162,  # vloeren - constructief, bordessen	4	-2000032
    "23.25": 1162,  # vloeren - constructief, vloeren t.b.v. technische voorziengen	4	-2000032
    # "13": 1162,
    # "23": 1162,
    # "43": 1162,
    # "16_NCG_betonpoer": 1160,
    # "16_NCG_kalkzandsteen steip": 1160,
    # "16_NCG_metselwerk stiep": 1160,
    # "17_NCG_funderingspaal_prefab beton_vierkant": 1160,
    # "17.10": 1160,
    # "B1A(17.21)": 1160,
    # Stairs and Slopes (Trappen en Hellingen)
    # "24":,	# Trappen en hellingen	2	-2000120
    # "24.00":,   # trappen en hellingen; algemeen 	3	-2000120
    # "24.10":,   # trappen en hellingen - trappen, algemeen (verzamelniveau)	4	-2000120
    # "24.11":,   # trappen en hellingen - trappen, rechte steektrappen	4	-2000120
    # "24.12":,   # trappen en hellingen - trappen, niet rechte steektrappen	4	-2000120
    # "24.13":,   # trappen en hellingen - trappen, spiltrappen	4	-2000120
    # "24.15":,   # trappen en hellingen - trappen, bordessen	4	-2000120
    # "24.20":,   # trappen en hellingen - hellingen, algemeen (verzamelniveau)	4	-2000180
    # "24.21":,   # trappen en hellingen - hellingen, beloopbare hellingen	4	-2000180
    # "24.22":,   # trappen en hellingen - hellingen, berijdbare hellingen	4	-2000180
    # "24.25":,   # trappen en hellingen - hellingen, bordessen	4	-2000180
    # "24.30":,   # trappen en hellingen - ladders en klimijzers, algemeen (verzamelniveau)	4	-2000120
    # "24.31":,   # trappen en hellingen - ladders en klimijzers, ladders	4	-2000120
    # "24.32":,   # trappen en hellingen - ladders en klimijzers, klimijzers	4	-2001340
    # "24.35":,   # trappen en hellingen - ladders en klimijzers, bordessen	4	-2000120
    # Roof (Dakbeschot)(Dakliggers)
    "27": 1167,  # Daken	2	-2000035
    "27.00": 1167,  # daken; algemeen	3	-2000035
    "27.10": 1167,  # daken - niet constructief, algemeen (verzamelniveau)	4	-2000035
    "27.11": 1167,  # daken - niet constructief, vlakke daken	4	-2000035
    "27.12": 1167,  # daken - niet constructief, hellende daken	4	-2000035
    "27.13": 1167,  # daken - niet constructief, luifels	4	-2000035
    "27.14": 1167,  # daken - niet constructief, overkappingen	4	-2000035
    "27.16": 1167,  # daken - niet constructief, gootconstructies	4	-2000035
    "27.20": 1166,  # daken - constructief, algemeen (verzamelniveau)	4	-2000035
    "27.21": 1166,  # daken - constructief, vlakke daken	4	-2000035
    "27.22": 1166,  # daken - constructief, hellende daken	4	-2000035
    "27.23": 1166,  # daken - constructief, luifels	4	-2000035
    "27.24": 1166,  # daken - constructief, overkappingen	4	-2000035
    "27.26": 1166,  # daken - constructief, gootconstructies	4	-2000035
    # Primary Load-Bearing Structures (Hoofddraagconstructies)
    "28": 4791,  # Hoofddraagconstructies	2	-2001320
    "28.00": 4791,  # hoofddraagconstructies; algemeen	3	-2001320
    "28.10": 4791,  # hoofddraagconstructies - kolommen en liggers, algemeen (verzamelniveau)	4	-2001320
    "28.11": 4791,  # hoofddraagconstructies - kolommen en liggers, kolom-/liggerconstructies	4	-2001320
    "28.12": 4791,  # hoofddraagconstructies - kolommen en liggers, spanten	4	-2001320
    "28.20": 4791,  # hoofddraagconstructies - wanden en vloeren, algemeen (verzamelniveau)	4	-2000011
    "28.21": 4791,  # hoofddraagconstructies - wanden en vloeren, wand-/vloerconstructies	4	-2000011
    "28.30": 4791,  # hoofddraagconstructies - ruimte-eenheden, algemeen (verzamelniveau)	4	-2001320
    "28.31": 4791,  # hoofddraagconstructies - ruimte-eenheden, doosconstructies	4	-2001320
    # Finishing (AFBOUW)
    # "3":,	# AFBOUW	1	-2000151
    # Exterior Wall Openings (Buitenwanopeningen)
    "31": 1174,  # Buitenwandopeningen	2	-2000011
    "31.00": 1174,  # buitenwandopeningen; algemeen 	3	-2000011
    "31.10": 1174,  # buitenwandopeningen - niet gevuld, algemeen (verzamelniveau)	4	-2000011
    "31.11": 1174,  # buitenwandopeningen - niet gevuld, daglichtopeningen	4	-2000011
    "31.12": 1174,  # buitenwandopeningen - niet gevuld, buitenluchtopeningen	4	-2000011
    "31.20": 1174,  # buitenwandopeningen - gevuld met ramen, algemeen (verzamelniveau)	4	-2000014
    "31.21": 1174,  # buitenwandopeningen - gevuld met ramen, gesloten ramen	4	-2000014
    "31.22": 1174,  # buitenwandopeningen - gevuld met ramen, ramen draaiend aan een kant	4	-2000014
    "31.23": 1174,  # buitenwandopeningen - gevuld met ramen, schuiframen	4	-2000014
    "31.24": 1174,  # buitenwandopeningen - gevuld met ramen, ramen draaiend op verticale of horizontale as	4	-2000014
    "31.25": 1174,  # buitenwandopeningen - gevuld met ramen, combinatieramen	4	-2000014
    "31.30": 1174,  # buitenwandopeningen - gevuld met deuren, algemeen (verzamelniveau)	4	-2000023
    "31.31": 1174,  # buitenwandopeningen - gevuld met deuren, draaideuren	4	-2000023
    "31.32": 1174,  # buitenwandopeningen - gevuld met deuren, schuifdeuren	4	-2000023
    "31.33": 1174,  # buitenwandopeningen - gevuld met deuren, tuimeldeuren	4	-2000023
    "31.34": 1174,  # buitenwandopeningen - gevuld met deuren, tourniqets	4	-2000023
    "31.40": 1174,  # buitenwandopeningen - gevuld met puien, algemeen (verzamelniveau)	4	-2000014
    "31.41": 1174,  # buitenwandopeningen - gevuld met puien, gesloten puien	4	-2000014
    # Interior Wall Openings (Binnenwandopeningen)
    "32": 3447,  # 	Binnenwandopeningen	2	-2000011
    "32.00": 3447,  # binnenwandopeningen; algemeen 	3	-2000011
    "32.10": 3447,  # binnenwandopeningen - niet gevuld, algemeen (verzamelniveau)	4	-2000011
    "32.11": 3447,  # binnenwandopeningen - niet gevuld, openingen als doorgang	4	-2000011
    "32.12": 3447,  # binnenwandopeningen - niet gevuld, openingen als doorzicht	4	-2000011
    "32.20": 3447,  # binnenwandopeningen - gevuld met ramen, algemeen (verzamelniveau)	4	-2000014
    "32.21": 3447,  # binnenwandopeningen - gevuld met ramen, gesloten ramen	4	-2000014
    "32.22": 3447,  # binnenwandopeningen - gevuld met ramen, ramen draaiend aan een kant	4	-2000014
    "32.23": 3447,  # binnenwandopeningen - gevuld met ramen, schuiframen	4	-2000014
    "32.24": 3447,  # binnenwandopeningen - gevuld met ramen, ramen draaiend op verticale of horizontale as	4	-2000014
    "32.25": 3447,  # binnenwandopeningen - gevuld met ramen, combinatieramen	4	-2000014
    "32.30": 3447,  # binnenwandopeningen - gevuld met deuren, algemeen (verzamelniveau)	4	-2000023
    "32.31": 3447,  # binnenwandopeningen - gevuld met deuren, draaideuren	4	-2000023
    "32.32": 3447,  # binnenwandopeningen - gevuld met deuren, schuifdeuren	4	-2000023
    "32.33": 3447,  # binnenwandopeningen - gevuld met deuren, tuimeldeuren	4	-2000023
    "32.34": 3447,  # binnenwandopeningen - gevuld met deuren, tourniqets	4	-2000023
    "32.40": 3447,  # binnenwandopeningen - gevuld met puien, algemeen (verzamelniveau)	4	-2000011
    "32.41": 3447,  # binnenwandopeningen - gevuld met puien, gesloten puien	4	-2000011
    # Floor Openings (Vloeropeningen)
    # "33":,	# Vloeropeningen	2	-2000032
    # "33.00":,	# vloeropeningen; algemeen 	3	-2000032
    # "33.10":,	# vloeropeningen - niet gevuld, algemeen (verzamelniveau)	4	-2000032
    # "33.11":,	# vloeropeningen - niet gevuld, openingen als doorgang	4	-2000032
    # "33.12":,	# vloeropeningen - niet gevuld, openingen als doorzicht	4	-2000032
    # "33.20":,	# vloeropeningen - gevuld, algemeen (verzamelniveau)	4	-2000032
    # "33.21":,	# vloeropeningen - gevuld, beloopbare vullingen	4	-2000032
    # "33.22":,	# vloeropeningen - gevuld, niet-beloopbare vullingen	4	-2000032
    # Balustrades and Railings (Balustrades en Leuningen)
    # "34":,	# Balustrades en leuningen	2	-2000126
    # "34.00":,	# balustrades en leuningen; algemeen 	3	-2000126
    # "34.10":,	# balustrades en leuningen - balustrades, algemeen (verzamelniveau)	4	-2000126
    # "34.11":3447,	# balustrades en leuningen - balustrades, binnenbalustrades	4	-2000126
    # "34.12":1174,	# balustrades en leuningen - balustrades, buitenbalustrades	4	-2000126
    # "34.20":,	# balustrades en leuningen - leuningen, algemeen (verzamelniveau)	4	-2000126
    # "34.21":3447,	# balustrades en leuningen - leuningen, binnenleuningen	4	-2000126
    # "34.22":1174,	# balustrades en leuningen - leuningen, buitenleuningen	4	-2000126
    # Roof Openings (Dak Openingen)
    "37": 1174,  # 	Dakopeningen	2	-2000035
    "37.00": 1174,  # dakopeningen; algemeen 	3	-2000035
    "37.10": 1174,  # dakopeningen - niet gevuld, algemeen (verzamelniveau)	4	-2000035
    "37.11": 1174,  # dakopeningen - niet gevuld, daglichtopeningen	4	-2000035
    "37.12": 1174,  # dakopeningen - niet gevuld, buitenluchtopeningen	4	-2000035
    "37.20": 1174,  # dakopeningen - gevuld, algemeen (verzamelniveau)	4	-2000014
    "37.21": 1174,  # dakopeningen - gevuld, gesloten ramen	4	-2000014
    "37.22": 1174,  # dakopeningen - gevuld, ramen draaiend aan één kant	4	-2000014
    "37.23": 1174,  # dakopeningen - gevuld, schuiframen	4	-2000014
    "37.24": 1174,  # dakopeningen - gevuld, ramen draaiend op een as	4	-2000014
    "37.25": 1174,  # dakopeningen - gevuld, combinatieramen	4	-2000014
    # Built_in Packages (Inbouwpakketten)
    # "38":,	# Inbouwpakketten	2	-2000151
    # "38.00":,	# inbouwpakketten; algemeen	3	-2000151
    # "38.10":,	# inbouwpakketten - algemeen (verzamelniveau)	4	-2000151
    # "38.11":,	# inbouwpakketten - inbouwpakketten met te openen delen	4	-2000151
    # "38.12":,	# inbouwpakketten - inbouwpakketten met gesloten delen	4	-2000151
    # Exterior Wall Finishes (Buitenwandafwerkingen)
    # "4":, #-	AFWERKINGEN	1	-2000151
    "41": 1174,  # 	Buitenwandafwerkingen	2	-2000011
    "41.00": 1174,  # buitenwandafwerkingen; algemeen 	3	-2000011
    "41.10": 1174,  # buitenwandafwerkingen - algemeen (verzamelniveau)	4	-2000011
    "41.11": 1174,  # buitenwandafwerkingen - afwerklagen 	4	-2000011
    "41.12": 1174,  # buitenwandafwerkingen - bekledingen 	4	-2000011
    "41.13": 1174,  # buitenwandafwerkingen - voorzetwanden	4	-2000011
    # Interior Wall Finishes (Binnenwandafwerkingen)
    "42": 3447,  # 	Binnenwandafwerkingen	2	-2000011
    "42.00": 3447,  # binnenwandafwerkingen; algemeen	3	-2000011
    "42.10": 3447,  # binnenwandafwerkingen - algemeen (verzamelniveau)	4	-2000011
    "42.11": 3447,  # binnenwandafwerkingen - afwerklagen	4	-2000011
    "42.12": 3447,  # binnenwandafwerkingen - bekledingen	4	-2000011
    # Floor Finishes (Vloerafwerkingen)
    "43": 1162,  # 	Vloerafwerkingen	2	-2000032
    "43.00": 1162,  # vloerafwerkingen; algemeen 	3	-2000032
    "43.10": 1162,  # vloerafwerkingen - verhoogd, algemeen (verzamelniveau) 	4	-2000032
    "43.11": 1162,  # vloerafwerkingen - verhoogd, podiums	4	-2000032
    "43.12": 1162,  # vloerafwerkingen - verhoogd, installatievloeren	4	-2000032
    "43.20": 1162,  # vloerafwerkingen - niet verhoogd, algemeen (verzamelniveau)	4	-2000032
    "43.21": 1162,  # vloerafwerkingen - niet verhoogd, afwerklagen	4	-2000032
    "43.22": 1162,  # vloerafwerkingen - niet verhoogd, bekledingen	4	-2000032
    "43.23": 1162,  # vloerafwerkingen - niet verhoogd, systeemvloerafwerkingen	4	-2000032
    # Stair and Ramp Finishes (Trap- en Hellingafwekingen)
    # "44":,	# Trap- en hellingafwerkingen	2	-2000120
    # "44.00:,	# trap- en hellingafwerkingen; algemeen 	3	-2000120
    # "44.10:,	# trap- en hellingafwerkingen - trapafwerkingen, algemeen (verzamelniveau)	4	-2000120
    # "44.11:,	# trap- en hellingafwerkingen - trapafwerkingen, afwerklagen	4	-2000120
    # "44.12:,	# trap- en hellingafwerkingen - trapafwerkingen, bekledingen	4	-2000120
    # "44.13:,	# trap- en hellingafwerkingen - trapafwerkingen, systeemafwerkingen	4	-2000120
    # "44.20:,	# trap- en hellingafwerkingen - hellingafwerkingen, algemeen (verzamelniveau)	4	-2000120
    # "44.21:,	# trap- en hellingafwerkingen - hellingafwerkingen, afwerklagen	4	-2000120
    # "44.22:,	# trap- en hellingafwerkingen - hellingafwerkingen, bekledingen	4	-2000120
    # "44.23:,	# trap- en hellingafwerkingen - hellingafwerkingen, systeemafwerkingen	4	-2000120
    # Ceiling Finishes (Plafondafwerkingen)
    # "45":,	# Plafondafwerkingen	2	-2000038
    # "45.00":,	# plafondafwerkingen; algemeen 	3	-2000038
    # "45.10":,	# plafondafwerkingen - verlaagd, algemeen (verzamelniveau)	4	-2000038
    # "45.11":,	# plafondafwerkingen - verlaagd, verlaagde plafonds	4	-2000038
    # "45.12":,	# plafondafwerkingen - verlaagd, systeem plafonds	4	-2000038
    # "45.14":,	# plafondafwerkingen - verlaagd, koofconstructies	4	-2000038
    # "45.15":,	# plafondafwerkingen - verlaagd, gordijnplanken	4	-2000038
    # "45.20":,	# plafondafwerkingen - niet verlaagd, algemeen (verzamelniveau)	4	-2000038
    # "45.21":,	# plafondafwerkingen - niet verlaagd, afwerkingen	4	-2000038
    # "45.22":,	# plafondafwerkingen - niet verlaagd, bekledingen	4	-2000038
    # "45.23":,	# plafondafwerkingen - niet verlaagd, systeemafwerkingen	4	-2000038
    # "45.24":,	# plafondafwerkingen - niet verlaagd, koofconstructies	4	-2000038
    # "45.25":,	# plafondafwerkingen - niet verlaagd, gordijnplanken	4	-2000038
    # Roof Finishes (Dakafwerkingen)
    "47": 1167,  # 	Dakafwerkingen	2	-2000035
    "47.00": 1167,  # dakafwerkingen; algemeen 	3	-2000035
    "47.10": 1167,  # dakafwerkingen - afwerkingen, algemeen (verzamelniveau)	4	-2000035
    "47.11": 1167,  # dakafwerkingen - afwerkingen, vlakke dakafwerkingen	4	-2000035
    "47.12": 1167,  # dakafwerkingen - afwerkingen, hellende dakafwerkingen	4	-2000035
    "47.13": 1167,  # dakafwerkingen - afwerkingen, luifel afwerkingen	4	-2000035
    "47.14": 1167,  # dakafwerkingen - afwerkingen, overkappings afwerkingen	4	-2000035
    "47.15": 1167,  # dakafwerkingen - afwerkingen, beloopbare dakafwerkingen	4	-2000035
    "47.16": 1167,  # dakafwerkingen - afwerkingen, berijdbare dakafwerkingen	4	-2000035
    "47.20": 1167,  # dakafwerkingen - bekledingen, algemeen (verzamelniveau)	4	-2000035
    "47.21": 1167,  # dakafwerkingen - bekledingen, vlakke bekledingen	4	-2000035
    "47.22": 1167,  # dakafwerkingen - bekledingen, hellende bekledingen	4	-2000035
    "47.23": 1167,  # dakafwerkingen - bekledingen, luifel bekledingen	4	-2000035
    "47.24": 1167,  # dakafwerkingen - bekledingen, overkappings bekledingen	4	-2000035
    "47.25": 1167,  # dakafwerkingen - bekledingen, beloopbare bekledingen	4	-2000035
    "47.26": 1167,  # dakafwerkingen - bekledingen, berijdbare bekledingen	4	-2000035
    # Finishing Packages (Afwerkingspakketten)
    # "48":,	# Afwerkingspakketten	2	-2000035
    # "48.00":,	# afwerkingspakketten; algemeen 	3	-2000035
    # "48.10":,	# afwerkingspakketten - algemeen (verzamelniveau)	4	-2000035
    # "48.11":,	# afwerkingspakketten - naadloze afwerkingen	4	-2000035
    # "48.12":,	# afwerkingspakketten - overige afwerkingen	4	-2000035
    # Mechanical Installations (Werktuigbouwkundig)
    # "5":,#-	INSTALLATIES WERKTUIGBOUWKUNDIG	1	-2000151
    # "51":,	# Warmteopwekking	2	-2001140
    # "51.00":,	# warmteopwekking; algemeen 	3	-2001140
    # "51.10":,	# warmteopwekking - lokaal, algemeen (verzamelniveau)	4	-2001140
    # "51.11":,	# warmteopwekking - lokaal, gasvormige brandstoffen	4	-2001140
    # "51.12":,	# warmteopwekking - lokaal, vloeibare brandstoffen	4	-2001140
    # "51.13":,	# warmteopwekking - lokaal, vaste brandstoffen	4	-2001140
    # "51.14":,	# warmteopwekking - lokaal, schoorstenen/kanalen (niet bouwkundig)	4	-2001140
    # "51.16":,	# warmteopwekking - lokaal, gecombineerde tapwater verwarming	4	-2001140
    # "51.19":,	# warmteopwekking - lokaal, brandstoffenopslag	4	-2001140
    # "51.20":,	# warmteopwekking - centraal, algemeen (verzamelniveau)	4	-2001140
    # "51.21":,	# warmteopwekking - centraal, gasvormige brandstoffen	4	-2001140
    # "51.22":,	# warmteopwekking - centraal, vloeibare brandstoffen	4	-2001140
    # "51.23":,	# warmteopwekking - centraal, vaste brandstoffen	4	-2001140
    # "51.24":,	# warmteopwekking - centraal, schoorstenen/kanalen (niet bouwkundig)	4	-2001140
    # "51.26":,	# warmteopwekking - centraal, gecombineerde tapwater verwarming	4	-2001140
    # "51.29":,	# warmteopwekking - centraal, brandstoffenopslag	4	-2001140
    # "51.30":,	# warmteopwekking - toegeleverde warmte, algemeen (verzamelniveau)	4	-2001140
    # "51.31":,	# warmteopwekking - toegeleverde warmte, water tot 140° C.	4	-2001140
    # "51.32":,	# warmteopwekking - toegeleverde warmte, water boven 140° C.	4	-2001140
    # "51.33":,	# warmteopwekking - toegeleverde warmte, stoom	4	-2001140
    # "51.36":,	# warmteopwekking - toegeleverde warmte, gecombineerde tapwaterverwarming	4	-2001140
    # "51.40":,	# warmteopwekking - warmte-krachtkoppeling, algemeen (verzamelniveau)	4	-2001140
    # "51.41":,	# warmteopwekking - warmte-krachtkoppeling, total-energy	4	-2001140
    # "51.44":,	# warmteopwekking - warmte-krachtkoppeling, schoorstenen/kanalen (niet bouwkundig)	4	-2001140
    # "51.46":,	# warmteopwekking - warmte-krachtkoppeling, gecombineerde tapwater verwarming	4	-2001140
    # "51.49":,	# warmteopwekking - warmte-krachtkoppeling, brandstoffenopslag	4	-2001140
    # "51.50":,	# warmteopwekking - bijzonder, algemeen (verzamelniveau)	4	-2001140
    # "51.51":,	# warmteopwekking - bijzonder, warmtepomp	4	-2001140
    # "51.52":,	warmteopwekking - bijzonder, zonnecollectoren	4	-2001140
    # "51.53":,	warmteopwekking - bijzonder, accumulatie	4	-2001140
    # "51.54":,	warmteopwekking - bijzonder, aardwarmte	4	-2001140
    # "51.55":,	warmteopwekking - bijzonder, kernenergie	4	-2001160
    # Mechanical Installations
    # "52":,	# Drainage (Afvoeren)	2	-2001160
    # "52.00":,	# afvoeren; algemeen	3	-2001160
    # "52.10":,	# afvoeren - regenwater, algemeen (verzamelniveau)	4	-2001160
    # "52.11":,	# afvoeren - regenwater, afvoerinstallatie - in het gebouw	4	-2001160
    # "52.12":,	# afvoeren - regenwater, afvoerinstallatie - buiten het gebouw	4	-2001160
    # "52.16":,	# afvoeren - regenwater, pompsysteem	4	-2001160
    # "52.20":,	# afvoeren - faecaliën, algemeen (verzamelniveau)	4	-2001160
    # "52.21":,	# afvoeren - faecaliën, standaard systeem /	4	-2001160
    # "52.22":,	# afvoeren - faecaliën, vacuümsysteem	4	-2001160
    # "52.23":,	# afvoeren - faecaliën, overdruksysteem	4	-2001160
    # "52.26":,	# afvoeren - faecaliën, pompsysteem	4	-2001160
    # "52.30":,	# afvoeren - afvalwater, algemeen (verzamelniveau)	4	-2001160
    # "52.31":,	# afvoeren - afvalwater, huishoudelijk afval	4	-2001160
    # "52.32":,	# afvoeren - afvalwater, bedrijfsafval	4	-2001160
    # "52.36":,	# afvoeren - afvalwater, pompsysteem	4	-2001160
    # "52.40":,	# afvoeren - gecombineerd, algemeen (verzamelniveau) 	4	-2001160
    # "52.41":,	# afvoeren - gecombineerd, geïntegreerd systeem 	4	-2001160
    # "52.46":,	# afvoeren - gecombineerd, pompsysteem	4	-2001160
    # "52.50":,	# afvoeren - speciaal, algemeen (verzamelniveau) 	4	-2001160
    # "52.51":,	# afvoeren - speciaal, chemisch verontreinigd afvalwater 	4	-2001160
    # "52.52":,	# afvoeren - speciaal, biologisch besmet afvalwater 	4	-2001160
    # "52.53":,	# afvoeren - speciaal, radio-actief besmet afvalwater 	4	-2001160
    # "52.56":,	# afvoeren - speciaal, pompsysteem	4	-2001160
    # "52.60":,	# afvoeren - vast vuil, algemeen (verzamelniveau)	4	-2001160
    # "52.61":,	# afvoeren - vast vuil, stortkokers 	4	-2001160
    # "52.62":,	# afvoeren - vast vuil, vacuümsysteem 	4	-2001160
    # "52.63":,	# afvoeren - vast vuil, persluchtsysteem 	4	-2001160
    # "52.64":,	# afvoeren - vast vuil, verdichtingssysteem 	4	-2001160
    # "52.65":,	# afvoeren - vast vuil, verbrandingssysteem	4	-2001160
    # Water
    # "53":,	# Water	2	-2001160
    # "53.00":,	# water; algemeen	3	-2001160
    # "53.10":,	# water - drinkwater, algemeen (verzamelniveau) 	4	-2001160
    # "53.11":,	# water - drinkwater, netaansluiting 	4	-2001160
    # "53.12":,	# water - drinkwater, bronaansluiting 	4	-2001160
    # "53.13":,	# water - drinkwater, reinwaterkelderaansluiting 	4	-2001160
    # "53.14":,	# water - drinkwater, drukverhoging 	4	-2001160
    # "53.19":,	# water - drinkwater, opslagtanks	4	-2001160
    # "53.20":,	# water - verwarmd tapwater, algemeen (verzamelniveau) 	4	-2001160
    # "53.21":,	# water - verwarmd tapwater, direct verwarmd met voorraad 	4	-2001160
    # "53.22":,	# water - verwarmd tapwater, indirect verwarmd met voorraad 	4	-2001160
    # "53.23":,	# water - verwarmd tapwater, doorstroom - direct verwarmd 	4	-2001160
    # "53.24":,	# water - verwarmd tapwater, doorstroom - indirect verwarmd	4	-2001160
    # "53.30":,	# water - bedrijfswater, algemeen (verzamelniveau) 	4	-2001160
    # "53.31":,	# water - bedrijfswater, onthard-watersysteem 	4	-2001160
    # "53.32":,	# water - bedrijfswater, demi-watersysteem 	4	-2001160
    # "53.33":,	# water - bedrijfswater, gedistileerd-watersysteem 	4	-2001160
    # "53.34":,	# water - bedrijfswater, zwembad-watersysteem	4	-2001160
    # "53.40":,	# water - gebruiksstoom en condens, algemeen (verzamelniveau) 	4	-2001160
    # "53.41":,	# water - gebruiksstoom en condens, lage-druk stoomsysteem 	4	-2001160
    # "53.42":,	# water - gebruiksstoom en condens, hoge -ruk stoomsysteem 	4	-2001160
    # "53.44":,	# water - gebruiksstoom en condens, condensverzamelsysteem	4	-2001160
    # "53.50":,	# water - waterbehandeling, algemeen (verzamelniveau) 	4	-2001160
    # "53.51":,	# water - waterbehandeling, filtratiesysteem 	4	-2001160
    # "53.52":,	# water - waterbehandeling, absorptiesysteem 	4	-2001160
    # "53.53":,	# water - waterbehandeling, ontgassingssysteem 	4	-2001160
    # "53.54":,	water - waterbehandeling, destillatiesysteem	4	-2001160
    # Gas System
    # "54":,	# Gassen	2	-2001160
    # "54.00":,	# gassen; algemeen	3	-2001160
    # "54.10":,	# gassen - brandstof, algemeen (verzamelniveau) 	4	-2001160
    # "54.11":,	# gassen - brandstof, aardgasvoorziening 	4	-2001160
    # "54.12":,	# gassen - brandstof, butaanvoorziening 	4	-2001160
    # "54.13":,	# gassen - brandstof, propaanvoorziening 	4	-2001160
    # "54.14":,	# gassen - brandstof, LPG-voorziening	4	-2001160
    # "54.20":,	# gassen - perslucht en vacuüm, algemeen (verzamelniveau) 	4	-2001160
    # "54.21":,	# gassen - perslucht en vacuüm, persluchtvoorziening 	4	-2001160
    # "54.22":,	# gassen - perslucht en vacuüm, vacuümvoorziening	4	-2001160
    # "54.30":,	# gassen - medisch, algemeen (verzamelniveau) 	4	-2001160
    # "54.31":,	# gassen - medisch, zuurstofvoorziening 	4	-2001160
    # "54.32":,	# gassen - medisch, carbogeenvoorziening 	4	-2001160
    # "54.33":,	# gassen - medisch, lachgasvoorziening 	4	-2001160
    # "54.34":,	# gassen - medisch, koolzuurvoorziening 	4	-2001160
    # "54.35":,	# gassen - medisch, medische luchtvoorziening	4	-2001160
    # "54.40":,	# gassen - technisch, algemeen (verzamelniveau) 	4	-2001160
    # "54.41":,	# gassen - technisch, stikstofvoorziening 	4	-2001160
    # "54.42":,	# gassen - technisch, waterstofvoorziening 	4	-2001160
    # "54.43":,	# gassen - technisch, argonvoorziening 	4	-2001160
    # "54.44":,	# gassen - technisch, heliumvoorziening 	4	-2001160
    # "54.45":,	# gassen - technisch, acyteleenvoorziening 	4	-2001160
    # "54.46":,	# gassen - technisch, propaanvoorziening 	4	-2001160
    # "54.47":,	# gassen - technisch, koolzuurvoorziening	4	-2001160
    # "54.50":,	# gassen - bijzonder, algemeen (verzamelniveau) 	4	-2001160
    # "54.51":,	# gassen - bijzonder, voorziening - zuivere gassen 	4	-2001160
    # "54.52":,	# gassen - bijzonder, voorziening - menggassen	4	-2001140
    # Cooling Generator and Distribution (Koude-opwekking en distributie)
    # "55":,	# Koude-opwekking en distributie	2	-2001140
    # "55.00":,	# koude-opwekking; algemeen	3	-2001140
    # "55.10":,	# koude-opwekking - lokaal, algemeen (verzamelniveau) 	4	-2001140
    # "55.11":,	# koude-opwekking - lokaal, raamkoelers 	4	-2001140
    # "55.12":,	# koude-opwekking - lokaal, splitsystemen 	4	-2001140
    # "55.13":,	# koude-opwekking - lokaal, compactsystemen	4	-2001140
    # "55.20":,	# koude-opwekking - centraal, algemeen (verzamelniveau) 	4	-2001140
    # "55.21":,	# koude-opwekking - centraal, compressorensystemen 	4	-2001140
    # "55.22":,	# koude-opwekking - centraal, absorptiesystemen 	4	-2001140
    # "55.23":,	# koude-opwekking - centraal, grondwatersystemen 	4	-2001140
    # "55.24":,	# koude-opwekking - centraal, oppervlaktewatersystemen	4	-2001140
    # "55.30":,	# koude-opwekking - distributie, algemeen (verzamelniveau) 	4	-2001140
    # "55.31":,	# koude-opwekking - distributie, distributie-systemen	4	-2001140
    # Heat Distribution (Warmtedistributie)
    # "56":,  #	Warmtedistributie	2	-2001140
    # "56.00":, #  #warmtedistributie; algemeen 	3	-2001140
    # "56.10":, #  #warmtedistributie - water, algemeen (verzamelniveau) 	4	-2001140
    # "56.11":, #  #warmtedistributie - water, radiatorsystemen 	4	-2001140
    # "56.12":, #  #warmtedistributie - water, convectorsystemen 	4	-2001140
    # "56.13":, #  #warmtedistributie - water, vloerverwarmingssysteem	4	-2001140
    # "56.20":, #  #warmtedistributie - stoom, algemeen (verzamelniveau) 	4	-2001140
    # "56.21":, #  #warmtedistributie - stoom, radiatorsystemen 	4	-2001140
    # "56.22":, #  #warmtedistributie - stoom, convectorsystemen 	4	-2001140
    # "56.24":, #  #warmtedistributie - stoom, stralingspanelen	4	-2001140
    # "56.30":, #  #warmtedistributie - lucht, algemeen (verzamelniveau) 	4	-2001140
    # "56.31":, #  #warmtedistributie - lucht, directe distributiesysteem 	4	-2001140
    # "56.32":, #  #warmtedistributie - lucht, systeem met stralingsoverdracht	4	-2001140
    # "56.40":, #  #warmtedistributie - bijzonder, algemeen (verzamelniveau) 	4	-2001140
    # "56.41":, #  #warmtedistributie - bijzonder, zonnewarmtesysteem 	4	-2001140
    # "56.42":, #  #warmtedistributie - bijzonder, aardwarmtesysteem 	4	-2001140
    # "56.43":, #  #warmtedistributie - bijzonder, centraal warmtepompsysteem	4	-2001140
    # Air Treatment (Luchtbehandeling)
    # "57":,	#   Luchtbehandeling	2	-2001140
    # "57.00":,	# luchtbehandeling; algemeen	3	-2001140
    # "57.10":,	# luchtbehandeling - natuurlijke ventilatie, algemeen (verzamelniveau) 	4	-2001140
    # "57.11":,	# luchtbehandeling - natuurlijke ventilatie, voorzieningen - regelbaar 	4	-2001140
    # "57.12":,	# luchtbehandeling - natuurlijke ventilatie, voorzieningen - niet regelbaar	4	-2001140
    # "57.20":,	# luchtbehandeling - lokale mechanische afzuiging, algemeen (verzamelniveau) 	4	-2001140
    # "57.21":,	# luchtbehandeling - lokale mechanische afzuiging, afzuiginstallatie	4	-2001140
    # "57.30":,	# luchtbehandeling - centrale mechanische afzuiging, algemeen (verzamelniveau) 	4	-2001140
    # "57.31":,	# luchtbehandeling - centrale mechanische afzuiging, afzuiginstallatie	4	-2001140
    # "57.40":,	# luchtbehandeling - lokale mechanische ventilatie, algemeen (verzamelniveau) 	4	-2001140
    # "57.41":,	# luchtbehandeling - lokale mechanische ventilatie, ventilatie-installatie	4	-2001140
    # "57.50":,	# luchtbehandeling - centrale mechanische ventilatie, algemeen (verzamelniveau)	4	-2001140
    # "57.51":,	# luchtbehandeling - centrale mechanische ventilatie, ventilatie-installatie 	4	-2001140
    # "57.52":,	# luchtbehandeling - centrale mechanische ventilatie, ventilatie-installatie met warmte-terugwinning	4	-2001140
    # "57.60":,	# luchtbehandeling - lokaal, algemeen (verzamelniveau) 	4	-2001140
    # "57.61":,	# luchtbehandeling - lokaal, luchtbehandelingsinstallatie	4	-2001140
    # "57.70":,	# luchtbehandeling - centraal, algemeen (verzamelniveau) 	4	-2001140
    # "57.71":,	# luchtbehandeling - centraal, luchtbehandelingsinstallatie	4	-2001140
    # Climate and Sanitation Control (Regeling Klimaat en Sanitair)
    # "58":,	#   Regeling klimaat en sanitair	2	-2001140
    # "58.00":,	#   regeling klimaat en sanitair; algemeen	3	-2001140
    # "58.10":,	#   regeling klimaat en sanitair - specifieke regelingen, algemeen (verzamelniveau) 	4	-2001140
    # "58.11":,	#   regeling klimaat en sanitair - specifieke regelingen, specifieke regeling 	4	-2001140
    # "58.12":,	#   regeling klimaat en sanitair - specifieke regelingen, gecombineerde regeling	4	-2001140
    # "58.20":,	#   regeling klimaat en sanitair - centrale melding, meting en sturing, algemeen (verzamelniveau)	4	-2001140
    # "58.21":,	#   regeling klimaat en sanitair - centrale melding, meting en sturing, specifieke regeling	4	-2001140
    # "58.22":,	#   regeling klimaat en sanitair - centrale melding, meting en sturing, gecombineerde regeling	4	-2001040
    # Electrical Installations (Installaties Elektrotechnisch)
    # "6":, #-	INSTALLATIES ELEKTROTECHNISCH	1	-2000151
    # "61":,	#   Centrale electrotechnische voorzieningen	2	-2001040
    # "61.00":,	#   centrale elektrotechnische voorzieningen; algemeen	3	-2001040
    # "61.10":,	#   centrale elektrotechnische voorzieningen - energie, noodstroom, algemeen (verzamelniveau) 	4	-2001040
    # "61.11":,	#   centrale elektrotechnische voorzieningen - energie, noodstroom, eigen energieopwekking	4	-2001040
    # "61.20":,	#   centrale elektrotechnische voorzieningen - aarding, algemeen (verzamelniveau)	4	-2001040
    # "61.21":,	#   centrale elektrotechnische voorzieningen - aarding, veiligheidsaarding	4	-2001040
    # "61.22":,	#   centrale elektrotechnische voorzieningen - aarding, medische aarding	4	-2001040
    # "61.23":,	#   centrale elektrotechnische voorzieningen - aarding, speciale aarding	4	-2001040
    # "61.24":,	#   centrale elektrotechnische voorzieningen - aarding, statische elektriciteit	4	-2001040
    # "61.25":,	#   centrale elektrotechnische voorzieningen - aarding, bliksemafleiding	4	-2001040
    # "61.26":,	#   centrale elektrotechnische voorzieningen - aarding, potentiaalvereffening	4	-2001040
    # "61.30":,	#   centrale elektrotechnische voorzieningen - kanalisatie, algemeen (verzamelniveau) 	4	-2001040
    # "61.31":,	#   centrale elektrotechnische voorzieningen - kanalisatie, t.b.v. installaties voor hoge spanning 	4	-2001040
    # "61.32":,	#   centrale elektrotechnische voorzieningen - kanalisatie, t.b.v. installaties voor lage spanning	4	-2001040
    # "61.33":,	#   centrale elektrotechnische voorzieningen - kanalisatie, t.b.v. installaties voor communicatie of beveiliging	4	-2001040
    # "61.40":,	#   centrale elektrotechnische voorzieningen - energie, hoge spanning, algemeen 	4	-2001040
    # "61.41":,	#   centrale elektrotechnische voorzieningen - energie, hoge spanning, 1 Kv en hoger	4	-2001040
    # "61.50":,	#   centrale elektrotechnische voorzieningen - energie, lage spanning, algemeen 	4	-2001040
    # "61.51":,	#   centrale elektrotechnische voorzieningen - energie, lage spanning, lager dan 1 Kv en hoger dan 100 V	4	-2001040
    # "61.60":,	#   centrale elektrotechnische voorzieningen - energie, zeer lage spanning, algemeen 	4	-2001040
    # "61.61":, #	centrale elektrotechnische voorzieningen - energie, zeer lage spanning, lager dan 100 V	4	-2001040
    # "61.70":,   #	centrale elektrotechnische voorzieningen - bliksemafleiding, algemeen 	4	-2001040
    # "61.71":,   #	centrale elektrotechnische voorzieningen - bliksemafleiding, volgens NEN 1014	4	-2001040
    # Power Current (Krachtstroom)
    # "62":,	#   Krachtstroom	2	-2001040
    # "62.00":,	# krachtstroom; algemeen	3	-2001040
    # "62.10":,	# krachtstroom - hoogspanning, algemeen (verzamelniveau) 	4	-2001040
    # "62.11":,	# krachtstroom - hoogspanning, 1 t/m 3 Kv 	4	-2001040
    # "62.12":,	# krachtstroom - hoogspanning, boven 3 Kv	4	-2001040
    # "62.20":,	# krachtstroom - laagspanning, onbewaakt, algemeen (verzamelniveau) 	4	-2001040
    # "62.21":,	# krachtstroom - laagspanning, onbewaakt, 220/230 V - 380 V 	4	-2001040
    # "62.22":,	# krachtstroom - laagspanning, onbewaakt, 380 V - 660 V 	4	-2001040
    # "62.23":,	# krachtstroom - laagspanning, onbewaakt, 660 V - 1 Kv	4	-2001040
    # "62.30":,	# krachtstroom - laagspanning, bewaakt, algemeen (verzamelniveau) 	4	-2001040
    # "62.31":,	# krachtstroom - laagspanning, bewaakt, 220/230 V - 380 V 	4	-2001040
    # "62.32":,	# krachtstroom - laagspanning, bewaakt, 380 V - 660 V 	4	-2001040
    # "62.33":,	# krachtstroom - laagspanning, bewaakt, 660 V - l kV	4	-2001040
    # "62.40":,	# krachtstroom - laagspanning, gestabiliseerd, algemeen (verzamelniveau) 	4	-2001040
    # "62.41":,	# krachtstroom - laagspanning, gestabiliseerd, 220/230 V - 380 V 	4	-2001040
    # "62.42":,	# krachtstroom - laagspanning, gestabiliseerd, 380 V - 660 V 	4	-2001040
    # "62.43":,	# krachtstroom - laagspanning, gestabiliseerd, 660 V - 1 Kv	4	-2001040
    # "62.50":,	# krachtstroom - laagspanning, gecompenseerd, algemeen (verzamelniveau) 	4	-2001040
    # "62.51":,	# krachtstroom - laagspanning, gecompenseerd, 220/230 V - 380 V 	4	-2001040
    # "62.52":,	# krachtstroom - laagspanning, gecompenseerd, 380 V - 660 V 	4	-2001120
    # "62.53":,	# krachtstroom - laagspanning, gecompenseerd, 660 V - 1 Kv	4	-2001120
    # Lighting (Verlichting)
    # "63":,	#   Verlichting	2	-2001120
    # "63.00":,	#   verlichting; algemeen	3	-2001120
    # "63.10":,	#   verlichting - standaard, onbewaakt, algemeen (verzamelniveau) 	4	-2001120
    # "63.11":,	#   verlichting - standaard, onbewaakt, 220/230 V 	4	-2001120
    # "63.12":,	#   verlichting - standaard, onbewaakt, 115 V 	4	-2001120
    # "63.13":,	#   verlichting - standaard, onbewaakt, 42 V 	4	-2001120
    # "63.14":,	#   verlichting - standaard, onbewaakt, 24 V	4	-2001120
    # "63.20":,	#   verlichting - calamiteiten, decentraal gevoed, algemeen (verzamelniveau)	4	-2001120
    # "63.23":,	#   verlichting - calamiteiten, decentraal gevoed, 42 V	4	-2001120
    # "63.24":,	#   verlichting - calamiteiten, decentraal gevoed, 24 V	4	-2001120
    # "63.30":,	#   verlichting - bijzonder, onbewaakt, algemeen (verzamelniveau) 	4	-2001120
    # "63.31":,	#   verlichting - bijzonder, onbewaakt, 220/230 V 	4	-2001120
    # "63.32":,	#   verlichting - bijzonder, onbewaakt, 115 V 	4	-2001120
    # "63.33":,	#   verlichting - bijzonder, onbewaakt, 42 V 	4	-2001120
    # "63.34":,	#   verlichting - bijzonder, onbewaakt, 24 V	4	-2001120
    # "63.40":,	#   verlichting - standaard, bewaakt, algemeen (verzamelniveau) 	4	-2001120
    # "63.41":,	#   verlichting - standaard, bewaakt, 220/230 V 	4	-2001120
    # "63.42":,	#   verlichting - standaard, bewaakt, 115 V 	4	-2001120
    # "63.43":,	#   verlichting - standaard, bewaakt, 42 V 	4	-2001120
    # "63.44":,	#   verlichting - standaard, bewaakt, 24 V	4	-2001120
    # "63.50":,	#   verlichting - calamiteiten, centraal gevoed, algemeen (verzamelniveau) 	4	-2001120
    # "63.51":,	#   verlichting - calamiteiten, centraal gevoed, 220/230 V 	4	-2001120
    # "63.52":,	#   verlichting - calamiteiten, centraal gevoed, 115 V 	4	-2001120
    # "63.53":,	#   verlichting - calamiteiten, centraal gevoed, 42 V 	4	-2001120
    # "63.54":,	#   verlichting - calamiteiten, centraal gevoed, 24 V	4	-2001120
    # "63.60":,	#   verlichting - bijzonder, bewaakt, algemeen (verzamelniveau) 	4	-2001120
    # "63.61":,	#   verlichting - bijzonder, bewaakt, 220/230 V 	4	-2001120
    # "63.62":,	#   verlichting - bijzonder, bewaakt, 115 V 	4	-2001120
    # "63.63":, #	verlichting - bijzonder, bewaakt, 42 V 	4	-2001120
    # "63.64":, #	verlichting - bijzonder, bewaakt, 24 V	4	-2001120
    # "63.70":, #	verlichting - reclame, algemeen (verzamelniveau)	4	-2001120
    # "63.71":, #	verlichting - reclame, 220/230 V	4	-2001120
    # "63.72":, #	verlichting - reclame, 115 V	4	-2001120
    # "63.73":, #	verlichting - reclame, 42 V	4	-2001120
    # "63.74":, #	verlichting - reclame, 24 V	4	-2001060
    # "63.75":, #	verlichting - reclame, 1Kv en hoger	4	-2001060
    # Communication (Communicatie)
    # "64":, #	Communicatie	2	-2001060
    # "64.00":,	# communicatie; algemeen	3	-2001060
    # "64.10":,	# communicatie - overdracht van signalen, algemeen (verzamelniveau) 	4	-2001060
    # "64.11":,	# communicatie - overdracht van signalen, algemene signaleringen 	4	-2001060
    # "64.12":,	# communicatie - overdracht van signalen, algemene personenoproep 	4	-2001060
    # "64.13":,	# communicatie - overdracht van signalen, tijdsignalering 	4	-2001060
    # "64.14":,	# communicatie - overdracht van signalen, aanwezigheid-/beletsignalering	4	-2001060
    # "64.20":,	# communicatie - overdracht van geluid/spraak, algemeen (verzamelniveau) 	4	-2001060
    # "64.21":,	# communicatie - overdracht van geluid/spraak, telefoon 	4	-2001060
    # "64.22":,	# communicatie - overdracht van geluid/spraak, intercom 	4	-2001060
    # "64.23":,	# communicatie - overdracht van geluid/spraak, radio/mobilofoon 	4	-2001060
    # "64.24":,	# communicatie - overdracht van geluid/spraak, geluiddistributie 	4	-2001060
    # "64.25":,	# communicatie - overdracht van geluid/spraak, vertaalsystemen 	4	-2001060
    # "64.26":,	# communicatie - overdracht van geluid/spraak, conferentiesystemen	4	-2001060
    # "64.30":,	# communicatie - overdracht van beelden, algemeen (verzamelniveau) 	4	-2001060
    # "64.31":,	# communicatie - overdracht van beelden, gesloten televisiecircuits 	4	-2001060
    # "64.32":,	# communicatie - overdracht van beelden, beeldreproductie 	4	-2001060
    # "64.33":,	# communicatie - overdracht van beelden, film/dia/overhead	4	-2001060
    # "64.40":,	# communicatie - overdracht van data, algemeen (verzamelniveau) 	4	-2001060
    # "64.41":,	# communicatie - overdracht van data, gesloten datanet 	4	-2001060
    # "64.42":,	# communicatie - overdracht van data, openbaar datanet	4	-2001060
    # "64.50":,	# communicatie - geïntegreerde systemen, algemeen (verzamelniveau) 	4	-2001060
    # "64.51":,	# communicatie - geïntegreerde systemen, gesloten netwerken 	4	-2001060
    # "64.52":,	# communicatie - geïntegreerde systemen, openbare netwerken	4	-2001060
    # "64.60":,	# communicatie - antenne-inrichtingen, algemeen	4	-2001060
    # Security (Beveiliging)
    # "65":, #	Beveiliging	2	-2001060
    # "65.00":,	# beveiliging; algemeen	3	-2001060
    # "65.10":,	# beveiliging - brand, algemeen (verzamelniveau) 	4	-2001060
    # "65.11":,	# beveiliging - brand, detectie en alarmering 	4	-2001060
    # "65.12":,	# beveiliging - brand, deurgrendelingen en -ontgrendelingen 	4	-2001060
    # "65.13":,	# beveiliging - brand, brandbestrijding	4	-2001060
    # "65.20":,	# beveiliging - braak, algemeen (verzamelniveau) 	4	-2001060
    # "65.21":,	# beveiliging - braak, detectie en alarmering 	4	-2001060
    # "65.22":,	# beveiliging - braak, toegangscontrole	4	-2001060
    # "65.30":,	# beveiliging - overlast, detectie en alarmering, algemeen (verzamelniveau) 	4	-2001060
    # "65.31":,	# beveiliging - overlast, detectie en alarmering, zonweringsinstallatie 	4	-2001060
    # "65.32":,	# beveiliging - overlast, detectie en alarmering, elektromagnetische voorzieningen	4	-2001060
    # "65.33":,	# beveiliging - overlast, detectie en alarmering, elektromagnetische voorzieningen 	4	-2001060
    # "65.34":,	# beveiliging - overlast, detectie en alarmering, overspanningsbeveiliging 	4	-2001060
    # "65.35":,	# beveiliging - overlast, detectie en alarmering, gassenbeveiliging 	4	-2001060
    # "65.36":,	# beveiliging - overlast, detectie en alarmering, vloeistofbeveiliging 	4	-2001060
    # "65.37":,	# beveiliging - overlast, detectie en alarmering, stralingsbeveiliging 	4	-2001060
    # "65.39":,	# beveiliging - overlast, detectie en alarmering, overige beveiligingen	4	-2001060
    # "65.40":,	# beveiliging - sociale alarmering, algemeen (verzamelniveau) 	4	-2001060
    # "65.41":,	# beveiliging - sociale alarmering, nooddetectie - gesloten systemen 	4	-2001060
    # "65.42":,	# beveiliging - sociale alarmering, nooddetectie - open systemen	4	-2001350
    # "65.50":,	# beveiliging - milieu-overlast, detectie en alarmering, algemeen (verzamelniveau) 	4	-2001350
    # Transport
    # "66":,	#   Transport	2	-2001350
    # "66.00":,	#   transport; algemeen	3	-2001350
    # "66.10":,	#   transport - liften en heftableau's, algemeen (verzamelniveau) 	4	-2001350
    # "66.11":,	#   transport - liften en heftableau's, elektrische liften 	4	-2001350
    # "66.12":,	#   transport - liften en heftableau's, hydraulische liften 	4	-2001350
    # "66.13":,	#   transport - liften en heftableau's, trapliften 	4	-2001350
    # "66.14":,	#   transport - liften en heftableau's, heftableau's	4	-2001350
    # "66.20":,	#   transport - roltrappen en rolpaden, algemeen (verzamelniveau) 	4	-2001350
    # "66.21":,	#   transport - roltrappen en rolpaden, roltrappen 	4	-2001350
    # "66.22":,	#   transport - roltrappen en rolpaden, rolpaden	4	-2001350
    # "66.30":,	#   transport - goederen, algemeen (verzamelniveau) 	4	-2001350
    # "66.31":,	#   transport - goederen, goederenliften 	4	-2001350
    # "66.32":,	#   transport - goederen, goederenheffers 	4	-2001350
    # "66.33":,	#   transport - goederen, baantransportmiddelen 	4	-2001350
    # "66.34":,	#   transport - goederen, bandtransportmiddelen 	4	-2001350
    # "66.35":,	#   transport - goederen, baktransportmiddelen 	4	-2001350
    # "66.36":,	#   transport - goederen, hijswerktuigen 	4	-2001350
    # "66.37":,	#   transport - goederen, vrije-baan-transportvoertuigen	4	-2001350
    # "66.40":,	#   transport - documenten, algemeen (verzamelniveau) 	4	-2001350
    # "66.41":,	#   transport - documenten, buizenpost 	4	-2001350
    # "66.42":,	#   transport - documenten, railcontainer banen 	4	-2001060
    # "66.44":,	#   transport - documenten, bandtransportmiddelen	4	-2001060
    # Building Management Provisions (Gebouwbeheervoorzieningen)
    # "67":,	#   Gebouwbeheervoorzieningen	2	-2001060
    # "67.00":,	#   gebouwbeheervoorzieningen; algemeen	3	-2001060
    # "67.10":,	#   gebouwbeheervoorzieningen - bediening en signalering, algemeen (verzamelniveau) 	4	-2001060
    # "67.11":,	#   gebouwbeheervoorzieningen - bediening en signalering, elektrotechnische systemen 	4	-2001060
    # "67.12":,	#   gebouwbeheervoorzieningen - bediening en signalering, optische systemen 	4	-2001060
    # "67.13":,	#   gebouwbeheervoorzieningen - bediening en signalering, pneumatische systemen 	4	-2001060
    # "67.14":,	#   gebouwbeheervoorzieningen - bediening en signalering, geïntegreerde systemen	4	-2001060
    # "67.20":,	#   gebouwbeheervoorzieningen - gebouwautomatisering, algemeen (verzamelniveau) 	4	-2001060
    # "67.21":,	#   gebouwbeheervoorzieningen - gebouwautomatisering, elektrotechnische systemen 	4	-2001060
    # "67.22":,	#   gebouwbeheervoorzieningen - gebouwautomatisering, optische systemen 	4	-2001060
    # "67.23":,	#   gebouwbeheervoorzieningen - gebouwautomatisering, pneumatische systemen 	4	-2001060
    # "67.24":,	#   gebouwbeheervoorzieningen - gebouwautomatisering, geïntegreerde systemen	4	-2001060
    # "67.30":,	#   gebouwbeheervoorzieningen - regelinstallaties klimaat en sanitair (op afstand), algemeen (verzamelniveau)	4	-2001060
    # "67.31":,	#   gebouwbeheervoorzieningen - regelinstallaties klimaat en sanitair (op afstand), elektrotechnische systemen	4	-2001060
    # "67.32":,	#   gebouwbeheervoorzieningen - regelinstallaties klimaat en sanitair (op afstand), optische systemen	4	-2001060
    # "67.33":,	#   gebouwbeheervoorzieningen - regelinstallaties klimaat en sanitair (op afstand), pneumatische systemen	4	-2001350
    # "67.34":,	#   gebouwbeheervoorzieningen - regelinstallaties klimaat en sanitair (op afstand), geïntegreerde systemen	4	-2001350
    # Fixed Provisions (Vaste Voorzieningen)
    # "7":, # -	VASTE VOORZIENINGEN	1	-2000151
    # "71":,	#   Vaste verkeersvoorzieningen	2	-2001350
    # "71.00":,	#   vaste verkeersvoorzieningen; algemeen	3	-2001350
    # "71.10":,	#   vaste verkeersvoorzieningen - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "71.11":,	#   vaste verkeersvoorzieningen - standaard, meubileringen 	4	-2001350
    # "71.12":,	#   vaste verkeersvoorzieningen - standaard, bewegwijzeringen 	4	-2001350
    # "71.13":,	#   vaste verkeersvoorzieningen - standaard, kunstwerken 	4	-2001350
    # "71.14":,	#   vaste verkeersvoorzieningen - standaard, decoraties e.d.	4	-2001350
    # "71.20":,	#   vaste verkeersvoorzieningen - bijzonder, algemeen (verzamelniveau)	4	-2001350
    # "71.21":,	#   vaste verkeersvoorzieningen - bijzonder, meubileringen	4	-2001350
    # "71.22":,	#   vaste verkeersvoorzieningen - bijzonder, bewegwijzeringen	4	-2001350
    # "71.23":,	#   vaste verkeersvoorzieningen - bijzonder, specifieke voorz. (o.a. loopleuningen)	4	-2001350
    # Fixed User Provisions (Vaste gebruikersvoorzieningen)
    # "72":,	#   Vaste gebruikersvoorzieningen	2	-2001350
    # "72.00":,	#   vaste gebruikersvoorzieningen; algemeen	3	-2001350
    # "72.10":,	#   vaste gebruikersvoorzieningen - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "72.11":,	#   vaste gebruikersvoorzieningen - standaard, meubilering 	4	-2001350
    # "72.12":,	#   vaste gebruikersvoorzieningen - standaard, lichtweringen 	4	-2001350
    # "72.13":,	#   vaste gebruikersvoorzieningen - standaard, gordijnvoorzieningen	4	-2001350
    # "72.14":,	#   vaste gebruikersvoorzieningen - standaard, beschermende voorzieningen	4	-2001350
    # "72.20":,	#   vaste gebruikersvoorzieningen - bijzonder, algemeen (verzamelniveau)	4	-2001350
    # "72.21":,	#   vaste gebruikersvoorzieningen - bijzonder, meubilering voor specifieke functie-doeleinden	4	-2001000
    # "72.22":,	#   vaste gebruikersvoorzieningen - bijzonder, instrumenten/apparatuur	4	-2001000
    # Fixed Kitchen Provisions (Vaste Keukenvoorzieningen)
    # "73":, #	Vaste keukenvoorzieningen	2	-2001000
    # "73.00":,	#   vaste keukenvoorzieningen; algemeen	3	-2001000
    # "73.10":,	#   vaste keukenvoorzieningen - standaard, algemeen (verzamelniveau) 	4	-2001000
    # "73.11":,	#   vaste keukenvoorzieningen - standaard, keukenmeubilering 	4	-2001000
    # "73.12":,	#   vaste keukenvoorzieningen - standaard, keukenapparatuur	4	-2001000
    # "73.20":,	#   vaste keukenvoorzieningen - bijzonder, algemeen (verzamelniveau) 	4	-2001000
    # "73.21":,	#   vaste keukenvoorzieningen - bijzonder, keukenmeubilering 	4	-2000160
    # "73.22":,	#   vaste keukenvoorzieningen - bijzonder, keukenapparatuur	4	-2000160
    # Fixed Sanitary Provisions (Vaste Sanitarie Voorzieningen)
    # "74":,	#   Vaste sanitaire voorzieningen	2	-2000160
    # "74.00":,	#   vaste sanitaire voorzieningen; algemeen	3	-2000160
    # "74.10":,	#   vaste sanitaire voorzieningen - standaard, algemeen (verzamelniveau) 	4	-2000160
    # "74.11":,	#   vaste sanitaire voorzieningen - standaard, sanitaire toestellen - normaal 	4	-2000160
    # "74.12":,	#   vaste sanitaire voorzieningen - standaard, sanitaire toestellen - aangepast 	4	-2000160
    # "74.13":,	#   vaste sanitaire voorzieningen - standaard, accessoires	4	-2000160
    # "74.20":,	#   vaste sanitaire voorzieningen - bijzonder, algemeen (verzamelniveau)	4	-2000160
    # "74.21":,	#   vaste sanitaire voorzieningen - bijzonder, sanitaire toestellen voor bijzondere toepassing	4	-2001350
    # "74.22":,	#   vaste sanitaire voorzieningen - bijzonder, ingebouwde sanitaire voorzieningen	4	-2001350
    # Fixed Maintenance Provisions (Vaste Onderhoudsvoorzieningen)
    # "75":,	#   Vaste onderhoudsvoorzieningen	2	-2001350
    # "75.00":,	#   vaste onderhoudsvoorzieningen; algemeen 	3	-2001350
    # "75.10":,	#   vaste onderhoudsvoorzieningen - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "75.11":,	#   vaste onderhoudsvoorzieningen - standaard, gebouwonderhoudsvoorzieningen	4	-2001350
    # "75.12":,	#   vaste onderhoudsvoorzieningen - standaard, interieur onderhoudsvoorzieningen	4	-2001350
    # "75.13":,	#   vaste onderhoudsvoorzieningen - standaard, gevelonderhoudsvoorzieningen	4	-2001350
    # "75.20":,	#   vaste onderhoudsvoorzieningen - bijzonder, algemeen (verzamelniveau)	4	-2001350
    # "75.21":,	#   vaste onderhoudsvoorzieningen - bijzonder, gebouwonderhoudsvoorzieningen	4	-2001350
    # "75.22":,	#   vaste onderhoudsvoorzieningen - bijzonder, interieur onderhoudsvoorzieningen	4	-2001350
    # "75.23":,	#   vaste onderhoudsvoorzieningen - bijzonder, gemechaniseerde gevelonderhoudsvoorzieningen	4	-2001350
    # Fixed Storage Provisions (Vaste Opslagvoorzieningen)
    # "76":,	#   Vaste opslagvoorzieningen	2	-2001350
    # "76.00":,	#   vaste opslagvoorzieningen; algemeen	3	-2001350
    # "76.10":,	#   vaste opslagvoorzieningen - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "76.11":,	#   vaste opslagvoorzieningen - standaard, meubileringen	4	-2001350
    # "76.20":,	#   vaste opslagvoorzieningen - bijzonder, algemeen (verzamelniveau) 	4	-2001350
    # "76.21":,	#   vaste opslagvoorzieningen - bijzonder, gemechaniseerde voorzieningen	4	-2001350
    # "76.22":,	#   vaste opslagvoorzieningen - bijzonder, specifieke voorzieningen	4	-2001350
    # Loose Inventory (Loose Inventaris)
    # "8":, # -	LOSSE INVENTARIS	1	-2000151
    # "81":,	#   Losse verkeersinventaris	2	-2001350
    # "81.00":,	#   losse verkeersinventaris; algemeen	3	-2001350
    # "81.10":,	#   losse verkeersinventaris - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "81.11":,	#   losse verkeersinventaris - standaard, meubilering 	4	-2001350
    # "81.12":,	#   losse verkeersinventaris - standaard, bewegwijzering 	4	-2001350
    # "81.13":,	#   losse verkeersinventaris - standaard, kunstwerken 	4	-2001350
    # "81.14":,	#   losse verkeersinventaris - standaard, decoraties e.d.	4	-2001350
    # "81.20":,	#   losse verkeersinventaris - bijzonder, algemeen (verzamelniveau)	4	-2001350
    # "81.21":,	#   losse verkeersinventaris - bijzonder, meubilering	4	-2001350
    # "81.22":,	#   losse verkeersinventaris - bijzonder, bewegwijzering	4	-2001350
    # "81.23":,	#   losse verkeersinventaris - bijzonder, specifieke voorzieningen (o.a. avalbakken)	4	-2001350
    # Loose User Inventory (Loose gebruikersinventaris)
    # "82":,	#   Losse gebruikersinventaris	2	-2001350
    # "82.00":,	#   losse gebruikersinventaris; algemeen	3	-2001350
    # "82.10":,	#   losse gebruikersinventaris - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "82.11":,	#   losse gebruikersinventaris - standaard, meubilering 	4	-2001350
    # "82.12":,	#   losse gebruikersinventaris - standaard, lichtweringen/verduisteringen 	4	-2001350
    # "82.13":,	#   losse gebruikersinventaris - standaard, stofferingen	4	-2001350
    # "82.20":,	#   losse gebruikersinventaris - bijzonder, algemeen (verzamelniveau)	4	-2001350
    # "82.21":,	#   losse gebruikersinventaris - bijzonder, meubilering voor specifieke functie-doeleinden	4	-2001000
    # "82.22":,	#   losse gebruikersinventaris - bij zonder, instrumenten/apparatuur	4	-2001000
    # Loose Kitchen Inventory (Loose Keukeninventaris)
    # "83":,	#   Losse keukeninventaris	2	-2001000
    # "83.00":,	#   losse keukeninventaris; algemeen	3	-2001000
    # "83.10":,	#   losse keukeninventaris - standaard, algemeen (verzamelniveau) 	4	-2001000
    # "83.11":,	#   losse keukeninventaris - standaard, keukenmeubilering 	4	-2001000
    # "83.12":,	#   losse keukeninventaris - standaard, keukenapparatuur 	4	-2001000
    # "83.13":,	#   losse keukeninventaris - standaard, kleine keukeninventaris	4	-2001000
    # "83.20":,	#   losse keukeninventaris - bijzonder, algemeen (verzamelniveau) 	4	-2001000
    # "83.21":,	#   losse keukeninventaris - bijzonder, keukeninrichting 	4	-2001000
    # "83.22":,	#   losse keukeninventaris - bijzonder, keukenapparatuur 	4	-2001000
    # "83.23":,	#   losse keukeninventaris - bijzonder, kleine keukeninventaris 	4	-2001160
    # "83.24":,	#   losse keukeninventaris - bijzonder, transportmiddelen	4	-2001160
    # Loose Sanitary Inventory (Losse sanitarie inventaris)
    # "84":,	#   Losse sanitaire inventaris	2	-2001160
    # "84.00":,	#   losse sanitaire inventaris; algemeen	3	-2001160
    # "84.10":,	#   losse sanitaire inventaris - standaard, algemeen (verzamelniveau) 	4	-2001160
    # "84.11":,	#   losse sanitaire inventaris - standaard, afvalvoorzieningen	4	-2001160
    # "84.12":,	#   losse sanitaire inventaris - standaard, voorzieningen t.b.v. hygiëne 	4	-2001160
    # "84.13":,	#   losse sanitaire inventaris - standaard, accessoires	4	-2001160
    # "84.20":,	#   losse sanitaire inventaris - bijzonder, algemeen (verzamelniveau) 	4	-2001350
    # "84.21":,	#   losse sanitaire inventaris - bijzonder, sanitaire toestellen voor bijzondere toepassing	4	-2001350
    # Loose Cleaning Inventory (Loose schoonmaakinventaris)
    # "85":,	#   Losse schoonmaakinventaris	2	-2001350
    # "85.00":,	#   losse schoonmaakinventaris; algemeen	3	-2001350
    # "85.10":,	#   losse schoonmaakinventaris -standaard, algemeen (verzamelniveau) 	4	-2001350
    # "85.11":,	#   losse schoonmaakinventaris - standaard, schoonmaakapparatuur 	4	-2001350
    # "85.12":,	#   losse schoonmaakinventaris - standaard, vuilopslag 	4	-2001350
    # "85.13":,	#   losse schoonmaakinventaris - standaard, vuiltransport	4	-2001350
    # "85.20":,	#   losse schoonmaakinventaris - bijzonder, algemeen (verzamelniveau) 	4	-2001350
    # "85.21":,	#   losse schoonmaakinventaris - bijzonder, schoonmaakapparatuur 	4	-2001350
    # "85.22":,	#   losse schoonmaakinventaris - bijzonder, vuilopslag 	4	-2001350
    # "85.23":,	#   losse schoonmaakinventaris - bijzonder, vuiltransport	4	-2001350
    # Loose Storage Inventory (Loose opslaginventaris)
    # "86":,	#   Losse opslaginventaris	2	-2001350
    # "86.00":,	#   losse opslaginventaris; algemeen	3	-2001350
    # "86.10":,	#   losse opslaginventaris - standaard, algemeen (verzamelniveau) 	4	-2001350
    # "86.11":,	#   losse opslaginventaris - standaard, meubileringen	4	-2001350
    # "86.20":,	#   losse opslaginventaris - bijzonder, algemeen (verzamelniveau) 	4	-2001350
    # "86.21":,	#   losse opslaginventaris - bijzonder, gemechaniseerde voorzieningen	4	-2001260
    # "86.22":,	#   losse opslaginventaris - bijzonder, specifieke voorzieningen	4	-2001260
    # Terrain (Terrein)
    # "9":, # -	TERREIN	1	-2000151
    # "90":,	#   Terrein	2	-2001260
    # "90.00":,	#   terrein; algemeen	3	-2001260
    # "90.10":,	#   terrein - grondvoorzieningen, algemeen (verzamelniveau) 	4	-2001260
    # "90.11":,	#   terrein - grondvoorzieningen, verwijderen opstakels 	4	-2001260
    # "90.12":,	#   terrein - grondvoorzieningen, grondwaterverlagingen 	4	-2001260
    # "90.13":,	#   terrein - grondvoorzieningen, drainagevoorz.	4	-2001260
    # "90.20":,	#   terrein - opstallen, algemeen (verzamelniveau) 	4	-2001260
    # "90.21":,	#   terrein - opstallen, gebouwtjes met speciale functie 	4	-2001260
    # "90.22":,	#   terrein - opstallen, overkappingen	4	-2001260
    # "90.30":,	#   terrein - omheiningen, algemeen (verzamelniveau) 	4	-2001260
    # "90.31":,	#   terrein - omheiningen, muren	4	-2001260
    # "90.32":,	#   terrein - omheiningen, hekwerken 	4	-2001260
    # "90.33":,	#   terrein - omheiningen, overige afscheidingen 	4	-2001260
    # "90.34":,	#   terrein - omheiningen, toegangen	4	-2001260
    # "90.40":,	#   terrein - terreinafwerkingen, algemeen (verzamelniveau) 	4	-2001260
    # "90.41":,	#   terrein - terreinafwerkingen, verhardingen 	4	-2001260
    # "90.42":,	#   terrein - terreinafwerkingen, beplantingen 	4	-2001260
    # "90.43":,	#   terrein - terreinafwerkingen, waterpartijen 	4	-2001260
    # "90.44":,	#   terrein - terreinafwerkingen, keerwanden/balustrades 	4	-2001260
    # "90.45":,	#   terrein - terreinafwerkingen, pergola's	4	-2001260
    # "90.50":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, algemeen (verzamelniveau) 	4	-2001260
    # "90.51":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, verwarmingsvoorzieningen	4	-2001260
    # "90.52":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, afvoervoorzieningen	4	-2001260
    # "90.53":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, watervoorzieningen	4	-2001260
    # "90.54":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, gasvoorzieningen	4	-2001260
    # "90.55":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, koudeopwekkingsvoorzieningen	4	-2001260
    # "90.56":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, warmtedistributievoorzieningen	4	-2001260
    # "90.57":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, luchtbehandelingsvoorzieningen	4	-2001260
    # "90.58":,	#   terrein - terreinvoorzieningen - werktuigbouwkundig, regelingvoorzieningen	4	-2001260
    # "90.60":,	#   terrein - terreinvoorzieningen - elektrotechnisch, algemeen (verzamelniveau) 	4	-2001260
    # "90.61":,	#   terrein - terreinvoorzieningen - elektrotechnisch, elektrotechnische en aardingsvoorzieningen	4	-2001260
    # "90.62":,	#   terrein - terreinvoorzieningen - elektrotechnisch, krachtvoorzieningen	4	-2001260
    # "90.63":,	#   terrein - terreinvoorzieningen - elektrotechnisch, lichtvoorzieningen	4	-2001260
    # "90.64":,	#   terrein - terreinvoorzieningen - elektrotechnisch, communicatievoorzieningen	4	-2001260
    # "90.65":,	#   terrein - terreinvoorzieningen - elektrotechnisch, beveiligingsvoorzieningen	4	-2001260
    # "90.66":,	#   terrein - terreinvoorzieningen - elektrotechnisch, transportvoorzieningen	4	-2001260
    # "90.67":,	#   terrein - terreinvoorzieningen - elektrotechnisch, beheervoorzieningen	4	-2001260
    # "90.70":,	#   terrein - terreininrichtingen - standaard, algemeen (verzamelniveau) 	4	-2001260
    # "90.71":,	#   terrein - terreininrichtingen - standaard, terreinmeubilering 	4	-2001260
    # "90.72":,	#   terrein - terreininrichtingen - standaard, bewegwijzering 	4	-2001260
    # "90.73":,	#   terrein - terreininrichtingen - standaard, kunstwerken 	4	-2001260
    # "90.74":,	#   terrein - terreininrichtingen - standaard, decoraties e.d.	4	-2001260
    # "90.80":,	#   terrein - terreininrichtingen - bijzonder, algemeen (verzamelniveau) 	4	-2001260
    # "90.81":,	#   terrein - terreininrichtingen - bijzonder, terreinmeubilering 	4	-2001260
    # "90.82":,	#   terrein - terreininrichtingen - bijzonder, specifieke voorzieningen	4	-2001350
    # "90.83":,	#   terrein - terreininrichtingen - bijzonder, bijzondere verhardingen	4	-2001350
    # Indirect Project Provisions (Indirecte Projectvoorzieningen)
    # "0":, # -	INDIRECTE PROJECTVOORZIENINGEN	1	-2000151
    # "0-.00":,	#   indirecte projectvoorzieningen	3	-2001350
    # "0-.10":,	#   indirecte projectvoorzieningen - werkterreininrichting, algemeen (verzamelniveau)	4	-2001350
    # "0-.11":,	#   indirecte projectvoorzieningen - werkterreininrichting, bijkomende werken	4	-2001350
    # "0-.12":,	#   indirecte projectvoorzieningen - werkterreininrichting, personen/materiaalvoorzieningen	4	-2001350
    # "0-.13":,	#   indirecte projectvoorzieningen - werkterreininrichting, energievoorzieningen	4	-2001350
    # "0-.14":,	#   indirecte projectvoorzieningen - werkterreininrichting, beveiligingsvoorzieningen	4	-2001350
    # "0-.15":,	#   indirecte projectvoorzieningen - werkterreininrichting, doorwerkvoorzieningen	4	-2001350
    # "0-.16":,	#   indirecte projectvoorzieningen - werkterreininrichting, voorzieningen belendende percelen	4	-2001350
    # "0-.17":,	#   indirecte projectvoorzieningen - werkterreininrichting, onderhoudsvoorzieningen	4	-2001350
    # "0-.20":,	#   indirecte projectvoorzieningen - materieelvoorzieningen, algemeen (verzamelniveau)	4	-2001350
    # "0-,21":,	#   indirecte projectvoorzieningen - materieelvoorzieningen, transport	4	-2001350
    # "0-.22":,	#   indirecte projectvoorzieningen - materieelvoorzieningen, gereedschappen	4	-2001350
    # "0-.30":,	#   indirecte projectvoorzieningen - risicodekking, algemeen (verzamelniveau) 	4	-2001350
    # "0-.31":,	#   indirecte projectvoorzieningen - risicodekking, verzekeringen	4	-2001350
    # "0-.32":,	#   indirecte projectvoorzieningen - risicodekking, waarborgen	4	-2001350
    # "0-.33":,	#   indirecte projectvoorzieningen - risicodekking, prijsstijgingen	4	-2001350
    # "0-.40":,	#   indirecte projectvoorzieningen - projectorganisatie, algemeen (verzamelniveau)	4	-2001350
    # "0-.41":,	#   indirecte projectvoorzieningen - projectorganisatie, administratie	4	-2001350
    # "0-.42":,	#   indirecte projectvoorzieningen - projectorganisatie, uitvoering	4	-2001350
    # "0-.43":,	#   indirecte projectvoorzieningen - projectorganisatie, documentatie	4	-2001350
    # "0-.50":,	#   indirecte projectvoorzieningen - bedrijfsorganisatie, algemeen (verzamelniveau)	4	-2001350
    # "0-.51":,	#   indirecte projectvoorzieningen - bedrijfsorganisatie, bestuur en directie	4	-2001350
    # "0-.52":,	#   indirecte projectvoorzieningen - bedrijfsorganisatie, winstregelingen	4	-2001350
    # Foundation
    # "13.22": 1161,
    # "16": 1161,
    # "16.11": 1161,
    # "23.20": 1161,
    # Foundation Floors
    # "13_NCG_ihwg strokenfundering": 1161,
    # Floor Beams
    # "05": 1163,
    # "28.10": 1163,
    # Timber Frame Walls
    # Roof Beams
    # "09": 1166,
    # "11": 1166,
    # "12": 1166,
    # Columns
    # "28.11": 4796,
    # Structural Frames
    # Steel Beams
    # Wall Plates
    # Roof Sheathing
    # "27": 1167,
    # Structural Provisions (L2s, L6s, vindverband)
    # Mass
    # : 1173  Missing Assembly Code for mass
    # Facade and Roof Openings (Exterior)
    # "31": 1174,
    # "37": 1174,
    # Interior Wall Openings
    # "32": 3447,
    # Point Cloud
    # : 3581,
    # Clash Test
    # Toposurface
}


def log(message):
    """Log messages to the console."""
    print(message)


def get_workset_id_by_element_type(element_type_name):
    """Get the appropriate workset ID based on the element type name."""
    for prefix, workset_id in WORKSET_MAPPING.items():
        if element_type_name.startswith(prefix):
            return workset_id
    return None


def assign_workset(element, workset_id):
    try:
        t = Transaction(doc, "Assign Workset")
        t.Start()
        param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id)
            log("Assigned element {} to WorksetId {}".format(element.Id, workset_id))
        else:
            log(
                "Workset parameter is missing or read-only for element {}.".format(
                    element.Id
                )
            )
        t.Commit()
    except Exception as e:
        log("Failed to assign WorksetId to element {}: {}".format(element.Id, e))


def process_elements():
    """Process elements across multiple categories and assign worksets."""
    categories = [
        BuiltInCategory.OST_StructuralFoundation,  # Structural Foundations
        BuiltInCategory.OST_Doors,  # Doors
        BuiltInCategory.OST_Windows,  # Windows
        BuiltInCategory.OST_Walls,  # Walls
        # BuiltInCategory.OST_WallsDefault,
        BuiltInCategory.OST_Floors,  # Floors
        # BuiltInCategory.OST_Roofs,  # Roofs
        # BuiltInCategory.OST_Ceilings,  # Ceilings
        # BuiltInCategory.OST_WallFoundationAnalytical,  # Wall Foundation Analytical
        # BuiltInCategory.OST_FoundationSlabAnalytical,  # Foundation Slab Analytical
        # BuiltInCategory.OST_EdgeSlab,  # Slab Edge
        BuiltInCategory.OST_Columns,  # Columns
        # BuiltInCategory.OST_ColumnsHiddenLines,  # Columns Hidden Lines
        # BuiltInCategory.OST_ColumnAnalytical,  # Columns Analytical
        BuiltInCategory.OST_StructuralColumns,  # Structural Column
        # BuiltInCategory.OST_HiddenStructuralColumnLines,  # Hidden Structural Column
        # BuiltInCategory.OST_StructuralFraming,  # Structural Framing
        # BuiltInCategory.OST_HiddenStructuralFramingLines,  # Hidden Structural Framing Lines
        # BuiltInCategory.OST_StructuralStiffener,  # Structural Stiffener
        # BuiltInCategory.OST_StructuralStiffenerHiddenLines,  # Hidden Structural Stiffener Lines
        # BuiltInCategory.OST_StructuralTruss,  # Structural Truss
        # BuiltInCategory.OST_StructuralTrussHiddenLines,  # Hidden Structural Truss Lines
        # BuiltInCategory.OST_HiddenStructuralConnectionLines_Deprecated,  # Hidden Structural Connection
        # BuiltInCategory.OST_StructuralFramingLocationLine,  # Structural Framing Location Line
        # BuiltInCategory.OST_FloorsStructure,  # Structural Floors
        # BuiltInCategory.OST_BeamAnalytical,  # Structural Beam Analytical
        # BuiltInCategory.OST_FramingAnalyticalGeometry,
        # BuiltInCategory.OST_StructuralFramingOpening,  # Structural Framing Opening
        # BuiltInCategory.OST_StructuralFramingOther,  # Structural Framing Other
        # BuiltInCategory.OST_StructuralFramingSystem,  # Structural Framin System
        # BuiltInCategory.OST_StructuralFramingSystemHiddenLines_Obsolete,  # Structural Framing System Hidden Lines
        # BuiltInCategory.OST_RoofsDefault,  # Roofs Default
        # BuiltInCategory.OST_RoofsHiddenLines,  # Roofs Hidden Lines
        # BuiltInCategory.OST_RoofsStructure,  # Roofs Structure
    ]

    for category in categories:
        elements = (
            FilteredElementCollector(doc)
            .OfCategory(category)
            .WhereElementIsNotElementType()
        )
        for element in elements:
            element_type = doc.GetElement(element.GetTypeId())
            element_type_name = element_type.get_Parameter(
                BuiltInParameter.ALL_MODEL_TYPE_NAME
            ).AsString()
            log(
                "Processing element ID {}: Type = {}".format(
                    element.Id, element_type_name
                )
            )

            workset_id = get_workset_id_by_element_type(element_type_name)
            if workset_id:
                assign_workset(element, workset_id)
            else:
                log("No matching workset found for element {}".format(element.Id))


log("Manual workset processing started.")
process_elements()
log("Manual workset processing completed.")
