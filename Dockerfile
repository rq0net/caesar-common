#
# The doc: https://docs.docker.com/engine/reference/builder/#usage
# Dockerfile-ceser-subscription
# Help from: https://www.eidel.io/2017/07/10/dockerizing-django-uwsgi-postgres/
#

FROM rq0net/p3d2-alpine

RUN apk --no-cache add curl

EXPOSE 3000

CMD ["uwsgi", "--ini", "/app/common.ini"]
