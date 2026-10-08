# Automatic Generate Adblock Hosts

An automated repository that compiles and generates a high-performance hosts blocklist to defeat ads, trackers, and telemetry. 

## Direct URL

Copy this URL to use directly in your adblocker:

```text
https://raw.githubusercontent.com/soctrungkien/hosts/refs/heads/main/hosts
```

## Features

* **Auto-Update:** Automatically rebuilt every day at 00:00 UTC.
* **Massive Coverage:** Blocks over 725k+ ad and tracking domains.
* **Format Compatibility:** Standard hosts format, perfectly compatible with AdAway, BindHost, DNSMasq, or custom system hosts.
* **Optimized:** Deduplicated and sorted for maximum resolution speed.

## Usage

### AdAway (Android)
1. Open AdAway.
2. Go to **Hosts sources**.
3. Add a new source and paste the Direct URL.
4. Sync and apply.

### BindHost (Magisk / KernelSU)
Add the URL to your custom configuration list and update via webui.

### Manual / System Level
Append the contents of the hosts file to your system hosts path:
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **Linux**: `/etc/hosts`
