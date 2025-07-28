# xStorage Home REST API Documentation

Eaton xStorage Home locally hosted REST HTTPS API Document (Unofficial)

This repository documents discovered API endpoints from an Eaton xStorage Home system, connected to your local network. The endpoints were reverse-engineered using Chrome network monitoring and verified via Postman.

> ⚠️ This project is **not affiliated with or endorsed by Eaton**. Use at your own risk.

---

## Notes

- **Firmware Version**: Running firmware version `00.01.0017-0-g72006700`.
- **HTTPS Access**: To avoid certificate errors, access the HTTPS interface via an HTTPS proxy server (e.g., NGINX).
- All endpoints require authentication using Bearer tokens.
- Bearer tokens expire after 60 minutes.
- Some endpoints are restricted to technician profiles and will return a `403 Forbidden` error for customer profiles.

---

## To-Do List

1. SSH into the controller and look for more endpoints.
2. Review the provided top-level firmware specification for the controller for more information.

---

## Summary Table

| Endpoint                          | Method | Requires Technician Account | Description                       |
|-----------------------------------|--------|-----------------------------|-----------------------------------|
| `/api/config/state`               | GET    | No                          | Retrieves the current configuration state of the system. |
| `/api/device`                     | GET    | No                          | Retrieves device information.     |
| `/api/device/status`              | GET    | No                          | Retrieves the current status of the device. |
| `/api/settings`                   | GET    | No                          | Retrieves device settings.        |
| `/api/metrics`                    | GET    | No                          | Retrieves hourly metrics data.    |
| `/api/metrics/daily`              | GET    | No                          | Retrieves daily metrics data.     |
| `/api/schedule/`                  | GET    | No                          | Retrieves schedule information.   |
| `/api/technical/status`           | GET    | Yes                         | Retrieves technical status of the device. |
| `/api/device/maintenance/diagnostics` | GET | Yes                         | Retrieves maintenance diagnostics. |
| `/api/device/command`             | POST   | No                          | Sends commands to the device.     |
| `/api/device/power`               | POST   | No                          | Controls the power state of the device (on/off). |
| `/api/auth/signin`                | POST   | No                          | Authenticates a user and retrieves a token. |

---

## API Endpoints

### General Endpoints

#### `GET /api/config/state`

- **Description**: Retrieves the current configuration state of the system.
- **Response**:

  ```json
  {
    "setupComplete": true,
    "missingSteps": [],
    "version": "00.01.0017-0-g72006700",
    "onboardState": "not_onboarded",
    "onboard": {
      "onboardedBy": {
        "name": " ",
        "email": ""
      },
      "onboardedAt": -62135596800,
      "techEmail": ""
    },
    "connected": false
  }
  ```

- **Comment**: Not much useful information.

#### `GET /api/device`

- **Description**: Retrieves device information.
- **Response**:

  ```json
  {
      "successful": true,
      "message": "Content Ready",
      "result": {
          "id": "",
          "updatedAt": 1752441080,
          "createdAt": 1752441080,
          "name": "REDACTED",
          "description": "",
          "address": "",
          "country": {
              "geonameId": "2635167",
              "name": "United Kingdom"
          },
          "city": {
              "geonameId": "2649833",
              "name": "London"
          },
          "postalCode": "",
          "latitude": 0,
          "longitude": 0,
          "firmwareVersion": "00.01.0017-0-g72006700",
          "commCardFirmwareVersion": "",
          "timezone": {
              "id": "Europe/London",
              "updatedAt": 0,
              "createdAt": 0,
              "timezone": "Europe/London",
              "countryId": "",
              "name": "Europe/London",
              "version": ""
          },
          "dns": "8.8.8.8",
          "bmsCapacity": 4.2,
          "bmsFirmwareVersion": "4004",
          "bmsBackupLevel": 0,
          "bmsSerialNumber": "REDACTED",
          "bmsModel": "RESIDENCIAL",
          "bmsAvgTemperature": 0,
          "inverterManufacturer": "EATON",
          "inverterModelName": "XSTH1P036P048V01",
          "inverterVaRating": 3600,
          "inverterNominalVpv": 3600,
          "inverterIsSinglePhase": true,
          "inverterFirmwareVersion": "00.06.0069",
          "inverterSerialNumber": "REDACTED",
          "networkInterfaces": [
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "name": "eth0",
                  "macAddress": "00:20:85:f2:00:35",
                  "ipAddress": "192.168.3.35"
              },
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "name": "wlan0",
                  "macAddress": "74:da:38:99:5a:b5",
                  "ipAddress": "192.168.3.52"
              }
          ],
          "powerMeters": [
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "position": 1,
                  "model": "None",
                  "singlePhase": true
              },
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "position": 2,
                  "model": "None",
                  "singlePhase": true
              }
          ],
          "hasPv": false,
          "hasBattery": true,
          "powerState": true,
          "connected": false,
          "deviceLastScheduleUpdate": 1752544607,
          "deviceLastUpdate": 1752441080,
          "updateStatus": "",
          "updateBlockedState": false,
          "bundleVersion": "v1.17",
          "localPortalRemoteId": "47221",
          "energySavingMode": {
              "enabled": true,
              "houseConsumptionThreshold": 300
          }
      }
  }

  ```

