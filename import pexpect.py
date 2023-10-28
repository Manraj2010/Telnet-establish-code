from netmiko import ConnectHandler, NetMikoTimeoutException
import time
import getpass

# Define the device information
device_info = {
    'device_type': 'cisco_ios',
    'ip': '192.168.56.101',
    'username': getpass.getpass('Enter Username: '),
    'password': getpass.getpass('Enter Password: '),
    'secret': getpass.getpass('Enter Enable Password: '),
}

# Define a retry mechanism
retries = 3
timeout = 10

for attempt in range(retries):
    try:
        # Create a Netmiko SSH session
        ssh_session = ConnectHandler(**device_info, timeout=timeout)
        
        # Enter enable mode
        ssh_session.enable()
        
        # Send a command to change the hostname
        new_hostname = 'R2'
        config_commands = [f'hostname {new_hostname}']
        ssh_session.send_config_set(config_commands)
        
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
        
    except NetMikoTimeoutException as error:
        if attempt == retries - 1:
            raise error # If all attempts fail, raise the last exception
        else:
            time.sleep(2) # Wait for 2 seconds before the next attempt
            print(f'--- Attempt {attempt + 1} failed, retrying...')