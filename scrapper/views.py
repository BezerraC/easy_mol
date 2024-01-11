import json
import os
from pathlib import Path

import pandas as pd
import pubchempy as pcp
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# from reportlab.pdfgen import canvas

#from xhtml2pdf import pisa

BASE_DIR = Path(__file__).resolve().parent.parent

def search(request):
    if request.method == 'POST':
        
        compostos = request.POST.get('molecules')
        print(f'compostos: {compostos}')
        compostos_lista = compostos.title().split(',')

        data_list = []
        queried_compounds = set()
        print(f'compostos_lista: {compostos_lista}')
        for composto in compostos_lista:
                if composto.strip() in queried_compounds:
                    continue

                queried_compounds.add(composto.strip())

                # Obtém os resultados para cada composto
                results = pcp.get_compounds(composto.strip(), 'name')
                print(f'results: {results}')
                print(f'composto.strip: {composto.strip()}')
                # Verifica  se há resultados antes de imprimir as informações
                if results:
                    for compound in results:
                        # Lipinski's rule of five conditions
                        h_bond_donors = compound.h_bond_donor_count
                        h_bond_acceptors = compound.h_bond_acceptor_count
                        molecular_mass = float(compound.molecular_weight)
                        partition_coefficient = compound.xlogp

                        # Check Lipinski's rule of five
                        conditions_met = 0

                        if h_bond_donors <= 5:
                            conditions_met += 1

                        if h_bond_acceptors <= 10:
                            conditions_met += 1

                        if molecular_mass < 500:
                            conditions_met += 1

                        if partition_coefficient <= 5:
                            conditions_met += 1

                        lipinski_pass = conditions_met >= 3
                        lipinski_rule_result = "0" if lipinski_pass else "1"
                        # Structure IMG
                        cid = compound.cid
                        img_path = f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={cid}&t=l"
                        # Synonyms
                        synonyms_list = compound.synonyms
                        synonyms = "; ".join(synonyms_list)
                        # Exact mass
                        exact_mass_f = float(compound.exact_mass)
                        exact_mass = "{:.2f}".format(exact_mass_f)
                        # Monoisotopic mass
                        monoisotopic_mass_f = float(compound.monoisotopic_mass)
                        monoisotopic_mass = "{:.2f}".format(monoisotopic_mass_f)

                        data = {
                            'Molecula': composto.strip(),
                            'Image_Path': img_path,
                            'Synonyms': synonyms,
                            'Molecular_Formula': compound.molecular_formula,
                            'Molecular_Weight': compound.molecular_weight,
                            'Canonical_SMILES': compound.canonical_smiles,
                            'Isomeric_SMILES': compound.isomeric_smiles,
                            'InChI': compound.inchi,
                            'InChIKey': compound.inchikey,
                            'IUPAC': compound.iupac_name,
                            'XLogP': compound.xlogp,
                            'Exact_Mass': exact_mass,
                            'Monoisotopic_Mass': monoisotopic_mass,
                            'TPSA': compound.tpsa,
                            'Hbond_Donors': compound.h_bond_donor_count,
                            'Hbond_Acceptors': compound.h_bond_acceptor_count,
                            'Rotatable_Bonds': compound.rotatable_bond_count,
                            'Linpiski_violations': lipinski_rule_result,
                        }

                        data_list.append(data)
                else:
                    error_message = f"Compound {composto.strip()} not found."
                    print(error_message)
                    return render(request, 'home.html', {'title': 'Searching Molecules', 'current_page': 'home', 'error_message': error_message})
                   


        # Adiciona a lista de dados capturados ao contexto
        context = {
            'message': 'Search completed successfully!',
            'data_list': data_list,
            'title': 'Result',
        }

        request.session['data_list'] = data_list

        return render(request, 'result.html', context)
    else:
        return render(request, 'home.html', {'title': 'Searching Molecules', 'current_page': 'home'})
    
def test(request):
    return render(request, 'test.html')
    
def replace_special_characters(text):
    # Substitua caracteres especiais por equivalentes comuns
    replacements = {
        'Å': 'A',
        # Adicione mais substituições conforme necessário
    }
    
    for key, value in replacements.items():
        text = text.replace(key, value)
    
    return text
def replace_specialsjson_characters(json_data):
    # Substitua caracteres especiais por equivalentes comuns
    replacements = {
        '\u212b': 'A',  # Unicode Å
    }

    for key, value in replacements.items():
        json_data = json_data.replace(key, value)

    return json_data


def download_file(request):
    download_type = request.POST.get('download_type')
    dfs = []
    if download_type == 'pdf':
        # Lógica para gerar o PDF
        # template_path = 'download_template.html'
        # data_list = request.session.get('data_list', [])
        # context = {'data_list': data_list}
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'

        # template = get_template(template_path)
        # html = template.render(context)

        # # Substitua caracteres especiais no HTML
        # html = replace_special_characters(html)

        # pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf-8')

        # if pisa_status.err:
        #     return HttpResponse('Erro ao gerar o PDF', status=500)

        # Gerar PDF com ReportLab
        # c = canvas.Canvas(response, pagesize=letter, bottomup=0)
        # textob = c.beginText()
        # textob.setTextOrigin(inch, inch)
        # textob.setFont("Helvetica", 12)

        # # Adicione os dados ao objeto textob
        # for item in data_list:
        #     for key, value in item.items():
        #         textob.textLine(f"{key}: {value}")
        #     textob.textLine("--------------------")

        # # Adicione o texto ao canvas
        # c.drawText(textob)
        # c.showPage()
        # c.save()

        # return response

        # Recupera a data_list da sessão
        data_list = request.session.get('data_list', [])

        # Configuração do PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio.pdf"'

        # Cria um objeto Canvas
        c = canvas.Canvas(response, pagesize=letter)

        # Adiciona os dados ao PDF
        y_position = 750  # Ajuste a posição inicial conforme necessário

        for item in data_list:
            for key, value in item.items():
                text = f"{key}: {value}"
                c.drawString(50, y_position, text)
                y_position -= 15  # Ajuste o espaçamento conforme necessário

            y_position -= 10  # Adiciona um espaço entre os itens

        # Salva o canvas como PDF
        c.save()
        return response

    elif download_type == 'csv':
    # Lógica para gerar o CSV
        data_list = request.session.get('data_list', [])
        context = {'data_list': data_list}
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="downloaded_file.csv"'

         # Cria o DataFrame
        df = pd.DataFrame(context)

        # Adiciona o DataFrame à lista
        dfs.append(df)
        # Concatena todos os DataFrames em um único DataFrame
        final_df = pd.concat(dfs, ignore_index=True)

        final_df.to_csv(response, index=False)
        return response

    elif download_type == 'json':
        # Lógica para gerar o JSON
        data_list = request.session.get('data_list', [])
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="downloaded_file.json"'

        # Adicione dados ao JSON
        json_data = json.dumps(data_list, indent=4)

        # Substitua caracteres especiais no JSON
        json_data = replace_specialsjson_characters(json_data)

        response.write(json_data)

        return response

    else:
        data_list = request.session.get('data_list', [])
        context = {'data_list': data_list, 'error_message': 'Tipo de download não suportado'}
        return render(request, 'result.html', context)
        # return HttpResponse('Tipo de download não suportado', status=400)

def home(request):
    return render(request, 'home.html', {'title': 'Searching Molecules', 'current_page': 'home'})

def features(request):
    return render(request, 'partials/coming_soon.html', {'title': 'Coming Soon', 'current_page': 'features'})

def about(request):
    return render(request, 'about.html', {'title': 'About', 'current_page': 'about'})