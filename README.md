# Automatic Generate Adblock Hosts

[![GitHub stars](https://img.shields.io/github/stars/soctrungkien/hosts.svg?style=flat)](https://github.com/soctrungkien/hosts/stargazers)
[![GitHub views](https://komarev.com/ghpvc/?username=soctrungkien&repo=hosts&label=Repo%20views&color=0e75b6&style=flat)](https://github.com/soctrungkien/hosts)
[![Daily Update](https://img.shields.io/badge/Update-Daily%20at%2000%3A00%20UTC-green)](https://github.com/soctrungkien/hosts)

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