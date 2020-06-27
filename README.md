#Zapizza2.0

Setup Linux
-----------------

Dá teus pulo aí...


Setup Windows
--

**Instalar requisitos Python3.6 e Git client**

Fazer download  e instalar ultima versao 3.6+ (Adicionar python ao PATH) de https://www.python.org/downloads/windows/

Fazer Download e instalar o GIT client de https://git-scm.com/download/win

**Configurar ambiente de desenvolvimento** 

Abrir PowerShell Windows.

**Testar versão Python instalada**
```bash
python --version
```

**Testar versão Git Client instalada**
```bash
git --version
```

**Criar pasa dos projetos e ambientes virtuais (opcional)**
```bash
cd ~
mkdir Mocca
cd Mocca
```

**Clona repositório no BitBucket**

git clone https://bitbucket.org/zamopiccazzateam/zapizza-2.0

**Atualiza pip (opcional)**
`python -m pip install --upgrade pip`

**Criar ambiente virtual Pyhton**
```bash
python -m venv env36
```

**Ativa ambiente virtual **

Esse passo deve ser feito sempre antes de qualquer alteração/execução do projeto
```bash
.\env36\Scripts\activate.bat
```

**Instala dependecias do projeto**
```bash
cd zapizza-2.0
pip install -e . -r requirements.txt
```

**Instancia banco de dados de desenvolvimento com dados de exemplo importados dos modelos**
```bash
initialize_db.exe .\development.ini
```

**Inicia servidor**
```bash
pserve.exe .\development.ini --reload
```

Sistema é disponibilizado em http://127.0.0.1:6543

Se você chegou até aqui fique feliz :)



Deploy em Heroku
-----------------
Os arquivos abaixo são exclusivamente utilizados para deploy da aplicação em stack Heroku
```bash
Procfile
run
runapp
production_heroku.ini
```
Baseado em: https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/deployment/heroku.html

Comandos úteis
```bash
git push heroku master
snap run heroku open
snap run heroku logs -t
snap run heroku pg:psql
snap run heroku bash
snap run heroku python
```
