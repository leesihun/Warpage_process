"""
Transfer manager for data auto transfer system.
Handles file/folder transfers using multiple protocols (SCP, SMB, local copy).
"""

import os
import shutil
import subprocess
import time
from typing import Optional, Tuple, List
import logging


class TransferManager:
    """Manages file transfers using different protocols."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def transfer_folder(self, source_path: str, target_ip: str, target_path: str,
                       protocol: str, username: str = "", password: str = "",
                       ssh_key_path: str = "", dry_run: bool = False,
                       password_fallbacks: List[str] = None) -> Tuple[bool, str]:
        """
        Transfer folder to remote location.

        Args:
            source_path: Local source folder path
            target_ip: Target IP address
            target_path: Target directory path
            protocol: Transfer protocol (scp, smb, local)
            username: Username for authentication
            password: Password for authentication
            ssh_key_path: Path to SSH private key
            dry_run: If True, only simulate the transfer
            password_fallbacks: List of fallback passwords to try if primary fails

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not os.path.exists(source_path):
            return False, f"Source path does not exist: {source_path}"
        
        if not os.path.isdir(source_path):
            return False, f"Source path is not a directory: {source_path}"
        
        protocol = protocol.lower()
        
        if dry_run:
            self.logger.info(f"DRY RUN: Would transfer {source_path} to {target_ip}:{target_path} using {protocol}")
            return True, "Dry run completed successfully"

        # Prepare all passwords to try
        all_passwords = [password] if password else []
        if password_fallbacks:
            all_passwords.extend(password_fallbacks)

        # If no passwords, try once with empty password
        if not all_passwords:
            all_passwords = [""]

        try:
            # Try each password until one succeeds
            last_error = ""
            for i, pwd in enumerate(all_passwords):
                try:
                    if i > 0:
                        self.logger.info(f"Trying password fallback {i}/{len(all_passwords)-1}")

                    if protocol == "scp" or protocol == "ssh":
                        success, message = self._transfer_ssh_paramiko(source_path, target_ip, target_path, username, pwd, ssh_key_path)
                    elif protocol == "smb":
                        success, message = self._transfer_smb(source_path, target_ip, target_path, username, pwd)
                    elif protocol == "local":
                        return self._transfer_local(source_path, target_path)
                    else:
                        return False, f"Unsupported protocol: {protocol}"

                    if success:
                        if i > 0:
                            self.logger.info(f"Transfer succeeded with password fallback {i}")
                        return True, message
                    else:
                        last_error = message
                        if i < len(all_passwords) - 1:
                            self.logger.warning(f"Password {i+1} failed, trying next: {message}")

                except Exception as e:
                    last_error = f"Transfer attempt {i+1} failed: {str(e)}"
                    self.logger.error(last_error)

            # All passwords failed
            error_msg = f"All password attempts failed. Last error: {last_error}"
            self.logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Transfer failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _transfer_ssh_paramiko(self, source_path: str, target_ip: str, target_path: str,
                              username: str, password: str, ssh_key_path: str) -> Tuple[bool, str]:
        """Transfer using paramiko SSH/SFTP - no system SSH required."""
        try:
            import paramiko
            import stat

            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using key or password
            try:
                if ssh_key_path and os.path.exists(ssh_key_path):
                    self.logger.info(f"Connecting to {target_ip} using SSH key: {ssh_key_path}")
                    ssh.connect(target_ip, username=username, key_filename=ssh_key_path, timeout=30)
                else:
                    self.logger.info(f"Connecting to {target_ip} using password authentication")
                    ssh.connect(target_ip, username=username, password=password, timeout=30)

            except paramiko.AuthenticationException:
                return False, "SSH authentication failed - check username/password/key"
            except paramiko.SSHException as e:
                return False, f"SSH connection error: {str(e)}"
            except Exception as e:
                return False, f"SSH connection failed: {str(e)}"

            # Create SFTP client
            sftp = ssh.open_sftp()

            try:
                # Get source folder name
                folder_name = os.path.basename(source_path)
                remote_target = f"{target_path.rstrip('/')}/{folder_name}"

                self.logger.info(f"Starting SFTP transfer: {source_path} -> {remote_target}")

                # Recursively upload directory
                self._sftp_upload_recursive(sftp, source_path, remote_target)

                self.logger.info(f"SSH transfer successful: {source_path} -> {username}@{target_ip}:{remote_target}")
                return True, "SSH transfer completed successfully"

            finally:
                sftp.close()
                ssh.close()

        except ImportError:
            return False, "paramiko library not available - please install: pip install paramiko"
        except Exception as e:
            return False, f"SSH transfer error: {str(e)}"

    def _sftp_upload_recursive(self, sftp, local_path: str, remote_path: str):
        """Recursively upload directory via SFTP."""
        import stat

        # Create remote directory
        try:
            sftp.mkdir(remote_path)
            self.logger.debug(f"Created remote directory: {remote_path}")
        except OSError:
            # Directory might already exist
            pass

        # Upload all contents
        for item in os.listdir(local_path):
            local_item = os.path.join(local_path, item)
            remote_item = f"{remote_path}/{item}"

            if os.path.isfile(local_item):
                # Upload file
                self.logger.debug(f"Uploading file: {local_item} -> {remote_item}")
                sftp.put(local_item, remote_item)
            elif os.path.isdir(local_item):
                # Recursively upload subdirectory
                self._sftp_upload_recursive(sftp, local_item, remote_item)
    
    def _transfer_smb(self, source_path: str, target_ip: str, target_path: str,
                     username: str, password: str) -> Tuple[bool, str]:
        """Transfer using SMB/CIFS protocol with proper connection cleanup."""
        try:
            # For Windows, use robocopy or xcopy
            if os.name == 'nt':
                # Clean up any existing connections to this server first
                cleanup_success, cleanup_msg = self._cleanup_smb_connections(target_ip)
                if not cleanup_success:
                    self.logger.warning(f"Connection cleanup warning: {cleanup_msg}")

                # Mount network drive temporarily
                drive_letter = "Z:"
                share_path = f"\\\\{target_ip}\\{target_path.replace('/', '\\')}"

                # Try to connect to network share
                net_use_cmd = f'net use {drive_letter} {share_path}'
                if username and password:
                    net_use_cmd += f' /user:{username} {password}'

                result = subprocess.run(net_use_cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    # Check if it's the multiple connection error
                    stderr = result.stderr.lower()
                    if ("multiple connections" in stderr or
                        "다중 연결" in stderr or
                        "둘 이상의 사용자" in stderr):
                        # Try cleanup and retry once
                        self.logger.warning("Multiple connection error detected, retrying after cleanup...")
                        self._cleanup_smb_connections(target_ip)
                        time.sleep(2)  # Wait briefly
                        result = subprocess.run(net_use_cmd, shell=True, capture_output=True, text=True)

                        if result.returncode != 0:
                            return False, f"Failed to connect after cleanup. Error: {result.stderr}"
                    else:
                        return False, f"Failed to connect to network share: {result.stderr}"

                try:
                    # Copy using robocopy
                    folder_name = os.path.basename(source_path)
                    target_full = os.path.join(drive_letter, folder_name)

                    robocopy_cmd = f'robocopy "{source_path}" "{target_full}" /E /R:3 /W:10'
                    result = subprocess.run(robocopy_cmd, shell=True, capture_output=True, text=True)

                    # Robocopy return codes: 0-7 are success, 8+ are errors
                    if result.returncode < 8:
                        self.logger.info(f"SMB transfer successful: {source_path} -> {target_full}")
                        return True, "SMB transfer completed successfully"
                    else:
                        return False, f"Robocopy failed: {result.stderr}"

                finally:
                    # Disconnect network drive
                    subprocess.run(f'net use {drive_letter} /delete', shell=True, capture_output=True)
            
            else:
                # For Linux, use smbclient
                cmd = [
                    "smbclient", f"//{target_ip}/{target_path}", 
                    "-U", username if username else "guest",
                    "-c", f"recurse ON; prompt OFF; mput {source_path}"
                ]
                
                if password:
                    cmd.extend(["-W", password])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
                
                if result.returncode == 0:
                    return True, "SMB transfer completed successfully"
                else:
                    return False, f"SMB transfer failed: {result.stderr}"
                    
        except Exception as e:
            return False, f"SMB transfer error: {str(e)}"
    
    def _transfer_local(self, source_path: str, target_path: str) -> Tuple[bool, str]:
        """Transfer to local directory."""
        try:
            folder_name = os.path.basename(source_path)
            target_full = os.path.join(target_path, folder_name)
            
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Copy folder
            if os.path.exists(target_full):
                shutil.rmtree(target_full)
            
            shutil.copytree(source_path, target_full)
            
            self.logger.info(f"Local transfer successful: {source_path} -> {target_full}")
            return True, "Local transfer completed successfully"
            
        except Exception as e:
            return False, f"Local transfer error: {str(e)}"

    def _cleanup_smb_connections(self, target_ip: str) -> Tuple[bool, str]:
        """Clean up existing SMB connections to target server."""
        try:
            if os.name == 'nt':
                # First, list existing connections to the target IP
                result = subprocess.run('net use', shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    connections_to_remove = []
                    lines = result.stdout.split('\n')

                    for line in lines:
                        if target_ip in line:
                            # Extract drive letter or UNC path
                            parts = line.split()
                            if len(parts) >= 2:
                                connections_to_remove.append(parts[1])  # Usually the drive letter/path

                    # Remove each connection
                    success = True
                    messages = []

                    for conn in connections_to_remove:
                        self.logger.info(f"Cleaning up SMB connection: {conn}")
                        cleanup_result = subprocess.run(f'net use "{conn}" /delete /y',
                                                      shell=True, capture_output=True, text=True)
                        if cleanup_result.returncode != 0:
                            success = False
                            messages.append(f"Failed to cleanup {conn}: {cleanup_result.stderr}")
                        else:
                            messages.append(f"Cleaned up connection: {conn}")

                    if connections_to_remove:
                        message = "; ".join(messages)
                        return success, message
                    else:
                        return True, f"No existing connections found to {target_ip}"

                return True, "Connection cleanup completed"
            else:
                # For non-Windows systems, no cleanup needed
                return True, "Connection cleanup not needed on this platform"

        except Exception as e:
            return False, f"Connection cleanup error: {str(e)}"

    def test_connection(self, target_ip: str, protocol: str, username: str = "", 
                       password: str = "", ssh_key_path: str = "") -> Tuple[bool, str]:
        """
        Test connection to target system.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if protocol.lower() in ["scp", "ssh"]:
                # Test SSH connection using paramiko
                try:
                    import paramiko

                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    if ssh_key_path and os.path.exists(ssh_key_path):
                        ssh.connect(target_ip, username=username, key_filename=ssh_key_path, timeout=10)
                    else:
                        ssh.connect(target_ip, username=username, password=password, timeout=10)

                    # Test with a simple command
                    stdin, stdout, stderr = ssh.exec_command("echo 'SSH connection test successful'")
                    output = stdout.read().decode().strip()
                    ssh.close()

                    if "successful" in output:
                        return True, "SSH connection successful"
                    else:
                        return False, "SSH connection test failed"

                except paramiko.AuthenticationException:
                    return False, "SSH authentication failed"
                except paramiko.SSHException as e:
                    return False, f"SSH connection error: {str(e)}"
                except ImportError:
                    return False, "paramiko library not available"
                except Exception as e:
                    return False, f"SSH connection failed: {str(e)}"
            
            elif protocol.lower() == "smb":
                # Test SMB connection with ping
                result = subprocess.run(["ping", "-n", "1", "-w", "5000", target_ip], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "SMB target reachable"
                else:
                    return False, "SMB target unreachable"
            
            elif protocol.lower() == "local":
                return True, "Local transfer - no connection test needed"
            
            else:
                return False, f"Unknown protocol: {protocol}"
                
        except Exception as e:
            return False, f"Connection test error: {str(e)}"


if __name__ == "__main__":
    # Test transfer manager
    logging.basicConfig(level=logging.INFO)
    
    manager = TransferManager()
    
    # Test connection
    success, message = manager.test_connection("192.168.1.100", "scp", "test_user")
    print(f"Connection test: {success} - {message}")
    
    # Test dry run transfer
    success, message = manager.transfer_folder(
        "../data/20250716", "192.168.1.100", "/remote/backup", 
        "scp", "test_user", dry_run=True
    )
    print(f"Dry run: {success} - {message}")