# Data Auto Transfer System (TCP Port 22 Version)

Automated daily transfer of dated folders to remote systems via **TCP port 22 ONLY**.

## 🔒 TCP Port 22 Compliance

**This version is specifically configured for firewall environments requiring TCP port 22 ONLY:**

- ✅ **Exclusively uses TCP port 22** for all data transfers via SSH/SCP protocol
- ✅ **Windows-to-Windows optimized** with PuTTY and OpenSSH support
- ✅ **Firewall compliant** - no other ports or protocols used
- ✅ **Explicit port enforcement** with `-P 22` flags in all SCP commands
- ✅ **Connection testing** validates TCP port 22 connectivity before transfers

## Features

- **Automated Daily Transfers**: Configurable execution time (default 6 AM) via TCP port 22
- **TCP Port 22 Protocol**: SCP/SSH protocol optimized for Windows environments
- **Smart Date Handling**: Automatically finds yesterday's folder (YYYYMMDD format)
- **Windows Authentication**: PuTTY (pscp/plink) and Windows OpenSSH support
- **Robust Error Handling**: Retry mechanisms with exponential backoff
- **Comprehensive Logging**: Detailed logs showing TCP port 22 usage
- **Flexible Configuration**: Text-based configuration with explicit port settings
- **Dry Run Mode**: Test transfers without actually moving files
- **Connection Testing**: Verify TCP port 22 connectivity before transfers

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**:
   Edit `config.txt` with your target system details:
   ```
   TARGET_IP=192.168.1.100
   TARGET_DIRECTORY=/remote/backup/data
   USERNAME=your_username
   SCHEDULE_TIME=06:00
   ```

3. **Test Connection**:
   ```bash
   python main.py --test
   ```

4. **Run Once** (for testing):
   ```bash
   python main.py --once
   ```

5. **Start Scheduler**:
   ```bash
   python main.py
   ```

## Configuration Options

| Setting | Description | Default | TCP Port 22 |
|---------|-------------|---------|--------------|
| `SCHEDULE_TIME` | Daily execution time (HH:MM) | 06:00 | ✅ |
| `SOURCE_DIRECTORY` | Source folder path | ../data | ✅ |
| `FOLDER_PATTERN` | Date folder naming pattern | %Y%m%d | ✅ |
| `TARGET_IP` | Remote system IP address | - | ✅ |
| `TARGET_DIRECTORY` | Remote destination path | - | ✅ |
| `PROTOCOL` | Transfer protocol (**scp only**) | scp | ✅ **Required** |
| `PORT` | **TCP port (must be 22)** | 22 | ✅ **Required** |
| `USERNAME` | Authentication username | - | ✅ |
| `PASSWORD` | Authentication password | - | ✅ |
| `SSH_KEY_PATH` | SSH private key path | - | ✅ |
| `DRY_RUN` | Test mode without actual transfer | false | ✅ |
| `RETRY_ATTEMPTS` | Number of retry attempts | 3 | ✅ |
| `RETRY_DELAY` | Delay between retries (seconds) | 30 | ✅ |
| `DELETE_AFTER_TRANSFER` | Delete source after transfer | false | ✅ |

## Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -c, --config FILE    Configuration file path (default: config.txt)
  --once              Run transfer once immediately
  --test              Test connection to target system  
  --dry-run           Enable dry run mode
  -h, --help          Show help message
```

## Transfer Protocol (TCP Port 22 Only)

### SCP (Secure Copy) - **ONLY SUPPORTED PROTOCOL**
- **Port**: TCP port 22 ONLY
- **Requirements**: SSH server running on target system
- **Authentication**: Username/password or SSH key
- **Windows Support**:
  - PuTTY (pscp/plink) - Recommended for Windows-to-Windows
  - Windows OpenSSH - Built-in Windows 10/11 support
- **Firewall Compliance**: Uses only TCP port 22, no other ports needed

> **Note**: SMB/CIFS and Local protocols have been removed to ensure exclusive TCP port 22 usage.

## Examples

### Basic Usage
```bash
# Test configuration
python main.py --test

# Run once with dry run
python main.py --once --dry-run

