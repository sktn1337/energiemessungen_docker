package main

import (
	"bufio"
	"fmt"
	"net"
	"net/http"
	"html/template"
	"io"
	"io/ioutil"	
	"strconv"
	"time"
	"log"	
	"os"
)
var Info *log.Logger
var rounds = 0
var start = make(chan bool)
var answer_checked = make(chan bool)
var time_start = time.Now()
var elapsed =time.Since(time_start)

//Struktur für die Dartstellung einer Html-Seite
type Page struct{
	Title string
	Body []byte
	data string
}

func Log_Init(infoHandle io.Writer){
	Info = log.New(infoHandle, "INFO: ",log.Ldate|log.Ltime|log.Lshortfile)
}

//tcp-client
func tcp_send(ip string){
	
	

	//erstelle TCP-Client
	conn, err := net.Dial("tcp",ip)
	for err!=nil {
		conn, err = net.Dial("tcp",ip)	
	}

	for {	
		text:="Test"
		//fmt.Println("blocked")
		<-start
		//fmt.Println("free")
		//Zeit wird gestoppt
		
					
		time_start= time.Now()
		Info.Println(time_start.Format(time.RFC3339)+"; start Testrun; Runden: "+strconv.Itoa(rounds)+"<br>")
		for i:=0;i<rounds;i++{
			fmt.Fprintf(conn,text+"\n")
			<-answer_checked
		}
		//Zeit wir wieder gestoppt	
		elapsed=time.Since(time_start)
		
		Info.Println(time.Now().Format(time.RFC3339)+"; stop Testrun; Dauer: "+elapsed.String()+"<br>")
		//fmt.Println(elapsed)
		
	}

	
}

func tcp_server(port string){
	fmt.Println("Lauching server...<br>")
	listener, err :=net.Listen("tcp", port)
	if err!=nil {
		log.Fatal(err)
	} else {
		conn, _ := listener.Accept()		
		for {
			message, _ := bufio.NewReader(conn).ReadString('\n')
			// Falls die Verbindung unverhofft abbricht			
			if len(message)==0{
				break;
			}
			
			//fmt.Print("Message received:", string(message),"<br>")
			//elapsed:=time.Since(time_start)
			//Info.Println(time.Now().Format(time.RFC3339)+"; stop Testrun; Dauer: "+elapsed.String()+"<br>")
			if(len(string(message))>0){
				answer_checked <- true
			}
			
		}
	}
}


func loadPage(title string) (*Page, error){
	filename:=title+".txt"
	body, err:= ioutil.ReadFile(filename)
	if err!=nil{
		return nil, err
	}
	return &Page{Title:title, Body: body},nil
}

//handler für die erste Seite
func http_view_handler(w http.ResponseWriter, r *http.Request){
	title := r.URL.Path[1:]
	p, err :=loadPage(title)
	if err!=nil{
		p = &Page{Title: title}	
	}
	t, _ := template.ParseFiles("main.html")
	t.Execute(w,p)
}

//in dieser FUnktion muss noch abgesichert werden, dass man nicht zwei aufträge zeitgleich starten kann
func round_handler(w http.ResponseWriter, r *http.Request){
	r.ParseForm()
	rounds, _ = strconv.Atoi(r.Form["rounds"][0])
	
	start<-true

	title := r.URL.Path[1:]
	p, err :=loadPage(title)
	if err!=nil{
		p = &Page{Title: title}	
	}
	p.data = "help"
	t, _ := template.ParseFiles("main.html")
	t.Execute(w,p)
}	




func main(){
	Log_Init(os.Stdout)

	go tcp_server(":8080")
	go tcp_send("127.0.0.1:8081")
	
	http.HandleFunc("/",http_view_handler)
	http.HandleFunc("/rounds",round_handler)
	
		
	fs:= http.FileServer(http.Dir("js/"))
	http.Handle("/static/",http.StripPrefix("/static/",fs))
	
	log.Fatal(http.ListenAndServe(":80",nil))
}		
