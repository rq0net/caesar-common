#

FROM rq0net/p3d2-alpine:pipenv

EXPOSE 9000

WORKDIR /app

CMD ["daphne", "-b", "0.0.0.0", "-p", "9000", "common.asgi:application"]
