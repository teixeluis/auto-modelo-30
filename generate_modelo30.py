import argparse
import pandas
import os
import yaml
import zipfile


from xlsx2csv import Xlsx2csv
from xml.dom import minidom 
from datetime import datetime

TEMP_CSV = "temp.csv"
CONFIG_FILE = "config.yaml"


# Lê o ficheiro CSV, filtrando os dados relevantes para a declaração, e somando os valores
# de comissões relativos a cada beneficiário:

def process_csv(file, config, start_date, end_date):
    orig = pandas.read_csv(file)

    relevant_columns = orig.filter(items=['Reservado em', 'Canal', 'Comissão Canal'], axis=1)
    #relevant_columns['Reservado em'] = pandas.to_datetime(relevant_columns['Reservado em'], format='%d-%m-%Y')
    relevant_columns['Reservado em'] = pandas.to_datetime(relevant_columns['Reservado em'], format='mixed')

    # Registos por reserva com comissões para parceiros intracomunitários:
    
    # TODO obtain partners from the reference data
    
    beneficiarios = []

    for beneficiario in config.get('beneficiario', []):
        beneficiarios.append(beneficiario.get('nome'))

    items = []

    for beneficiario_name in beneficiarios:
        items.append(relevant_columns.loc[(relevant_columns['Canal'] == beneficiario_name) & (relevant_columns['Reservado em'] >= start_date) & (relevant_columns['Reservado em'] <= end_date)])

    records = pandas.concat(items)
    
    print(records)

    # Somam-se os rendimentos de cada beneficiário:

    result = records.groupby('Canal')['Comissão Canal'].sum()

    print(result)

    return result

# Carrega ficheiro yaml de configuração:

def load_config():
    with open(CONFIG_FILE, 'r') as stream:
        try:
            # Converts yaml document to python object
            config = yaml.safe_load(stream)
        
        # Printing dictionary
        #    print(config)

            return config
        except yaml.YAMLError as e:
            print(e)

# Obtém o campo desejado do dicionário:

def get_config_value(data, key, child_key, value, child_field):

    # Search for the entry with the specified nome
    child_field_value = None
    for entry in data.get(key, []):
        if entry.get(child_key) == value:
            child_field_value = entry.get(child_field)
            break

    return child_field_value

# Gera o XML da declaração Modelo 30:

def generate_modelo_30(data_frame, nif, date, serv_fin, decl_type, config, xml_file):
    decl = minidom.Document() 
  
    modelo30 = decl.createElement('Modelo30')
    modelo30.setAttributeNS("", "xmlns", "http://www.dgci.gov.pt/2002/OT")
    modelo30.setAttributeNS("xmlns", "xsi", "http://www.w3.org/2001/XMLSchema-instance")
    modelo30.setAttributeNS("xmlns", "schemaLocation", "http://www.dgci.gov.pt/2002/OT Modelo30.xsd")

    decl.appendChild(modelo30)
    
    # NIF do declarante:
    declarante = decl.createElement('Declarante')
    declarante.appendChild(decl.createTextNode(nif))
    modelo30.appendChild(declarante)

    dt = datetime.strptime(date, '%Y-%m-%d')

    # Ano da declaração:
    ano = decl.createElement('Ano')
    ano.appendChild(decl.createTextNode(str(dt.year)))
    modelo30.appendChild(ano)

    # SF = Serviço de Finanças:
    sf = decl.createElement('SF')
    sf.appendChild(decl.createTextNode(serv_fin))
    modelo30.appendChild(sf)

    # Tipo de declaração (1 = 1ª declaração do ano)
    tipo = decl.createElement('Tipo')
    tipo.appendChild(decl.createTextNode(decl_type))
    modelo30.appendChild(tipo)

    # Mês da declaração:
    mes = decl.createElement('Mes')
    mes.appendChild(decl.createTextNode(str(dt.month)))
    modelo30.appendChild(mes)

    # Registos dos rendimentos:

    curr_record = 1

    for i in data_frame.index:
        registo = decl.createElement('Registo')
        registo.setAttribute('numero', str(curr_record))
        
        beneficiario = decl.createElement('Beneficiario')

        beneficiario_nome = i
        beneficiario_nif = get_config_value(config, 'beneficiario', 'nome', beneficiario_nome, 'nif')
        beneficiario.appendChild(decl.createTextNode(beneficiario_nif))
        registo.appendChild(beneficiario)

        nif_estr = decl.createElement('NIFEstrangeiro')
        nif_estr_value = get_config_value(config, 'beneficiario', 'nome', beneficiario_nome, 'nif_estr')
        nif_estr.appendChild(decl.createTextNode(nif_estr_value))
        registo.appendChild(nif_estr)

        pais = decl.createElement('Pais')
        pais_value = get_config_value(config, 'beneficiario', 'nome', beneficiario_nome, 'pais')
        pais.appendChild(decl.createTextNode(pais_value))
        registo.appendChild(pais)

        tipo_rend = decl.createElement('TipoRend')
        tipo_rend_value = config.get('declaracao').get('tipo_rend')
        tipo_rend.appendChild(decl.createTextNode(tipo_rend_value))
        registo.appendChild(tipo_rend)

        rendimento = decl.createElement('Rendimento')
        rendimento_value = data_frame[i]
        rendimento.appendChild(decl.createTextNode(str(rendimento_value)))
        registo.appendChild(rendimento)

        tributacao = decl.createElement('Tributacao')
        tributacao_value = config.get('declaracao').get('tributacao')
        tributacao.appendChild(decl.createTextNode(tributacao_value))
        registo.appendChild(tributacao)

        modelo30.appendChild(registo)
        curr_record = curr_record + 1

    xml_str = decl.toprettyxml(indent ='\t')
        
    with open(xml_file, "w") as f: 
        f.write(xml_str)


def main():
    parser = argparse.ArgumentParser(description='Gera declaração Modelo 30 (XML) a partir de ficheiro Excel (XSLX) exportado do Talkguest.')

    parser.add_argument('talkguest_file', type=str,
                        help='ficheiro Excel do Talkguest')

    parser.add_argument('modelo_30_file', type=str,
                        help='ficheiro Modelo 30 a ser gerado')

    parser.add_argument('start_date', type=str,
                        help='Data inicio declaração')
    
    parser.add_argument('end_date', type=str,
                        help='Data fim declaração')
    
    args = parser.parse_args()

    config = load_config()

    Xlsx2csv(args.talkguest_file, outputencoding="utf-8").convert(TEMP_CSV)

    data_frame = process_csv(TEMP_CSV, config, args.start_date, args.end_date)

    # TODO Add these values to the reference data:
    generate_modelo_30(data_frame, config.get('declarante').get('nif'), args.start_date, config.get('declarante').get('sf'), config.get('declaracao').get('tipo'), config, args.modelo_30_file)

    with zipfile.ZipFile(args.modelo_30_file.replace('.xml', '.zip'), 'w') as myzip:
        myzip.write(args.modelo_30_file)

main()
