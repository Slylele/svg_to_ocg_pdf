import os
# Chemin relatif vers le dossier GTK
gtk_path = os.path.join(os.path.dirname(__file__), 'gtk', 'bin')
os.environ["PATH"] += os.pathsep + gtk_path

import sys
import fitz  # PyMuPDF
from lxml import etree
import cairosvg
import tempfile
import datetime
import time


# DEFINITION DES VARIABLES D'EXPORT (issues du .bat ou par défaut)

if len(sys.argv) > 2:
    export_dir = sys.argv[1]
    svg_file = os.path.join(export_dir, sys.argv[2])
else:
    export_dir = os.getcwd() # par défaut, le dossier courant
    svg_file = os.path.join(export_dir, "Test_exemple.svg")

print(f"Les fichiers seront exportés dans : {export_dir}")

now = datetime.datetime.now() # current date and time
datetime_text = now.strftime("%Y%m%d-%H%M%S")

base_name = svg_file.replace(".svg", "")
output_pdf = base_name + "_" + datetime_text + ".pdf"


# VARIABLES MOIFIABLES SELON VOTRE UTILISATION
varPagesLayer = "Pages"         # Nom par défaut du calque contenant les rectangles des pages
varPagesObjectPrefix = "Page"   # préfixe par défaut des rectangles de pages dans le calque des pages
scale_svg = 0.264585            # visible dans les propriétés du document : à modifier si différent
page_margin = 10                # 10 = 1 cm


