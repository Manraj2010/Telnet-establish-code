from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException
from paramiko import SSHClient, AutoAddPolicy
import time
import getpass

# Define the device information
device_info = {
    'device_type': 'cisco_ios',
    'ip': '192.168.56.101',
    'username': getpass.getpass('Enter Username: '),
    'password': getpass.getpass('Enter Password: '),
    'secret': getpass.getpass('Enter Enable Password: '),
    'timeout': 120,
}

# Define the maximum number of connection retries
max_retries = 3

# Custom SSH client that auto-accepts keys
class MySSHClient(SSHClient):
    def load_system_host_keys(self):
        pass

    def missing_host_key(self, hostname, key):
        self._policy = AutoAddPolicy()
        return 'a'

for retry in range(max_retries):
    try:
        # Create a Netmiko SSH session using the custom SSH client
        ssh_session = ConnectHandler(**device_info, ssh_strict=False, session_cls=MySSHClient)
        ssh_session.enable()

        # Introduce a delay for stability
        time.sleep(2)

        # Send a command to change the hostname
        new_hostname = 'R2'
        config_commands = [f'hostname {new_hostname}']
        ssh_session.send_config_set(config_commands)

        # Introduce a delay for stability
        time.sleep(2)

        # Send a command to output the running configuration
        output = ssh_session.send_command('show running-config')

        # Save the running configuration to a file
        output_file = 'running_config.txt'
        with open(output_file, 'w') as config_file:
            config_file.write(output)

        # Exit enable mode
        ssh_session.exit_enable_mode()

        # Disconnect from the device
        ssh_session.disconnect()

        # Display the information
        print('------------------------------------------------------')
        print('{:<20} {:<15} {:<15}'.format('Device IP', 'Username', 'Enable Password'))
        print('{:<20} {:<15} {:<15}'.format(device_info['ip'], device_info['username'], '********'))
        print('--- Running Configuration saved to:', output_file)
        print('--- Hostname changed to:', new_hostname)
        print('------------------------------------------------------')

        # Break out of the retry loop if successful
        break
    except SSHException as e:
        print(f"Connection attempt {retry + 1} failed. Error: {e}")
        if retry < max_retries - 1:
            print("Retrying...")
            time.sleep(5)
        else:
            print("Maximum retries reached. Unable to establish a connection.")
            exit(1)
