# Trabalho Final de Data Warehousing e Inteligência de Negócio - ICP357

## Descrição

Este projeto tem como objetivo implementar um ambiente analítico a partir de dados reais, passando por todas as fases de um projeto de solução analítica: coleta, tratamento, transformação e análise dos dados. O ambiente analítico será direcionado a um tomador de decisão, permitindo a exploração dos dados usando ferramentas de alto nível.

## Objetivo Geral

Implementar um ambiente analítico a partir de dados reais, executando todas as fases usuais em um projeto de solução analítica, desde a coleta dos dados, passando pelas tarefas de tratamento e transformação, até a análise.

## Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina as seguintes ferramentas:

- [Python](https://www.python.org/downloads/) (versão 3.x)
- [Prisma](https://www.prisma.io/docs/getting-started/setup-prisma/start-from-scratch/relational-databases-typescript-sqlite) CLI
- [SQLite](https://www.sqlite.org/index.html)

## Instalação

Siga estas etapas para configurar o ambiente de desenvolvimento e executar o projeto.

### Clonando o Projeto

Para obter uma cópia do projeto em sua máquina local, primeiro clone o repositório do GitHub:

```bash
git clone https://github.com/Nyon0k/trabalho_final_datawarehouse.git
cd trabalho_final_datawarehouse
```

### Configurando o Ambiente Virtual

É recomendado utilizar um ambiente virtual para gerenciar as dependências do projeto de forma isolada. Você pode criar um utilizando o `venv`:

```bash
python3 -m venv venv
```

Após criar o ambiente virtual, ative-o:

- No Windows:

```bash
.\venv\Scripts\activate
```

- No Linux ou macOS:

```bash
source venv/bin/activate
```

### Instalando Dependências

Com o ambiente virtual ativado, instale as dependências do projeto utilizando o `pip`:

```bash
pip install -r requirements.txt
```

### Criando o Banco de Dados com Prisma

Para criar o banco de dados conforme definido no schema do Prisma, execute o seguinte comando:

```bash
prisma db push
```

Este comando irá criar o banco de dados SQLite `database.db` e aplicar o esquema definido no arquivo `schema.prisma`.

### Executando o Tratamento de Dados

Para executar o tratamento de dados, siga as seguintes etapas:

1. Certifique-se de ter todas as dependências instaladas e o ambiente virtual ativado.

2. Certifique-se de ter o arquvio correto de dados na pasta `dados`. Faça o download do .csv e salve no caminho `dados/dados_iqarj.csv`
   [https://datariov2-pcrj.hub.arcgis.com/datasets/PCRJ::qualidade-do-ar-dados-hor%C3%A1rios/about?layer=2](https://datariov2-pcrj.hub.arcgis.com/datasets/PCRJ::qualidade-do-ar-dados-hor%C3%A1rios/about?layer=2)

3. Execute o script `etl/etl.py`:

```bash
python etl/etl.py
```

Este script irá executar o processo de extração, transformação e carga dos dados, seguindo as regras definidas no código.

Após a execução bem-sucedida do script, os dados tratados estarão disponíveis para análise no ambiente analítico.

### Populando o Banco de Dados

Para popular o banco de dados, execute o script `etl/update_bd.py`:

```bash
python etl/update_bd.py
```

Este script irá inserir os dados iniciais no banco de dados.

## Executando o Projeto

Com todas as dependências instaladas e o banco de dados configurado, você está pronto para o projeto de análise. Para iniciar o processo, execute o script principal:

```bash
streamlit run bi.py
```
