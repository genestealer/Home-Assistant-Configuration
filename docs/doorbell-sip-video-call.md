# Front Door Doorbell → Axis Camera SIP Video Call

Set up 2026-10-30. No passwords are stored in this file.

## Overview
Pressing the doorbell rings the mechanical chime and makes the Axis front door camera place a SIP video call to the Linphone app on our phones. Home Assistant doesn't sit in the call path. It only adds a test button, status sensors and the existing push notification.

**Call path**
1. Doorbell button → ESP8266 doorbell controller (ESPHome)
2. ESP pin D6 pulls camera input Port 1 to ground for 1 second
3. Axis event rule: Port 1 active → Make call
4. Camera SIP account (sip.linphone.org) calls the household phone SIP account
5. Linphone rings on every phone signed in to that account and shows a video preview before answering. The first phone to answer takes the call and the others stop ringing

## Hardware
- **Doorbell controller:** NodeMCU v2 (ESP8266), ESPHome device `doorbell-controller`, IP 192.168.2.36, config [esphome/doorbell-controller.yaml](../esphome/doorbell-controller.yaml)
- **Camera:** Axis P3265-LV dome, IP 192.168.4.33, 4-pin I/O terminal block
- **Camera audio:** built-in microphone, plus an external powered speaker on the camera's audio output
- **Cable:** grey multicore between the ESP and the camera terminal block

### Camera I/O terminal block
| Pin | Function | Notes |
|---|---|---|
| 1 | DC ground | Shared with ESP GND |
| 2 | 12 V DC out (max 25 mA) | Not connected. Would damage the ESP |
| 3 | Digital input (Port 1) | Active when connected to pin 1 |
| 4 | Digital output (Port 2) | Open drain, connects to pin 1 when active |

The ports have fixed directions: Port 1 is always an input, Port 2 always an output.

### Wiring (grey multicore)
| Wire | ESP pin | Camera pin | Direction |
|---|---|---|---|
| Green | D6 (GPIO12) | 3, input Port 1 | ESP → camera |
| White | D5 (GPIO14) | 4, output Port 2 | Camera → ESP |
| 3× Black | GND | 1, DC ground | Common ground |
| Red | n/a | n/a | Spare |

No optocoupler: the ESP and camera connect directly. The shared ground is required for both signals.

Lesson learned: D5 and D6 were first set the wrong way round in the ESP config. Swapping the pins in the config fixed it, with no rewiring needed.

## ESPHome (doorbell-controller.yaml)
- `cctvSipCallTrigger`: D6, open-drain output, inverted. The doorbell press turns it on for 1 s, pulling camera Port 1 low. Internal only, not shown in HA
- **Front Door CCTV Output** (binary sensor): D5, input with pull-up, inverted. Reads camera Port 2. Spare channel for future camera → ESP or HA signalling
- **Trigger CCTV Call** (button): pulses D6 without ringing the chime. Use it to test the call
- **Front Door** (`event.doorbell_front_door`, device class `doorbell`, event type `ring`): fires on each press. Exposed to Google Assistant so Nest speakers and displays announce the doorbell and Google Home sends a phone notification
  - Exposure is managed by the **Assistant UI for Google Assistant (Manual Setup)** custom integration (`hass-ga-manual-ui`): entity → Settings → Voice assistants → Expose → **Google Assistant (Manual)** on. The `event` line in `google_assistant` → `exposed_domains` alone was not enough
  - In the Google Home app: the doorbell must be in a home/room, with its notifications turned on
- The doorbell press also turns on the chime relay (D1) and plays the button LED effect
- The YAML header documents the wiring, the call path and the video limits

## Home Assistant entities
| Entity | Purpose |
|---|---|
| `button.doorbell_trigger_cctv_call` | Test the SIP call without ringing the bell |
| `binary_sensor.doorbell_front_door_cctv_output` | ESP reading of camera Port 2 |
| `binary_sensor.front_door_33_port_1` | Axis integration view of camera Port 1 (input) |
| `switch.front_door_33_port_2` | Axis integration control of camera Port 2 (output) |
| `camera.front_door_33` | Camera stream and snapshots |

The **Doorbell - Notify phones** automation still sends the push notification with a snapshot. It acts as the fallback if the SIP call fails.

**Optional HA path:** `rest_command.axis_front_door_virtual_input_on` / `_off` toggle Axis virtual input 1 over the camera's HTTP API (VAPIX). It's defined in [includes/rest_commands/axis_front_door.yaml](../includes/rest_commands/axis_front_door.yaml). It needs the `axis_front_door_username` / `axis_front_door_password` secrets updated (they were out of date and returned 401) and a second camera rule on Virtual input 1.

## Axis camera settings

**System → Accessories → I/O ports**

The directions are fixed by the hardware; the camera has no setting to change them.

| Setting | Port 1 (pin 3, from ESP D6) | Port 2 (pin 4, to ESP D5) |
|---|---|---|
| Name | Port 1 | Port 2 |
| Direction | Input (fixed) | Output (fixed) |
| Normal state | Open circuit (first button) | Open circuit (first button) |
| Supervised | Off (no end-of-line resistors) | n/a |
| Port toggle | n/a | Off. This is the output's manual on/off, not an enable switch |
| Idle reading | "Current state: Circuit open" | ESP reads `Front Door CCTV Output` = off |

**System → Plain config → IOPort** (same settings, for checking)
- `I0` (Port 1): Configurable unticked, Direction Input. Input → Generate when circuit is: **Closed**
- `I1` (Port 2): Output → Active: **Closed**, Button: None, Delay time: 0, Mode: Bistable, Pulse time: 0

