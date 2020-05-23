package main

import (
    "fmt"
    "log"
    "net/http"
)

func main() {
    http.Handle("/", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("[INFO]: Access on %q", r.RequestURI)
        fmt.Fprintf(w, "Hello world!")
    }))

    log.Println("[INFO]: Hello world app is running on port 8080")
    http.ListenAndServe(":8080", nil)
}
