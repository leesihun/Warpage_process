# Data Auto Transfer System

Automated daily transfer of dated folders to remote systems.

## Features

- **Automated Daily Transfers**: Configurable execution time (default 6 AM)
- **Multiple Protocols**: SCP, SMB/CIFS, local copy support
- **Smart Date Handling**: Automatically finds yesterday's folder (YYYYMMDD format)
- **Robust Error Handling**: Retry mechanisms with exponential backoff
- **Comprehensive Logging**: Detailed logs with file rotation
- **Flexible Configuration**: Text-based configuration file
- **Dry Run Mode**: Test transfers without actually moving files
- **Connection Testing**: Verify connectivity before transfers

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

| Setting | Description | Default |
|---------|-------------|---------|
| `SCHEDULE_TIME` | Daily execution time (HH:MM) | 06:00 |
| `SOURCE_DIRECTORY` | Source folder path | ../data |
| `FOLDER_PATTERN` | Date folder naming pattern | %Y%m%d |
| `TARGET_IP` | Remote system IP address | - |
| `TARGET_DIRECTORY` | Remote destination path | - |
| `PROTOCOL` | Transfer protocol (scp/smb/local) | scp |
| `USERNAME` | Authentication username | - |
| `PASSWORD` | Authentication password | - |
| `SSH_KEY_PATH` | SSH private key path | - |
| `DRY_RUN` | Test mode without actual transfer | false |
| `RETRY_ATTEMPTS` | Number of retry attempts | 3 |
| `RETRY_DELAY` | Delay between retries (seconds) | 30 |
| `DELETE_AFTER_TRANSFER` | Delete source after transfer | false |

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

## Transfer Protocols

### SCP (Secure Copy)
- **Requirements**: SSH access to target system
- **Authentication**: Username/password or SSH key
- **Best for**: Linux/Unix systems

### SMB/CIFS
- **Requirements**: Network share access
- **Authentication**: Username/password
- **Best for**: Windows systems

### Local
- **Requirements**: Local filesystem access
- **Best for**: Same-machine transfers, network drives

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

### SCP Transfer to Linux Server
```
TARGET_IP=192.168.1.100
TARGET_DIRECTORY=/backup/pemtron_data
PROTOCOL=scp
USERNAME=backup_user
SSH_KEY_PATH=/path/to/private_key
```

### SMB Transfer to Windows Share
```
TARGET_IP=192.168.1.200
TARGET_DIRECTORY=shared_folder/backup
PROTOCOL=smb
USERNAME=domain\\backup_user
PASSWORD=your_password
```

## Logging

Logs are written to `data_transfer.log` with automatic rotation:
- **File Size Limit**: 10MB per file
- **Backup Files**: 5 previous logs kept
- **Console Output**: Real-time status updates
- **Log Levels**: DEBUG, INFO, WARNING, ERROR

## Troubleshooting

### Connection Issues
1. Verify target IP and credentials
2. Test network connectivity: `ping [TARGET_IP]`
3. For SCP: Ensure SSH service is running
4. For SMB: Check Windows firewall and sharing settings

### Transfer Failures
1. Check log file for detailed error messages
2. Verify sufficient disk space on target
3. Ensure proper permissions on source and target
4. Test with dry run mode first

### Scheduling Issues
1. Verify system time and timezone
2. Check if Python process has necessary permissions
3. For Windows: Consider running as Windows Service
4. For Linux: Use cron as alternative

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

## Security Considerations

- Store passwords securely or use SSH keys
- Restrict network access using firewalls
- Use dedicated service accounts with minimal permissions
- Regularly rotate credentials
- Monitor log files for suspicious activity

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