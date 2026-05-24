#!/bin/bash
echo ""
echo " Iniciando Uandra Tasks..."
echo ""

pip install django -q 2>/dev/null || pip3 install django -q

if [ ! -f db.sqlite3 ]; then
    python manage.py migrate -v 0 2>/dev/null || python3 manage.py migrate -v 0
    python seed.py 2>/dev/null || python3 seed.py
fi

echo " Acesse: http://localhost:8000"
(sleep 2 && (xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null)) &
python manage.py runserver 2>/dev/null || python3 manage.py runserver
