package main

import (
	"io"
	"log"
	"net"
	"time"
)

func main() {
	listener, _ := net.Listen("tcp", ":18080")
	defer listener.Close()
	
	log.Println("TCP proxy listening on :18080, 2s delay per connection")
	
	for {
		clientConn, _ := listener.Accept()
		go func(conn net.Conn) {
			defer conn.Close()
			log.Printf("New connection from %s - delaying 2s before backend connect", conn.RemoteAddr())
			
			// Delay before connecting to backend
			// This simulates slow connection establishment from client perspective
			time.Sleep(2 * time.Second)
			
			backend, err := net.Dial("tcp", "web:8080")
			if err != nil {
				log.Printf("Backend connection failed: %v", err)
				return
			}
			defer backend.Close()
			
			log.Printf("Connected to backend for %s", conn.RemoteAddr())
			
			// Bidirectional copy
			go io.Copy(backend, conn)
			io.Copy(conn, backend)
		}(clientConn)
	}
}