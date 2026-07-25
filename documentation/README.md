# OmenCtl Documentation

Welcome to the internal documentation for **OmenCtl**. This directory contains comprehensive details about the software architecture, hardware manipulation via EC (Embedded Controller) and WMI (Windows Management Instrumentation) in Linux, and guidelines for development.

## Table of Contents

1. [Architecture & Execution Flow](ARCHITECTURE.md)
   Learn how a command flows from the User Interface (GTK4), through the D-Bus IPC, into the Python Daemon, and finally down to the hardware WMI/EC level.

2. [Hardware Offsets & Registers](HARDWARE_OFFSETS.md)
   A deep dive into the Embedded Controller (EC) registers, memory offsets, and ACPI paths used to control Fan Speeds, RGB Lighting, and Power Profiles.
