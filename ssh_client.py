"""
SSH Client for secure remote command execution
"""

import paramiko
import logging
import time
from typing import Dict, Optional, Union
import socket
from io import StringIO

class SSHClient:
    """Secure SSH client for remote command execution"""
    
    def __init__(self, hostname: str, username: str, password: str = None, 
                 key_filename: str = None, port: int = 22, timeout: int = 30):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout
        
        self.client = None
        self.connected = False
        
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': self.hostname,
                'port': self.port,
                'username': self.username,
                'timeout': self.timeout,
                'banner_timeout': 200,
                'auth_timeout': 60
            }
            
            if self.key_filename:
                connect_kwargs['key_filename'] = self.key_filename
            elif self.password:
                connect_kwargs['password'] = self.password
            else:
                raise ValueError("Must provide either password or key file")
            
            self.client.connect(**connect_kwargs)
            self.connected = True
            
            self.logger.info(f"Successfully connected to {self.hostname}:{self.port}")
            return True
            
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"SSH connection error: {e}")
            return False
        except socket.error as e:
            self.logger.error(f"Socket error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected connection error: {e}")
            return False
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Union[str, int]]:
        """Execute a command on the remote system"""
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to remote system")
        
        try:
            self.logger.debug(f"Executing command: {command}")
            
            # Execute command
            stdin, stdout, stderr = self.client.exec_command(
                command, 
                timeout=timeout,
                get_pty=True  # Get pseudo-terminal for better output
            )
            
            # Get output
            stdout_output = stdout.read().decode('utf-8', errors='ignore')
            stderr_output = stderr.read().decode('utf-8', errors='ignore')
            return_code = stdout.channel.recv_exit_status()
            
            result = {
                'stdout': stdout_output,
                'stderr': stderr_output,
                'return_code': return_code,
                'command': command
            }
            
            self.logger.debug(f"Command completed with return code: {return_code}")
            output_preview = '\n'.join(stdout_output.splitlines()[:10])
            self.logger.debug(f"Command output (first 10 lines):\n{output_preview}")
            return result
            
        except paramiko.SSHException as e:
            self.logger.error(f"SSH execution error: {e}")
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'command': command
            }
        except socket.timeout:
            self.logger.error(f"Command timed out after {timeout} seconds")
            return {
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'return_code': -2,
                'command': command
            }
        except Exception as e:
            self.logger.error(f"Unexpected execution error: {e}")
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -3,
                'command': command
            }
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to the remote system"""
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to remote system")
        
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            
            self.logger.info(f"Successfully uploaded {local_path} to {remote_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise e
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if a file exists on the remote system"""
        result = self.execute_command(f"test -f {remote_path}")
        return result['return_code'] == 0
    
    # TODO: this should not be in ssh_client as its unrelated to ssh/sftp functionality
    def get_system_info(self) -> Dict[str, str]:
        """Get basic system information"""
        info = {}
        
        commands = {
            'hostname': 'hostname',
            'kernel': 'uname -r',
            'os': 'cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d \'"\'',
            'architecture': 'uname -m',
            'uptime': 'uptime',
            'whoami': 'whoami',
            'id': 'id',
            'pwd': 'pwd'
        }
        
        for key, cmd in commands.items():
            result = self.execute_command(cmd)
            if result['return_code'] == 0:
                info[key] = result['stdout'].strip()
            else:
                info[key] = 'Unknown'
        
        return info
    
    def test_connectivity(self) -> bool:
        """Test if the connection is still active"""
        try:
            result = self.execute_command('echo "connectivity_test"', timeout=10)
            return result['return_code'] == 0 and 'connectivity_test' in result['stdout']
        except:
            return False
    
    def disconnect(self):
        """Close the SSH connection"""
        if self.client:
            try:
                self.client.close()
                self.connected = False
                self.logger.info(f"Disconnected from {self.hostname}")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connect():
            raise RuntimeError("Failed to establish SSH connection")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        if self.connected:
            self.disconnect()