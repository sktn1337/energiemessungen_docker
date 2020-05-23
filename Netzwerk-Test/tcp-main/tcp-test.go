package main

import (
	"bufio"
	"fmt"
	"net"
	_"net/http"
	_"html/template"
	"io"
	_"io/ioutil"	
	"strconv"
	_"strings"
	"time"
	"log"	
	"os"
	
)
var Info *log.Logger
var rounds = 0
var text = "default"
var answer_checked = make(chan bool)
var answer_text = make(chan string)
var time_start = time.Now()
var elapsed =time.Since(time_start)

var start =make(chan int)
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


func tcp_server(port string){
	
	//fmt.Println("Launching server...<br>")
	listener, err :=net.Listen("tcp", port)
	if err!=nil {
		log.Fatal(err)
	} else {//fmt.Println("Connection to Client established")
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

func connection_to_the_outside(){

	//fmt.Println("Launching server...<br>")
	listener, err :=net.Listen("tcp", ":9000")
	if err!=nil {
		log.Fatal(err)
	} else {//fmt.Println("Connection established")
		for{	
			conn, _ := listener.Accept()		
	                
			conn.Write([]byte("Der Server ist bereit eine den Start einer Messrunde entgegen zu nehmen\n"))	
			/*message, _ := bufio.NewReader(conn).ReadString('\n')			
			if len(message)==0{
				return;
			}
			if(len(string(message))>0){
				i , err := strconv.Atoi(strings.TrimSpace(message))			
				if err==nil {
				       	conn.Write([]byte("Messung gestartet\n"))	
					start <- i
				} else { 
					log.Fatal(err)
				}
			}*/
			conn.Write([]byte("Messung gestartet\n"))
			start <- 1
			newmessage := "default"
			newmessage = <- answer_text
			conn.Write([]byte(newmessage+"\n"))
			
			conn.Close()
		}
	}
}


func main(){
	Log_Init(os.Stdout)

	serverPort := ":8080"
        //fmt.Println("Enter a server port (: at the beginning): ")
        //fmt.Scanf("%s\n",&serverPort)
	serverPort = os.Args[1]
        clientIP := "127.0.0.1:8081"
        //fmt.Println("Enter a client IP (with port): ")
        //fmt.Scanf("%s\n",&clientIP)
	clientIP=os.Args[2]

	go tcp_server(serverPort)
	
	go connection_to_the_outside()	

	//erstelle TCP-Client
	conn, err := net.Dial("tcp",clientIP)
	for err!=nil {
		conn, err = net.Dial("tcp",clientIP)	
	}
	
	for {	//fmt.Println("Connection to Server established")
		text="Test"
		rounds = <- start
		/*fmt.Println("Enter Number of Rounds:")
		fmt.Scanf("%d\n",&rounds) 
		fmt.Println("Test startet")*/
		//Zeit wird gestoppt
		time.Sleep(10*time.Second)
		for i:=0;i<1;i++ {			
			time_start= time.Now()
			answer:=time_start.Format("2006-01-02 15:04:05.999999")+"; start Testrun; Runden: \n"
			//Info.Println(answer)
			rounds=0
			for {
				fmt.Fprintf(conn,text+"\n")
				if time.Since(time_start)>1*time.Minute{
					break
				}
				<-answer_checked
				rounds++
			}
			//Zeit wir wieder gestoppt	
			elapsed=time.Since(time_start)
			answer2:=time.Now().Format("2006-01-02 15:04:05.999999")+"; stop Testrun; Dauer: "+elapsed.String()+"; Anzahl Runden:"+strconv.Itoa(rounds)+"\n"
			//Info.Println(answer2)
		
			answer_text <- answer+answer2
			//fmt.Println(elapsed)
			time.Sleep(time.Second)
		}
	}
}
