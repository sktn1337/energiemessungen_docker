package main

import (
	_"fmt"
	_"html"
	"strconv"
	"log"
	"net/http"
	"encoding/json"
	"database/sql"
        "math/rand"
	"os"
	_ "github.com/go-sql-driver/mysql"
)

type Output struct{
	ID	string `json:"id"`
	VALUE	string `json:"value"`
}

func main(){	
	log.SetOutput(os.Stdout)

	http.HandleFunc("/",Index)
	http.HandleFunc("/insert/",Insert)
	log.Fatal(http.ListenAndServe(":9000",nil))
}


func Index(w http.ResponseWriter, r * http.Request){
	w.Header().Set("Content-Type", "application/json")


	driver:="mysql"
	connection:="root:123456@tcp(db:3306)/Messungen"
	
	db, err := sql.Open(driver,connection)
        defer db.Close()
        if err != nil{
                panic(err)
        }
	

	sqlState := `SELECT Szenario, Beschreibung FROM Messrunde`
	rows, err := db.Query(sqlState)
	defer rows.Close()
	
	var outputs []Output
	for rows.Next() {
        	var id int
        	var beschreibung string

        	err = rows.Scan(&id, &beschreibung)
		if err != nil {
			panic(err)
		}

		var out Output
		out.ID=strconv.Itoa(id)
		out.VALUE=beschreibung
        	outputs = append(outputs,out) 
    	}

     	err = rows.Err() 
	if err !=nil {
		panic(err)
	}
        log.Println("data read")
	json.NewEncoder(w).Encode(outputs)
}

func Insert(w http.ResponseWriter, r * http.Request){
        w.Header().Set("Content-Type", "application/json")

        driver:="mysql"
        connection:="root:123456@tcp(db:3306)/Messungen"

        db, err := sql.Open(driver,connection)
        defer db.Close()
        if err != nil{
                panic(err)
        }

        number := rand.Intn(10000)
        sqlState := "INSERT INTO `Messrunde`(`Szenario`, `Beschreibung`, `WattMittelwert`, `HitsMittelwert`) VALUES (1,\"RESTAPI Insert Test\",0.0,0)"
        insert, err2 := db.Query(sqlState)
        defer insert.Close()

	if err2 != nil{
		panic (err2)
	}
	var output []Output
        var out Output
        out.ID="-1"
	out.VALUE=strconv.Itoa(number)
        output=append(output,out)
	log.Println("data written")
        json.NewEncoder(w).Encode(output)
}
