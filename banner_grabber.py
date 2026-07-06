import socket

def grab_banner(target_ip, target_port):
    try:
        # 1. Create the socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Set a timeout (so the script doesn't hang forever if a port is closed)
        s.settimeout(3.0)
        
        # 3. Connect to the target IP and Port
        print(f"[*] Connecting to {target_ip} on port {target_port}...")
        s.connect((target_ip, target_port))
        
        # 4. Receive the banner data (1024 bytes is usually plenty)
        # .decode() converts the raw bytes from the network into a readable string
        banner = s.recv(1024).decode('utf-8', errors='replace').strip()
        
        # 5. If it's empty, send a generic probe to trigger an active response
        if not banner:
          s.send(b"GET / HTTP/1.1\r\n\r\n") # Generic probe
          banner = s.recv(1024).decode('utf-8', errors='replace').strip()
        
        return banner if banner else "Connected, but port remained silent."
        

    except socket.timeout:
        return "Error: Connection timed out (No banner received)."
    except ConnectionRefusedError:
        return "Error: Connection refused (Port might be closed)."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # 5. Always close the connection when done
        s.close()

if __name__ == "__main__":
    print("=== Welcome to the Advanced Banner Grabbing Tool ===")
    
    # Get target details from user
    target_host = input("Enter target IP address or hostname (e.g., scanme.nmap.org): ")
    
    print("\nSelect Port Scanning Option:")
    print("1. Scan default common ports (21, 22, 80)")
    print("2. Enter custom ports manually")
    choice = input("Enter your choice (1 or 2): ")
    
    ports_to_scan = []
    
    if choice == '1':
        ports_to_scan = [21, 22, 80]
    elif choice == '2':
        # Get custom ports as a string (e.g., "22, 80, 443")
        custom_input = input("Enter ports separated by commas (e.g., 22, 80, 443): ")
        
        # Split the string by commas, remove spaces, and convert them to integers
        try:
            ports_to_scan = [int(port.strip()) for port in custom_input.split(",")]
        except ValueError:
            print("[-] Error: Invalid port input. Please enter numbers only.")
            exit()
    else:
        print("[-] Invalid choice. Exiting script.")
        exit()
        
    print(f"\nStarting enumeration on target: {target_host}")
    print("-" * 50)
    
    for port in ports_to_scan:
        result = grab_banner(target_host, port)
        print(f"[+] Port {port}: {result}")
        print("-" * 50)