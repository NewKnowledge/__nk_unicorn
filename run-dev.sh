docker pull newknowledge.azurecr.io/ds/cluster-db-dev:seed-latest
docker pull newknowledge.azurecr.io/ds/social-db-dev:seed-dev
docker-compose down -v --remove-orphans 
docker-compose up --build
# docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml down -v --remove-orphans 
# docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up --build 