- **Comment**: Lots of good information.

#### `GET /api/device/status`

- **Description**: Retrieves the current status of the device.
- **Response**:

  ```json
  {
      "successful": true,
      "message": "Content Ready",
      "result": {
          "currentMode": {
              "id": "4c773998-fdc8-4faf-8132-847c27d10eb6",
              "command": "SET_CHARGE",
              "createdAt": 1752584987000,
              "updatedAt": 1752584987000,
              "duration": 1,
              "startTime": 1409,
              "endTime": 1509,
              "recurrence": "MANUAL_EVENT",
              "type": "MANUAL",
              "parameters": {
                  "action": "ACTION_CHARGE",
                  "power": 15,
                  "soc": 90
              },
              "user": {
                  "id": "00000000-0000-0000-0000-000000000000",
                  "firstName": "Local",
                  "lastName": "User"
              }
          },
          "energyFlow": {
              "acPvRole": "DISCONNECTED",
              "acPvValue": 0,
              "batteryBackupLevel": 0,
              "batteryStatus": "BAT_CHARGING",
              "batteryEnergyFlow": 406,
              "criticalLoadRole": "NONE",
              "criticalLoadValue": 0,
              "dcPvRole": "DISCONNECTED",
              "dcPvValue": 0,
              "gridRole": "NONE",
              "gridValue": 0,
              "nonCriticalLoadRole": "NONE",
              "nonCriticalLoadValue": 0,
              "operationMode": "CHARGING",
              "selfConsumption": 0,
              "selfSufficiency": 0,
              "stateOfCharge": 88,
              "energySavingModeEnabled": true,
              "energySavingModeActivated": false
          },
          "last30daysEnergyFlow": {
              "gridConsumption": 0,
              "photovoltaicProduction": 0,
              "selfConsumption": 0,
              "selfSufficiency": 0
          },
          "today": {
              "gridConsumption": 0,
              "photovoltaicProduction": 0,
              "selfConsumption": 0,
              "selfSufficiency": 0
          }
      }
  }

  ```

- **Comment**: Lots of good information.

#### `GET /api/settings`

