#HP-10.0.0.54-192.168.141.161
#TOSHIBA-10.0.0.57-
#LG-10.0.0.50-192.168.141.25
#XIAOMI-10.0.0.52-
#LENOVO-10.0.0.52-192.168.141.225
import socket
import threading

class PeerToPeerChat:
    def __init__(self, own_ip, own_port):
        """
        Inicializa la clase PeerToPeerChat con la dirección IP y puerto propios,
        así como las listas para almacenar vecinos y mensajes recibidos.
        """
        self.own_ip = own_ip
        self.own_port = own_port
        self.neighbours = {}  # Almacena los nombres de los vecinos y sus direcciones IP y puertos
        self.received_messages = set()  # Almacena los mensajes recibidos para evitar reenviarlos

    def send_message(self, destination_name, message):
        """
        Envía un mensaje al vecino especificado.
        """
        try:
            # Obtiene la dirección IP y puerto del vecino destinatario
            destination_ip, destination_port = self.neighbours.get(destination_name, (None, None))
            if destination_ip and destination_port:
                # Verifica si la conexión con el vecino está activa
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)  # Establece un tiempo de espera de 1 segundo
                    result = s.connect_ex((destination_ip, destination_port))
                    if result == 0:
                        s.send(message.encode())
                        print(f"Mensaje enviado a {destination_name}: {message}")
                    else:
                        print(f"Error: No hay conexión con {destination_name}")
            else:
                print(f"Error: No se encontró el vecino {destination_name}")
        except ConnectionRefusedError:
            print(f"Error: No se pudo conectar con {destination_name}")

    def handle_client(self, client_socket, client_address):
        """
        Maneja la conexión del cliente. Recibe mensajes entrantes.
        """
        while True:
            try:
                # Recibe mensajes del cliente
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"\nMensaje recibido de {client_address}: {message}")
                    
                    # Verifica si el mensaje ya se ha recibido antes
                    if message not in self.received_messages:
                        self.received_messages.add(message)

            except ConnectionResetError:
                print(f"Conexión perdida con {client_address}")
                break

    def start_listening(self):
        """
        Inicia un servidor para escuchar conexiones entrantes de otros pares.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.own_ip, self.own_port))
            server_socket.listen()
           
            
            while True:
                # Acepta conexiones entrantes y maneja cada una en un hilo separado
                client_socket, client_address = server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                thread.start()
                print(f"Conexión establecida con {client_address}")

    def add_neighbour(self, neighbour_name, neighbour_ip, neighbour_port):
        """
        Agrega un nuevo vecino a la lista de vecinos.
        """
        self.neighbours[neighbour_name] = (neighbour_ip, neighbour_port)
        print(f"Vecino añadido: {neighbour_name} ({neighbour_ip}:{neighbour_port})")

    def show_neighbours(self):
        """
        Muestra la lista de vecinos y su estado de conexión.
        """
        print("\nLista de Vecinos:")
        for name, (ip, port) in self.neighbours.items():
            if self.check_connection(ip, port):
                print(f"{name}: {ip}:{port} - Activo")
            else:
                print(f"{name}: {ip}:{port} - Sin conexión")

    def start_chat(self):
        """
        Inicia el chat permitiendo al usuario enviar mensajes a los vecinos.
        """
        while True:
            destination_name = input("\nIngrese el nombre del destino (o 'list' para ver vecinos, o 'menu' para volver al menú principal): ")
            if destination_name.lower() == 'list':
                self.show_neighbours()
            elif destination_name.lower() == 'menu':
                break
            else:
                message = input("Ingrese su mensaje: ")
                self.send_message(destination_name, message)

    def check_connection(self, ip, port):
        """
        Verifica si hay conexión con un vecino específico.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Establece un tiempo de espera de 1 segundo
                result = s.connect_ex((ip, port))
                return result == 0
        except:
            return False

if __name__ == "__main__":
    own_ip = input("Ingrese su dirección IP: ")
    own_port = int(input("Ingrese su puerto: "))
    peer = PeerToPeerChat(own_ip, own_port)

    # Inicia un hilo para que el servidor esté escuchando conexiones entrantes
    t1 = threading.Thread(target=peer.start_listening)
    t1.start()

    print("\nServidor iniciado. Esperando conexiones...")

    while True:
        # Presenta un menú interactivo para que el usuario realice acciones
        print("\nMENU:")
        print("1. Agregar vecino")
        print("2. Ver vecinos")
        print("3. Enviar mensaje")
        print("4. Salir")
        choice = input("Ingrese el número de la opción que desea: ")
        
        if choice == "1":
            # Agrega un nuevo vecino
            neighbour_name = input("Ingrese el nombre del vecino: ")
            neighbour_ip = input("Ingrese la dirección IP del vecino: ")
            neighbour_port = int(input("Ingrese el puerto del vecino: "))
            peer.add_neighbour(neighbour_name, neighbour_ip, neighbour_port)
        elif choice == "2":
            # Muestra la lista de vecinos y su estado de conexión
            peer.show_neighbours()
        elif choice == "3":
            # Inicia el chat
            peer.start_chat()
        elif choice == "4":
            # Sale del programa
            break
        else:
            print("Opción no válida. Por favor ingrese un número del 1 al 4.")

