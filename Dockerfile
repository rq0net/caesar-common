#
# The doc: https://docs.docker.com/engine/reference/builder/#usage
# Dockerfile-ceser-cdndomain
# Help from: https://www.eidel.io/2017/07/10/dockerizing-django-uwsgi-postgres/
#

FROM asia.gcr.io/project0215-10/p3d2:pipenv

EXPOSE 9000

WORKDIR /app

CMD ["daphne", "--application-close-timeout", "300", "-b", "0.0.0.0", "-p", "9000", "cdndomain.asgi:application"]