# Start daily scheduler
python main.py
```

### SCP Transfer with SSH Key (TCP Port 22)
```
TARGET_IP=10.213.43.11
TARGET_DIRECTORY=gumi_s-aoi
PROTOCOL=scp
PORT=22
USERNAME=s.hun.lee
SSH_KEY_PATH=/path/to/private_key
```

### SCP Transfer with Password (TCP Port 22)
```
TARGET_IP=10.213.43.11
TARGET_DIRECTORY=gumi_s-aoi
PROTOCOL=scp
PORT=22
USERNAME=s.hun.lee
PASSWORD=your_password
PASSWORD_FALLBACKS=backup_password1,backup_password2
```

### Windows PuTTY Optimized Configuration
```
# Requires PuTTY installed (pscp/plink commands available)
TARGET_IP=10.213.43.11
TARGET_DIRECTORY=gumi_s-aoi
PROTOCOL=scp
PORT=22
USERNAME=s.hun.lee
PASSWORD=atleast12!
PASSWORD_FALLBACKS=qwerty12!
```

## Logging

Logs are written to `data_transfer.log` with automatic rotation:
- **File Size Limit**: 10MB per file
- **Backup Files**: 5 previous logs kept
- **Console Output**: Real-time status updates
- **Log Levels**: DEBUG, INFO, WARNING, ERROR

## Troubleshooting

### TCP Port 22 Connection Issues
1. **Verify TCP port 22 is open**: `telnet [TARGET_IP] 22`
2. **Test SSH connectivity**: `ssh -p 22 username@[TARGET_IP]`
3. **Check firewall settings**: Ensure TCP port 22 is allowed
4. **Verify SSH service**: Ensure SSH server is running on target
5. **Windows specific**: Install PuTTY or Windows OpenSSH client

### Authentication Issues
1. **Password authentication**: Verify credentials with `ssh -p 22 username@[TARGET_IP]`
2. **Key authentication**: Test SSH key with `ssh -p 22 -i keyfile username@[TARGET_IP]`
3. **Windows OpenSSH**: Ensure OpenSSH client is installed and in PATH
4. **PuTTY**: Verify pscp/plink commands work: `pscp -P 22 -pw password testfile username@[TARGET_IP]:`

### Transfer Failures
1. Check log file for "TCP port 22" messages and error details
2. Verify sufficient disk space on target system
3. Ensure proper permissions on source and target directories
4. Test with dry run mode first: `python main.py --once --dry-run`
5. Verify SCP command syntax in logs

### Windows Environment Issues
1. **Path issues**: Ensure Python and SSH tools are in system PATH
2. **Permissions**: Run as administrator if needed
3. **Antivirus**: Configure antivirus to allow SSH connections
4. **Service mode**: Use NSSM to run as Windows service

## Windows Service Installation

To run as a Windows service, use `nssm` (Non-Sucking Service Manager):

```bash
# Install nssm
# Download from: https://nssm.cc/

# Create service
nssm install DataAutoTransfer "python.exe" "C:\path\to\main.py"
nssm set DataAutoTransfer AppDirectory "C:\path\to\data_autotransfer"
nssm start DataAutoTransfer
```

## Security Considerations (TCP Port 22 Focused)

- **Network Security**: Only TCP port 22 is used, reducing attack surface
- **SSH Key Authentication**: Preferred over passwords for better security
- **Firewall Configuration**: Allow only TCP port 22 (SSH) in firewall rules
- **Dedicated Accounts**: Use service accounts with minimal SSH permissions
- **Password Security**: Store passwords securely, use strong passwords
- **Connection Monitoring**: Monitor SSH logs on target systems
- **Regular Updates**: Keep SSH server and client software updated
- **Windows Security**: Configure Windows Defender to allow SSH connections

## File Structure

```
data_autotransfer/
├── main.py              # Main application entry point
├── config.txt           # Configuration file
├── config_parser.py     # Configuration parser
├── date_utils.py        # Date calculation utilities
├── transfer_manager.py  # Transfer protocol handlers
├── logger.py           # Logging configuration
├── scheduler.py        # Scheduling system
├── requirements.txt    # Python dependencies
└── README.md          # This documentation
```