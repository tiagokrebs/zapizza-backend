#Zapizza2.0

SETUP WINDOWS 10
--

**Instalar requisitos Python3.6 e Git client**
Fazer download  e instalar ultima versao 3.6+ (Adicionar python ao PATH) de https://www.python.org/downloads/windows/
Fazer Download e instalar o GIT client de https://git-scm.com/download/win

**Configurar ambiente de desenvolvimento** 
Abrir PowerShell Windows. O PowerShell se assemelha ao linux porque integra comandos bash (cd, ls, rm, ...)

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
`python -m pip install --upgrade p`

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
python -m pip install --upgrade pip
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


Setup Linux
-----------------

Dá teus pulo aí...

