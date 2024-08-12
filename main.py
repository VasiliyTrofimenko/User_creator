import subprocess 
import ipaddress
import configparser

print ("Print user name of peer") 
user_name = input("User name: ")
#gen private and public key
print(subprocess.run([f"wg genkey | tee /etc/wireguard/keys/{user_name}privatekey | wg pubkey | tee /etc/wireguard/keys/{user_name}publickey"], shell=True))

with open(f"{user_name}privatekey") as file:
    privatekey = file.read()
    print(f"prKey: {privatekey}")  
with open(f"{user_name}publickey") as file:
    publickey = file.read()
    print(f"pubKey: {privatekey}")

#find last AllowedIPs
with open('wg0.conf', 'r') as config_file:
    last_allowed_ip = None
    for line in config_file:
        if line.startswith('AllowedIPs = '):
            last_allowed_ip = line.strip().split(' = ')[1]
#spilit ipaddress and subnet mask
    ip_address, subnet_mask = last_allowed_ip.split('/')
    ip_address = ipaddress.ip_address(ip_address) #convert to ipaddress
    subnet = ipaddress.IPv4Network(f'{ip_address}/{subnet_mask}') #Join ipaddress and subnet mask
    next_allowed_ip = str(ipaddress.ip_address(int(ip_address) + 1))# increment ipaddress
    next_allowed_ip += f'/{subnet_mask}' #join ipaddress and subnet mask

#new peer record in wg0.conf
with open('wg0.conf', 'a') as configfile:
    configfile.write(f'\n#{user_name}\n')
    configfile.write('[Peer]\n')
    configfile.write(f'PublicKey = {publickey}\n')
    configfile.write(f'AllowedIPs = {next_allowed_ip}\n')
#reload server
print(subprocess.run(["sudo wg-quick down wg0 && sudo wg-quick up wg0"], shell=True))
print(subprocess.run(["sudo wg"], shell=True))

#new peer client
print(subprocess.run([f"touch {user_name}Connect"], shell=True))
with open(f'{user_name}Connect', 'a') as configfile:
    #interfase
    configfile.write('[Interface]\n')
    configfile.write(f'PrivateKey = {privatekey}\n')
    configfile.write(f'Address = {next_allowed_ip}\n')
    configfile.write(f'DNS = 8.8.8.8\n')
    #peer
    configfile.write('[Peer]\n')
    configfile.write(f'PublicKey = {privatekey}\n')#serverPublicKey
    configfile.write('Endpoint = \n')
    configfile.write('AllowedIPs = 0.0.0.0/0\n')
    configfile.write('PersistentKeepalive = 25\n')