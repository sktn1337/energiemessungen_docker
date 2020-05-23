package main

import(
	"net"
	"fmt"
	"bufio"
	"log"
	"strings"
	"sync"
	"os"
)

//Waitgroup wird benötigt um die main Funktion am laufen zu halten
var wg sync.WaitGroup
//dieser Channel wird benötigt, um die empfangene Nachricht weiterzuleiten
var circle_message = make(chan string)

//Diese Funktion sendet die gerade erhaltene Funktion an den nächsten Knoten weiter
func tcp_send(ip string){
	//Verbindung zum nächsten Knoten wird über IP hergestellt
	conn, err := net.Dial("tcp",ip)
	//wiederhole den Verbindungsversuch
	for err!=nil {
		//log.Fatal(err)
		conn, err = net.Dial("tcp",ip)	
	}
	//warte den erhalt einer Nachricht
	for {	
		// Channel wird nach Nachricht abgehört (block bis Nachricht erhalten)
		text := <-circle_message
		// Trimme die Nachricht
		text=strings.TrimRight(text,"\n")
		//Hänge eine 1 hinten an
		text = text+"1"	
		//verschicke Nachricht 
		fmt.Fprintf(conn,text+"\n")
		
	}
}

//Starte TCP server der auf eine ankommende Nachricht wartet
func tcp_server(port string){
	
	//fmt.Println("Lauching server...")
	//starte Server mit Port port
	listener, err :=net.Listen("tcp", port)
	// Startet der Server nicht, breche ab	
	if err!=nil {
		log.Fatal(err)
	} else {
		//erzeuge Listener auf dem Server
		//fmt.Println("Verbindung erstellt")		
		conn, _ := listener.Accept()		
		for {
			//horsche auf NachrichtcJs3hJt_
			message, _ := bufio.NewReader(conn).ReadString('\n')
			// Falls die Verbindung unverhofft abbricht, dient die Laenge des Strings als  Shcutzmechanismus			
			if len(message)==0{
				break;
			}
			//fmt.Print("Message received:", string(message))
			//schmeisse Nachricht auf den Channel
			circle_message <- string(message)	
		}
		//Signalisiere Waitgroup, dass abgebrochen wurde
		wg.Done()
	}
}

func main(){	
	wg.Add(1)
	serverPort := ":8080"
	//Lese Parameter bzgl ServerPort von der Konsole aus: Form :8080
	serverPort = os.Args[1]
	clientIP := "127.0.0.1:8081"
	//Lese Parameter bzgl ClientIP von der Konsole aus: Form 128.232.21.2:8080
	clientIP = os.Args[2]

	//start Server und Client nebenläufig
	go tcp_server(serverPort)
	go tcp_send(clientIP)
	//Halte main am laufen, solange der Server läuft
	wg.Wait()
}
