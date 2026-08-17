# Secure Risk Monitoring System

This project satisfies the MIT304 Assessment 3 brief by implementing a simple web-based cyber security system with:

- User authentication (register/login)
- Asset and risk management
- Threat-vulnerability-impact risk calculation
- Security control concepts such as MFA, login restrictions, firewall/geo-blocking, and activity monitoring
- Basic compliance support via an ISO 27001-style explanation
- A short report in markdown form

## Run the app

From the project folder:

```bash
c:/Users/ASUS/Desktop/MIT-coursework/Trimester2/CyberSecurity/.venv/Scripts/python.exe app.py
```

Then open http://127.0.0.1:5000/

## Test the app

```bash
c:/Users/ASUS/Desktop/MIT-coursework/Trimester2/CyberSecurity/.venv/Scripts/python.exe -m pytest -q
```

## Assessment alignment

### User Authentication (5 points)
Implemented a registration and login system with session-based authentication.

### Asset & Risk Management (15 points)
Users can add assets and record risks. The project calculates a basic risk score and ALE for each risk.

### Security Controls (15 points)
The system includes defensive control concepts in the report and dashboard, such as MFA, login restrictions, firewall/geo-blocking, and activity monitoring.

### Risk & Compliance (15 points)
The app supports risk treatment strategies and references ISO 27001 alignment in the report.

## Short report summary

The system is designed to help organisations monitor cyber risks by collecting information assets, identifying threats and vulnerabilities, evaluating impact, and selecting a response strategy. The design uses authentication, access controls, and monitoring as core defensive measures. In line with ISO 27001, the solution supports asset protection, risk treatment, and control implementation.
