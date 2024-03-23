echo "BUILD START"
source .venv/bin/activate  
./.venv/bin/python3 -m manage collectstatic --noinput --clear
echo "BUILD END"