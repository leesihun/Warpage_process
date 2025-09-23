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

                    if protocol == "scp":
                        success, message = self._transfer_scp(source_path, target_ip, target_path, username, pwd, ssh_key_path)
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
    
    def _transfer_scp(self, source_path: str, target_ip: str, target_path: str,
                     username: str, password: str, ssh_key_path: str) -> Tuple[bool, str]:
        """Transfer using SCP protocol over TCP port 22."""
        try:
            # Build SCP command
            folder_name = os.path.basename(source_path)
            target_full = f"{username}@{target_ip}:{target_path}/"

            cmd = ["scp", "-r", "-P", "22"]  # Explicitly use TCP port 22

            # Add SSH key if provided
            if ssh_key_path and os.path.exists(ssh_key_path):
                cmd.extend(["-i", ssh_key_path])

            # Add essential options for automated transfer
            cmd.extend([
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null" if os.name != 'nt' else "NUL",
                "-o", "ServerAliveInterval=60",
                "-o", "ServerAliveCountMax=3"
            ])

            cmd.extend([source_path, target_full])

            self.logger.info(f"Executing SCP transfer over TCP port 22: {' '.join(cmd[:-2])} [source] [target]")

            # Execute SCP command - Windows specific handling
            if os.name == 'nt':
                # Windows: Try different authentication methods
                if password and not ssh_key_path:
                    # First try with plink (PuTTY) if available
                    if self._check_plink_available():
                        return self._transfer_plink(source_path, target_ip, target_path, username, password)
                    else:
                        # Use PowerShell's scp if available, or fall back to native scp with password prompt
                        return self._transfer_windows_scp(source_path, target_ip, target_path, username, password)
                else:
                    # Key-based authentication or no password
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            else:
                # Unix/Linux: use sshpass for password authentication
                if password and not ssh_key_path:
                    cmd = ["sshpass", "-p", password] + cmd
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            if result.returncode == 0:
                self.logger.info(f"SCP transfer successful over TCP port 22: {source_path} -> {target_full}")
                return True, "SCP transfer completed successfully over TCP port 22"
            else:
                error_msg = f"SCP failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "SCP transfer timed out"
        except FileNotFoundError:
            return False, "SCP command not found. Please install OpenSSH client or PuTTY."
        except Exception as e:
            return False, f"SCP transfer error: {str(e)}"

    def _check_plink_available(self) -> bool:
        """Check if PuTTY's plink command is available."""
        try:
            result = subprocess.run(["plink", "-V"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _transfer_plink(self, source_path: str, target_ip: str, target_path: str,
                       username: str, password: str) -> Tuple[bool, str]:
        """Transfer using PuTTY's pscp over TCP port 22."""
        try:
            # Use pscp (PuTTY SCP) for Windows - PuTTY doesn't use -o options
            folder_name = os.path.basename(source_path)
            target_full = f"{username}@{target_ip}:{target_path}/"

            cmd = [
                "pscp", "-r", "-P", "22",
                "-pw", password,
                "-batch",  # Non-interactive mode for automation
                source_path, target_full
            ]

            self.logger.info(f"Executing PSCP transfer over TCP port 22: pscp -r -P 22 -batch [auth] [source] [target]")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            if result.returncode == 0:
                self.logger.info(f"PSCP transfer successful over TCP port 22: {source_path} -> {target_full}")
                return True, "PSCP transfer completed successfully over TCP port 22"
            else:
                error_msg = f"PSCP failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            return False, f"PSCP transfer error: {str(e)}"

    def _transfer_windows_scp(self, source_path: str, target_ip: str, target_path: str,
                             username: str, password: str) -> Tuple[bool, str]:
        """Transfer using Windows native OpenSSH SCP with password input over TCP port 22."""
        try:
            folder_name = os.path.basename(source_path)
            target_full = f"{username}@{target_ip}:{target_path}/"

            # Use Windows OpenSSH SCP - simplified options for reliability
            cmd = [
                "scp", "-r", "-P", "22",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=NUL",  # Windows equivalent of /dev/null
                "-o", "PasswordAuthentication=yes",
                "-o", "PubkeyAuthentication=no",  # Force password auth only
                source_path, target_full
            ]

            self.logger.info(f"Executing Windows OpenSSH SCP transfer over TCP port 22: scp -r -P 22 [options] [source] [target]")

            # Execute with password input via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(input=f"{password}\n", timeout=3600)
                returncode = process.returncode

                if returncode == 0:
                    self.logger.info(f"Windows OpenSSH SCP transfer successful over TCP port 22: {source_path} -> {target_full}")
                    return True, "Windows OpenSSH SCP transfer completed successfully over TCP port 22"
                else:
                    error_msg = f"Windows OpenSSH SCP failed (code {returncode}): {stderr.strip()}"
                    self.logger.error(error_msg)
                    return False, error_msg

            except subprocess.TimeoutExpired:
                process.kill()
                return False, "Windows OpenSSH SCP transfer timed out"

        except Exception as e:
            return False, f"Windows OpenSSH SCP transfer error: {str(e)}"
    
    def _transfer_smb(self, source_path: str, target_ip: str, target_path: str, 
                     username: str, password: str) -> Tuple[bool, str]:
        """Transfer using SMB/CIFS protocol."""
        try:
            # For Windows, use robocopy or xcopy
            if os.name == 'nt':
                # Mount network drive temporarily
                drive_letter = "Z:"
                share_path = f"\\\\{target_ip}\\{target_path.replace('/', '\\')}"
                
                # Try to connect to network share
                net_use_cmd = f'net use {drive_letter} {share_path}'
                if username and password:
                    net_use_cmd += f' /user:{username} {password}'
                
                result = subprocess.run(net_use_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
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
    
    def test_connection(self, target_ip: str, protocol: str, username: str = "",
                       password: str = "", ssh_key_path: str = "") -> Tuple[bool, str]:
        """
        Test connection to target system over TCP port 22.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if protocol.lower() == "scp":
                # Test SSH connection over TCP port 22
                if password and not ssh_key_path:
                    # Handle password authentication
                    if os.name == 'nt':
                        # Windows: Try with plink first if available
                        if self._check_plink_available():
                            plink_cmd = ["plink", "-P", "22", "-pw", password, "-batch", f"{username}@{target_ip}", "echo 'Connection test successful over TCP port 22'"]
                            result = subprocess.run(plink_cmd, capture_output=True, text=True, timeout=15)
                        else:
                            # Use Windows OpenSSH with password input
                            cmd = [
                                "ssh", "-p", "22", "-o", "ConnectTimeout=10",
                                "-o", "StrictHostKeyChecking=no",
                                "-o", "UserKnownHostsFile=NUL",
                                "-o", "PasswordAuthentication=yes",
                                "-o", "PubkeyAuthentication=no",
                                f"{username}@{target_ip}",
                                "echo 'Connection test successful over TCP port 22'"
                            ]
                            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                            try:
                                stdout, stderr = process.communicate(input=f"{password}\n", timeout=15)
                                result = type('obj', (), {'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr})()
                            except subprocess.TimeoutExpired:
                                process.kill()
                                return False, "SSH connection test timed out over TCP port 22"
                    else:
                        # Unix/Linux: use sshpass
                        cmd = [
                            "sshpass", "-p", password,
                            "ssh", "-p", "22", "-o", "ConnectTimeout=10",
                            "-o", "StrictHostKeyChecking=no",
                            "-o", "UserKnownHostsFile=/dev/null",
                            f"{username}@{target_ip}",
                            "echo 'Connection test successful over TCP port 22'"
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                else:
                    # Key-based authentication
                    cmd = ["ssh", "-p", "22", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes"]
                    if ssh_key_path and os.path.exists(ssh_key_path):
                        cmd.extend(["-i", ssh_key_path])
                    cmd.extend([
                        "-o", "StrictHostKeyChecking=no",
                        "-o", "UserKnownHostsFile=/dev/null" if os.name != 'nt' else "NUL",
                        f"{username}@{target_ip}",
                        "echo 'Connection test successful over TCP port 22'"
                    ])
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

                if result.returncode == 0:
                    return True, "SSH connection successful over TCP port 22"
                else:
                    return False, f"SSH connection failed over TCP port 22: {result.stderr.strip()}"
            
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