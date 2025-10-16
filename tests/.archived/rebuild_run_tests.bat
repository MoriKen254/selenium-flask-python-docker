docker compose down
docker compose build
docker compose up -d
docker build -t todo-tests .
timeout /t 30
run_unit_tests.bat
run_integration_tests.bat
