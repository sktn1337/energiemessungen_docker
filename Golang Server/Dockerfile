FROM golang

WORKDIR /app
COPY server.go .
ARG CGO_ENABLED=0
RUN go build -o server .
EXPOSE 8080

CMD ./server
