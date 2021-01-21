# sse_schinder

## Installation

**Erstell eine virtaulenviroment:**  
`virtualenv venv`  
wenn das nicht geht, nimm  
`python3 -m venv venv`

Bei Windows:  
`python virtualenv venv`

**Virtualenviroment aktivieren:**  
`source venv/bin/activate`

Bei Windows:  
`./venv/scripts/acticate`
(oder so ähnlich)

**Requirements instalieren:**  
`pip install -r requirements.txt `

**Datenbank**  
Vor dem ersten starten muss die Datenbank initiert werden:  
`flask db init`

Darauf muss das Model migriert werden:  
`flask db migrate`

Und die Migationenen auf die DB angnewandt werden:  
`flask db upgrade`

## Anwendung starten 

Öffne ein Terminal in deiner Entwicklungumgebung und führe folgenden Befehl aus:  

`flask run`