# SCRIPT D'EXPORT SU SVG EN PDF AVEC OCG (Calques)
def svg_to_vector_pdf(svg_path, output_pdf_path):
    tree = etree.parse(svg_path)
    root = tree.getroot()
    ns = {
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
    }

    all_layers = root.xpath("//svg:g[@inkscape:groupmode='layer']", namespaces=ns)
    pages_layer = next((layer for layer in all_layers if layer.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label', '') == varPagesLayer), None)
    if pages_layer is None:
        print("❌ Calque 'Pages' introuvable.")
        return

    # Recherche les objets dont le label (ou l'id) commence par 'pages' dans le calque "Pages" identifié précédemment dans la variable pages_layer
    page_rects = []
    for rect in pages_layer.xpath(".//svg:rect", namespaces=ns):
        try:
            rect_label = rect.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label')
            check_rect = rect_label.startswith(varPagesObjectPrefix)
        except:
            rect_label = rect.attrib.get('id', '')
            check_rect = rect_label.startswith(varPagesObjectPrefix)
        if check_rect:
            page_rects.append({
                'id': rect_label,
                'x_mm': float(rect.attrib.get('x', '0')),
                'y_mm': float(rect.attrib.get('y', '0')),
                'width_mm': float(rect.attrib.get('width', '180')),
                'height_mm': float(rect.attrib.get('height', '240'))
            })

    #content_layers = [layer for layer in all_layers if layer != pages_layer]
    #content_layers = list(reversed([layer for layer in all_layers])) → cette méthode inversait l'ordre des calques mais avec pour effet de changer l'ordre des objets
    content_layers = [layer for layer in all_layers]

    doc = fitz.open()

    ocg_map = {}
    #for layer in content_layers:
    for layer in reversed(content_layers):
        label = layer.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label', 'Calque')
        layer_style = layer.attrib.get('style')
        if layer_style == 'display:none':
            ocg_map[label] = doc.add_ocg(label, on=False)  # Calque masqué par défaut
        else:
            if layer == pages_layer:
                continue
            else:
                ocg_map[label] = doc.add_ocg(label)

    with tempfile.TemporaryDirectory() as tmpdirname:
        for i, page in enumerate(page_rects):
            page_id = page['id']
            margin_mm = page_margin / scale_svg

            # Dimensions avec marges en mm
            x_mm = page['x_mm'] - margin_mm
            y_mm = page['y_mm'] - margin_mm
            width_mm = page['width_mm'] + 2 * margin_mm
            height_mm = page['height_mm'] + 2 * margin_mm

            # Conversion mm → pt (pour PyMuPDF)
            mm_to_pt = 2.83465 * scale_svg
            width_pt = width_mm * mm_to_pt
            height_pt = height_mm * mm_to_pt
            margin_pt = margin_mm * mm_to_pt

            # Conversion mm → px (pour CairoSVG)
            mm_to_px = 3.7795 * scale_svg
            width_px = width_mm * mm_to_px
            height_px = height_mm * mm_to_px

            pdf_page = doc.new_page(width=width_pt, height=height_pt)

            for j, layer in enumerate(content_layers):
                for g in all_layers:
                    g.attrib['style'] = 'display:none'
                layer.attrib['style'] = 'display:inline'

                # Supprimer tous les éléments avec style="display:none"
                for elem in root.xpath(".//*"):
                    style = elem.attrib.get('style', '').replace(" ", "")
                    is_layer = elem.tag.endswith('g') and elem.attrib.get(
                        '{http://www.inkscape.org/namespaces/inkscape}groupmode') == 'layer'
                    if 'display:none' in style and not is_layer:
                        parent = elem.getparent()
                        if parent is not None:
                            parent.remove(elem)

                root.attrib['viewBox'] = f"{x_mm} {y_mm} {width_mm} {height_mm}"
                root.attrib['width'] = f"{width_mm}mm"
                root.attrib['height'] = f"{height_mm}mm"

                temp_svg_path = os.path.join(tmpdirname, f"{page_id}_layer_{j}.svg")
                tree.write(temp_svg_path)

                temp_pdf_path = os.path.join(tmpdirname, f"{page_id}_layer_{j}.pdf")
                cairosvg.svg2pdf(
                    url=temp_svg_path,
                    write_to=temp_pdf_path,
                    output_width=int(width_px),
                    output_height=int(height_px),
                    scale=1.0
                )

                # Insérer le PDF vectoriel dans la page PDF avec l'OCG global
                label = layer.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label', 'Calque')
                #ocg = ocg_map[label]

                with open(temp_pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                layer_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                if layer != pages_layer:
                    ocg = ocg_map[label]
                    pdf_page.show_pdf_page(fitz.Rect(0, 0, width_pt, height_pt), layer_doc, 0, oc=ocg)
                else:
                    pdf_page.show_pdf_page(fitz.Rect(0, 0, width_pt, height_pt), layer_doc, 0)

                # Dessiner le fond blanc dans la marge par 4 rectangles
                # paramètres = alignement vertical (distance du bord gauche) / alignement horizontal (distance du haut) / position Largeur du 2éme point / position Hauteur du 2éme point
                pdf_page.draw_rect(fitz.Rect(0, 0, width_pt, margin_pt*0.997), fill=(1, 1, 1), color=None)  # En haut
                pdf_page.draw_rect(fitz.Rect(0, 0, margin_pt*0.997, height_pt), fill=(1, 1, 1), color=None)  # à gauche
                pdf_page.draw_rect(fitz.Rect(0, height_pt*1.001 - margin_pt, width_pt, height_pt), fill=(1, 1, 1), color=None)  # En bas
                pdf_page.draw_rect(fitz.Rect(width_pt*1.002 - margin_pt, 0, width_pt, height_pt), fill=(1, 1, 1), color=None)  # A droite

                pdf_page.insert_link({
                    "from": fitz.Rect((margin_mm+5) * mm_to_pt, (margin_mm+5) * mm_to_pt, (margin_mm+15) * mm_to_pt, (margin_mm+15) * mm_to_pt),  # zone cliquable en points
                    "uri": "https://test.com",
                    "kind": fitz.LINK_URI
                })

            layer_doc.close()

    doc.save(output_pdf_path)
    print(f"✅ PDF vectoriel multi-pages créé : {output_pdf_path}")


# EXECUTION DU SCRIPT
if os.path.exists(svg_file):
    svg_to_vector_pdf(svg_file, output_pdf)
else:
    print(f"❌ Fichier SVG introuvable : {svg_file}")

time.sleep(8)
# Après génération, ouvrir le PDF avec NotePad++ et modifier la 1ère ligne juste sous '1 0 obj' : à la fin, remplacer >> par /PageLayout /SinglePage/PageMode /UseOC>>