docker build -t gofishing .
docker tag gofishing:latest lokispundit/gofishing
docker push lokispundit/gofishing
