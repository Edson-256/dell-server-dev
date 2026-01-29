# Project: Dell Server Setup (Ubuntu 24.04 LTS)

## System Configuration
- **Hardware:** Dell Inspiron 14 7460 (Model P74G)
  - **CPU:** Intel(R) Core(TM) i7-7500U @ 2.70GHz (2 Cores, 4 Threads)
  - **RAM:** 16GB DDR4 (2x 8GB SODIMM @ 2133 MT/s)
  - **Storage:**
    - Primary: 480GB KINGSTON SA400S3 (SATA SSD) - Ubuntu LVM
    - Secondary: 240GB ADATA SU650NS38 (M.2 SATA SSD) - Windows NTFS
  - **GPU:** Intel HD Graphics 620 + NVIDIA GeForce 940MX
- **OS:** Ubuntu Server 24.04.3 LTS (amd64)
- **Storage Layout (Ubuntu):** LVM Group using entire disk (~447GB on sda)
- **Power Management:** 
  - Lid Switch: Ignored (`HandleLidSwitch=ignore` in `/etc/systemd/logind.conf`) to keep server running when closed.
  - Screen: Auto-off after 60s (`consoleblank=60` in GRUB) to prevent burn-in.

## Network
- **Ethernet (enp3s0):** DHCP (IP: `192.168.100.44`).
- **Wi-Fi (wlp2s0):** DHCP (IP: `192.168.100.115`).
- **Access:** Primary access via SSH from macOS using iTerm2 profiles.

## Pending Issues / Notes
- **Local Keyboard:** The physical keyboard on the Dell is not correctly mapped (ABNT2/US layout mismatch). Direct local access is difficult; SSH is strictly preferred.

## Completed Tasks
- [x] Install Docker (Installed on 2026-01-29)
- [x] Install Portainer (Installed on 2026-01-29)

## Next Steps
- Configure Portainer environments.
- Set up automated backups for the Docker volumes.
- Explore and deploy initial services (Nginx, Home Assistant, etc.).