- **Description**: Retrieves device settings.
- **Response**:

  ```json
  {
      "successful": true,
      "message": "Content Ready",
      "result": {
          "id": "990e5920-246f-4768-b31c-121b9149108a",
          "updatedAt": 1752441080,
          "createdAt": 1752441080,
          "name": "REDACTED",
          "description": "",
          "hasPv": false,
          "hasBattery": true,
          "address": "",
          "country": {
              "geonameId": "2635167",
              "name": "United Kingdom"
          },
          "city": {
              "geonameId": "2649833",
              "name": "London"
          },
          "postalCode": "",
          "latitude": 0,
          "longitude": 0,
          "defaultMode": {
              "id": "8870c322-0f3d-4d7f-a701-b664da32448c",
              "updatedAt": 1752284944,
              "createdAt": 1752284944,
              "user": null,
              "command": "SET_BASIC_MODE",
              "parameters": null
          },
          "firmwareVersion": "00.01.0017-0-g72006700",
          "bmsSerialNumber": "H-B60-H-41-031",
          "commCardFirmwareVersion": "",
          "inverterFirmwareVersion": "00.06.0069",
          "inverterSerialNumber": "REDACTED",
          "inverterPowerRating": 0,
          "bmsFirmwareVersion": "4004",
          "bmsBackupLevel": 0,
          "timezone": {
              "id": "Europe/London",
              "updatedAt": 0,
              "createdAt": 0,
              "timezone": "Europe/London",
              "countryId": "",
              "name": "Europe/London",
              "version": ""
          },
          "dns": "8.8.8.8",
          "inverterIsSinglePhase": true,
          "bmsCapacity": 4.2,
          "networkInterfaces": [
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "name": "eth0",
                  "macAddress": "00:20:85:f2:00:35",
                  "ipAddress": "192.168.3.35"
              },
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "name": "wlan0",
                  "macAddress": "74:da:38:99:5a:b5",
                  "ipAddress": "192.168.3.52"
              }
          ],
          "powerMeters": [
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "position": 1,
                  "model": "None",
                  "singlePhase": true
              },
              {
                  "id": "",
                  "updatedAt": 0,
                  "createdAt": 0,
                  "position": 2,
                  "model": "None",
                  "singlePhase": true
              }
          ],
          "updateBlockedState": false,
          "bundleVersion": "v1.17",
          "localPortalRemoteId": "47221",
          "energySavingMode": {
              "enabled": true,
              "houseConsumptionThreshold": 300
          }
      }
  }

  ```

- **Comment**: Lots of good information.

---

### Metrics Endpoints

#### `GET /api/metrics`

- **Description**: Retrieves hourly metrics data.
- **Response**:

  ```json
  {
    "metrics": [
      { "batteryStateOfCharge": 6, "time": 1752534000000 },
      { "batteryStateOfCharge": 7, "time": 1752534300000 }
    ],
    "total": { "batteryStateOfCharge": 52 }
  }
  ```

- **Comment**: Day metrics (shows data by the hour).

#### `GET /api/metrics/daily`

- **Description**: Retrieves daily metrics data.
- **Response**:

  ```json
  {
    "metrics": [
      { "batteryStateOfCharge": 64, "time": 1752447600000 }
    ],
    "total": { "batteryStateOfCharge": 64 }
  }
  ```

- **Comment**: Week metrics (shows data by the day).

---

### Command Endpoints

#### `POST /api/device/command`

  - **SET_CHARGE**: Sets the device to charge mode.

    ```json
    { "command": "SET_CHARGE", "duration": 2, "parameters": { "power": 10, "soc": 90, "action": "ACTION_CHARGE" } }
    ```

    - **Duration**: Number of hours for the command to run (integer from 1 to 12).
    - **Power**: Integer value between 5–100%.
    - **SOC**: Target State of Charge (0–100%) in 1% steps; UI only allows steps of 5%.

  - **SET_BASIC_MODE**: Sets the device to idle/default mode.

    ```json
    { "command": "SET_BASIC_MODE", "duration": 2, "parameters": null }
    ```

  - **SET_DISCHARGE**: Sets the device to discharge mode.

    ```json
    { "command": "SET_CHARGE", "duration": 2, "parameters": { "power": 5, "soc": 10, "action": "ACTION_DISCHARGE" } }
    ```

    - **Duration**: Number of hours for the command to run (integer from 1 to 12).
    - **Power**: Integer value between 5–100%.
    - **SOC**: Target State of Charge (0–100%) in 1% steps; UI only allows steps of 5%.

  - **SET_MAXIMIZE_AUTO_CONSUMPTION**: Maximizes auto consumption.

    ```json
    { "command": "SET_MAXIMIZE_AUTO_CONSUMPTION", "duration": 2, "parameters": null }
    ```

  - **SET_VARIABLE_GRID_INJECTION**: Sets variable grid injection.

    ```json
    { "command": "SET_VARIABLE_GRID_INJECTION", "duration": 2, "parameters": { "maximumPower": 0 } }
    ```

  - **SET_FREQUENCY_REGULATION**: Sets frequency regulation.

    ```json
    { "command": "SET_FREQUENCY_REGULATION", "duration": 2, "parameters": { "powerAllocation": 0, "optimalSoc": 0 } }
    ```

  - **SET_PEAK_SHAVING**: Sets peak shaving.

    ```json
    { "command": "SET_PEAK_SHAVING", "duration": 2, "parameters": { "maxHousePeakConsumption": 0 } }
    ```

