# Auto Modelo 30

## Descrição

Ferramenta de geração da declaração Modelo 30 da Autoridade Tributária com base ficheiro XLSX 
exportado do Talkguest.



## Requisitos

 * Python 3.10.6 ou superior;
 * Python PIP 22.0.2 ou superior;
 * Pacotes adicionais (ver abaixo).


## Instalação:

### Instalar as dependências fazendo:

```
$ pip install xlsx2csv pandas PyYAML
```

## Configuração

A aplicação espera um ficheiro config.yaml na mesma directoria, com a seguinte estrutura:

```
declarante:
  nif: '123456789'
  sf: '3212'

beneficiario:
  - nome: 'Booking.com'
    nif: '710671563'
    nif_estr: '805734958B01'
    pais: '528'
  - nome: 'Airbnb'
    nif: '712026681'
    nif_estr: '9827384L'
    pais: '372'

declaracao:
  tipo: '1'
  tipo_rend: '08'
  tributacao: '02'

```

Nele devem constar os detalhes do declarante, bem como os beneficiários (entitidades de países
dentro da união europeia dos quais adquire bens ou serviços), assim como as características
da declaração a aplicar em cada montante declarado. Estes valores devem estar consoante
a informação correcta para o caso do contribuinte.

## Utilização

A aplicação é executada a partir da linha de comandos, e a sua sintaxe é:

```
$ python3 generate_modelo30.py <ficheiro excel do Talkguest> <ficheiro XML Modelo 30> <data inicio declaração> <data fim declaração>
```

Por exemplo se quisermos gerar a declaração do mês de Abril de 2023:

```
$ python3 generate_modelo30.py lista_reservas.xlsx modelo30_230959709.xml '2023-04-01' '2023-04-30'
```

Para obter o ficheiro de reservas exportado do Talkguest, é necessario ir à secção  Reservas > Lista de Reservas na aplicação
Talkguest, e do lado superior direito da página, clicar em Ações > Exportar Reservas. Daí resultará o download do
ficheiro utilizado nesta aplicação.

**Nota:** O ficheiro xml da declaração deve sempre ser validado através da aplicação da autoridade 
tributária, que pode ser obtida aqui:

[https://oa.portaldasfinancas.gov.pt/mod30/downloads]([https://oa.portaldasfinancas.gov.pt/mod30/downloads])


## Limitações

 - Actualmente a aplicação apenas gera uma declaração de Modelo 30 valida para o caso em que 
   o contribuinte tem a prestação / aquisição de serviços intracomunitários habilitada
   para a sua actividade, e em que todas as as operações intracomunitárias consistam na liquidação
   de comissões. Quaisquer outros registos que devam constar da declaração, devem ser
   introduzidos manualmente pelo cliente.
