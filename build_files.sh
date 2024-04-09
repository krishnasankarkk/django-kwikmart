echo "BUILD START"
    python3 -m venv .venv
source .venv/bin/activate  
./.venv/bin/python3 -m pip install --upgrade pip
./.venv/bin/python3 -m pip install -r requirements.txt
./.venv/bin/python3 manage.py makemigrations
./.venv/bin/python3 manage.py migrate
./.venv/bin/python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