---

### Power Control Endpoints

#### `POST /api/device/power`

- **Description**: Controls the power state of the device (on/off).
- **Request**:

  ```json
  {
    "parameters": {
      "state": false
    }
  }
  ```

  - **state**: Boolean value to control power state (true = on, false = off).

- **Comment**: When the device is turned off, the "powerState" field in other API responses will return false.

---

### Authentication Endpoints

#### `POST /api/auth/signin`

- **Description**: Authenticates a user and retrieves a token.
- **Request**:
  - **Technician**:

    ```json
    {
      "username": "admin",
      "pwd": "jlwgK41G",
      "inverterSn": "REDACTED",
      "email": "anything@anything.com",
      "userType": "tech"
    }
    ```

    - **Note**: When signing in with the Technician account, the email address can be anything.
  - **Customer**:

    ```json
    {
      "username": "user",
      "pwd": "REDACTED",
      "userType": "customer"
    }
    ```

- **Response**:

  ```json
  {
    "": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

---

### Technical Status Endpoint

#### `GET /api/technical/status`

- **Description**: Retrieves technical status of the device.
- **Note**: Requires technician login; customer accounts will receive a 403 Forbidden error.

- **Response**:

  ```json
  {
    "successful": true,
    "message": "Content Ready",
    "result": {
      "operationMode": "CHARGING",
      "gridVoltage": 241.40001,
      "gridFrequency": 49.96,
      "currentToGrid": 0.90000004,
      "inverterPower": 0,
      "inverterTemperature": 43.4,
      "busVoltage": 393.7,
      "gridCode": "UK_G98",
      "dcCurrentInjectionR": 0,
      "dcCurrentInjectionS": 0,
      "dcCurrentInjectionT": 0,
      "inverterModel": "XSTH1P036P048V01",
      "inverterPowerRating": 0,
      "pv1Voltage": 0,
      "pv1Current": 0,
      "pv2Voltage": 0,
      "pv2Current": 0,
      "bmsVoltage": 98.6,
      "bmsCurrent": 0.42000002,
      "bmsTemperature": 34.3,
      "bmsAvgTemperature": 0,
      "bmsMaxTemperature": 35.5,
      "bmsMinTemperature": 32.8,
      "bmsTotalCharge": 206,
      "bmsTotalDischarge": 143,
      "bmsStateOfCharge": 90,
      "bmsState": "BAT_IDLE",
      "bmsFaultCode": null,
      "bmsHighestCellVoltage": 4119,
      "bmsLowestCellVoltage": 4101,
      "tidaProtocolVersion": "",
      "invBootloaderVersion": "04.00",
      "meters": null
    }
  }
  ```

- **Comment**: Returns technical status including grid, inverter, and battery metrics.

#### `GET /api/device/maintenance/diagnostics`

- **Description**: Retrieves maintenance diagnostics.
- **Note**: Requires technician login; customer accounts will receive a 403 Forbidden error.

- **Response**:

  ```json
  {
    "successful": true,
    "message": "Content Ready",
    "result": {
      "updatedAt": 1752591465,
      "createdAt": 1752591465,
      "diskUsage": {
        "updatedAt": 1752591412,
        "createdAt": 69,
        "partition": [
          {
            "name": "/",
            "free": 336388096,
            "used": 150028288,
            "size": 486416384
          },
          {
            "name": "/mnt/DB",
            "free": 427753472,
            "used": 14790656,
            "size": 447496192
          }
        ]
      },
      "ramUsage": {
        "updatedAt": 1752591412,
        "createdAt": 69,
        "total": 120078336,
        "used": 30228480
      },
      "cpuUsage": {
        "updatedAt": 1752591412,
        "createdAt": 69,
        "used": 6.125211505924395
      }
    }
  }
  ```

- **Comment**: Returns system diagnostics including disk, RAM, and CPU usage.