**Testing**
- Press **Trigger CCTV Call** in HA: Port 1 shows "Circuit closed" and `binary_sensor.front_door_33_port_1` turns on for about 1 s
- Turn on `switch.front_door_33_port_2` (or the Port 2 toggle): `binary_sensor.doorbell_front_door_cctv_output` turns on within about 100 ms

**Network speaker pairing** on the same page is unused. The speaker is wired to the camera's audio output.

**System → SIP → SIP settings**
- Enable SIP: on
- Allow incoming calls: on
- **Call handling:**
  - Calling timeout: 60 s
  - Incoming call timeout: 60 s
  - End calls after: 3600 s (infinite call duration off)
- **Ports:**
  - SIP: 5060
  - TLS: 5061
  - RTP start port: 4000
- **NAT traversal:** ICE, TURN and STUN all off. Calls to linphone.org work without them
- **Audio and video:**
  - Audio codecs, in priority order: PCMU, PCMA, opus, L16/16000
  - Audio direction: Send and receive
  - H.264 packetization mode: Auto (the camera offers mode 1)
  - Video direction: Send only
- **Additional:**
  - UDP-to-TCP switching: on (the camera switches to TCP for large call requests that include video)
  - Allow via rewrite: on
  - Allow contact rewrite: on
  - Register with server every: 300 s
  - DTMF payload type: 96

**System → SIP → SIP accounts**
- Account: the camera's own linphone.org username and password
- Domain / Registrar: `sip.linphone.org`
- Transport: (fill in what's set on the account)
- Answer automatically: on (lets us call the camera to look and listen)

**System → Events → Rules**
- Name: Doorbell SIP call
- Condition: I/O → Digital input, Port 1, Active, used as trigger
- Action: Calls → Make call, SIP account = camera account, recipient = `sip:<phone-account>@sip.linphone.org`

**SIP video stream limits**
- Resolution: 704×576 maximum. Higher resolutions give no video
- H.264 profile: Baseline. Main and High give no video
- Frame rate: 15 fps
- **Cause:** the camera always offers SIP video as H.264 Baseline level 1.3 (`profile-level-id=42000d`), capped at 768 kbps. Linphone can accept up to level 3.1 (720p), so the limit is the camera's SIP implementation, not the phone
- None of the SIP pages has a setting to change this offer
- For full-resolution viewing, use the HA camera stream (RTSP) instead

## Linphone (phones)
- **Accounts:** two linphone.org accounts. The camera has its own account, and all household phones share one phone account
- **Shared account:** Linphone's server rings every phone signed in to the shared account at once, and the others stop ringing once one answers
- **Sign-in:** use **Use a linphone.org account**, which enables push notifications so phones ring while locked
- **Video:** Settings → Video, H.264 enabled
- **Preview:** video preview before answering is enabled

**Pixel 9 settings**
- Settings → Apps → Linphone → App battery usage → Allow background usage, Unrestricted
- Settings → Apps → Linphone → Notifications → all allowed
- Settings → Apps → Special app access → Full screen notifications → Linphone on

## Alternative: local Asterisk App (tested, working)
- **App:** Asterisk by TECH7Fox, v6.4.0, config at `/addon_configs/3e533915_asterisk/asterisk/`
- **Where to edit:** put changes in `custom/`. The App regenerates `default/` at every start
- **`custom/pjsip_custom.conf`:** holds the `linphone-auth` / `linphone-aor` / `linphone-endpoint` templates, which the dashboard's **Add New Device** needs, plus extension 104 (camera)
- **Phone:** the phone used extension 105 while testing; recreate it if you go back to Asterisk
- **`custom/logger.conf`:** writes `asterisk/debug.log` for troubleshooting. Remove it when no longer needed, because it grows indefinitely
- **Dialplan:** the camera called 105 via Asterisk at 192.168.10.21:5060, and the dialplan routes any extension number to that extension (`_X!`)
- **Dashboard quirks (v6.4.0):**
  - The endpoint table shows built-in demo rows (100, 101, 102, 103, 8001) and never lists real extensions. Deleting rows only hides them until the page reloads
  - **Add New Device** keeps only the first audio codec and splits on commas, so don't use commas in passwords or names
  - Use the Console tab (`pjsip show endpoints`, `pjsip show contacts`) to see the real state
- **`auto_add`:** creates one WebRTC extension per HA person, for the HA SIP card only. It's now off. The AMI password has been changed
- **Limitation:** Linphone with a self-hosted server has no push notifications, so Android can put it to sleep and calls fail with "404 Not Found / invalid URI". This is why we moved to linphone.org accounts

## Troubleshooting notes
- Use **Trigger CCTV Call** in HA to test without ringing the chime
- `binary_sensor.front_door_33_port_1` should turn on for about 1 s per press. If it doesn't, check the D6 wiring and ground
- If Port 1 fires but nothing rings: check the camera's SIP account status shows Registered / OK (200), and check the Port 1 rule is enabled
- If the phone doesn't ring while locked: check Linphone battery and push settings
- If the call connects with no video: check the SIP video stream is 704×576 or lower, Baseline profile, 15 fps
- **Asterisk:** turn on detailed SIP logging with `hassio.addon_stdin` input `pjsip set logger on`, read `asterisk/debug.log`, then turn it off with `pjsip set logger off`
- After an Asterisk App restart, devices only sign in again on their own interval (300 s)

## Security
- Use a separate long random password for each SIP account and for the Asterisk AMI password
- Never forward SIP ports (5060/5061) from the router
- The camera auto-answers incoming calls, so anyone with a SIP login that can reach it can listen at the door. Guard the account passwords
- The shared household account means anyone with its password can receive doorbell calls
