cd C:\Users\revat\MyStore\pyapps\pulsex\backend

New-Item -ItemType Directory -Force .\app
New-Item -ItemType Directory -Force .\app\routers
New-Item -ItemType Directory -Force .\app\services
New-Item -ItemType Directory -Force .\app\models
New-Item -ItemType Directory -Force .\app\schemas

New-Item -ItemType File -Force .\app\__init__.py
New-Item -ItemType File -Force .\app\routers\__init__.py
New-Item -ItemType File -Force .\app\services\__init__.py
New-Item -ItemType File -Force .\app\models\__init__.py
New-Item -ItemType File -Force .\app\schemas\__init__.py