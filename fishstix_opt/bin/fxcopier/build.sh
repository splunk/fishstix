docker build -t fxcopier .
docker tag fxcopier:latest lokispundit/fxcopier
docker push lokispundit/fxcopier
