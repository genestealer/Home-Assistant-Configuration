// Clean, full implementation of the CC1101 + RADIAN logic
#include "everblu_component.h"
#include "esphome/core/log.h"
#include <cstring>
#include <algorithm>
#include <cmath>
#include <SPI.h>

namespace esphome {
namespace everblu {

static const char *const TAG = "everblu";

// --- CC1101 constants (from original project) ---
  static constexpr uint8_t WRITE_SINGLE_BYTE = 0x00;
  static constexpr uint8_t WRITE_BURST       = 0x40;
  static constexpr uint8_t READ_SINGLE_BYTE  = 0x80;
  static constexpr uint8_t READ_BURST        = 0xC0;

  // Registers
  static constexpr uint8_t IOCFG2  = 0x00;
  static constexpr uint8_t IOCFG1  = 0x01;
  static constexpr uint8_t IOCFG0  = 0x02;
  static constexpr uint8_t FIFOTHR = 0x03;
  static constexpr uint8_t SYNC1   = 0x04;
  static constexpr uint8_t SYNC0   = 0x05;
  static constexpr uint8_t PKTLEN  = 0x06;
  static constexpr uint8_t PKTCTRL1= 0x07;
  static constexpr uint8_t PKTCTRL0= 0x08;
  static constexpr uint8_t FSCTRL1 = 0x0B;
  static constexpr uint8_t FREQ2   = 0x0D;
  static constexpr uint8_t FREQ1   = 0x0E;
  static constexpr uint8_t FREQ0   = 0x0F;
  static constexpr uint8_t MDMCFG4 = 0x10;
  static constexpr uint8_t MDMCFG3 = 0x11;
  static constexpr uint8_t MDMCFG2 = 0x12;
  static constexpr uint8_t MDMCFG1 = 0x13;
  static constexpr uint8_t MDMCFG0 = 0x14;
  static constexpr uint8_t DEVIATN = 0x15;
  static constexpr uint8_t MCSM1   = 0x17;
  static constexpr uint8_t MCSM0   = 0x18;
  static constexpr uint8_t FOCCFG  = 0x19;
  static constexpr uint8_t BSCFG   = 0x1A;
  static constexpr uint8_t AGCCTRL2= 0x1B;
  static constexpr uint8_t AGCCTRL1= 0x1C;
  static constexpr uint8_t AGCCTRL0= 0x1D;
  static constexpr uint8_t WORCTRL = 0x20;
  static constexpr uint8_t FREND1  = 0x21;
  static constexpr uint8_t FSCAL3  = 0x23;
  static constexpr uint8_t FSCAL2  = 0x24;
  static constexpr uint8_t FSCAL1  = 0x25;
  static constexpr uint8_t FSCAL0  = 0x26;
  static constexpr uint8_t TEST2   = 0x2C;
  static constexpr uint8_t TEST1   = 0x2D;
  static constexpr uint8_t TEST0   = 0x2E;

  // Status registers (use with READ_SINGLE)
  static constexpr uint8_t PARTNUM_ADDR    = 0x30;
  static constexpr uint8_t VERSION_ADDR    = 0x31;
  static constexpr uint8_t FREQEST_ADDR    = 0x32;
  static constexpr uint8_t LQI_ADDR        = 0x33;
  static constexpr uint8_t RSSI_ADDR       = 0x34;
  static constexpr uint8_t MARCSTATE_ADDR  = 0x35;
  static constexpr uint8_t TXBYTES_ADDR    = 0x3A;
  static constexpr uint8_t RXBYTES_ADDR    = 0x3B;

  // PATABLE / FIFO addresses
  static constexpr uint8_t PATABLE_ADDR = 0x3E;
  static constexpr uint8_t TX_FIFO_ADDR = 0x3F;
  static constexpr uint8_t RX_FIFO_ADDR = 0x3F | 0x80; // read
  static constexpr uint8_t RXBYTES_MASK = 0x7F;

  // Command strobes
  static constexpr uint8_t SRES    = 0x30;
  static constexpr uint8_t SFSTXON = 0x31;
  static constexpr uint8_t SXOFF   = 0x32;
  static constexpr uint8_t SCAL    = 0x33;
  static constexpr uint8_t SRX     = 0x34;
  static constexpr uint8_t STX     = 0x35;
  static constexpr uint8_t SIDLE   = 0x36;
  static constexpr uint8_t SAFC    = 0x37;
  static constexpr uint8_t SWOR    = 0x38;
  static constexpr uint8_t SPWD    = 0x39;
  static constexpr uint8_t SFRX    = 0x3A;
  static constexpr uint8_t SFTX    = 0x3B;
  static constexpr uint8_t SWORRST = 0x3C;
  static constexpr uint8_t SNOP    = 0x3D;

  // Globals
  static GPIOPin *g_cs_global{nullptr};
  static GPIOPin *g_gdo0_global{nullptr};
  static uint8_t g_status_state = 0;
  static uint8_t g_status_fifo_free = 0;
  static EverbluComponent *g_self{nullptr};
  static bool g_spi_trace{false};

  // On CC1101, after CSn goes low the SO (MISO) line should go low when the crystal is stable.
  // Waiting for SO low improves reliability and avoids 0xFF reads on some boards.
  static inline void wait_so_low_() {
#if defined(ESP8266)
    const uint8_t MISO_PIN = 12; // HW SPI MISO on ESP8266
    uint32_t t0 = micros();
    while (digitalRead(MISO_PIN) == HIGH && (micros() - t0) < 2000) {
      // ~2 ms max wait
      delayMicroseconds(5);
    }
#endif
  }

  // SPI helpers
  static void spi_begin(GPIOPin *cs) {
    cs->digital_write(false);
    delayMicroseconds(5);
    wait_so_low_();
  }
  static void spi_end(GPIOPin *cs) {
    cs->digital_write(true);
    delayMicroseconds(5);
  }
  static void write_reg(uint8_t addr, uint8_t val) {
  spi_begin(g_cs_global);
    uint8_t a = addr | WRITE_SINGLE_BYTE;
    SPI.transfer(a);
    SPI.transfer(val);
  spi_end(g_cs_global);
    if (g_spi_trace) {
      ESP_LOGD(TAG, "SPI WR 0x%02X <= 0x%02X", addr, val);
    }
  }
  static uint8_t read_reg(uint8_t addr) {
  spi_begin(g_cs_global);
    // For status registers (0x30..0x3D), use READ_BURST (per CC1101 status access rules)
    bool is_status = (addr >= 0x30 && addr <= 0x3D);
    uint8_t a = addr | (is_status ? READ_BURST : READ_SINGLE_BYTE);
    SPI.transfer(a);
    uint8_t v = SPI.transfer(0);
  spi_end(g_cs_global);
    if (g_spi_trace) {
      ESP_LOGD(TAG, "SPI RD 0x%02X => 0x%02X", addr, v);
    }
    return v;
  }
  static void read_burst(uint8_t addr, uint8_t *buf, uint8_t len) {
  spi_begin(g_cs_global);
    SPI.transfer(addr | READ_BURST);
    for (uint8_t i = 0; i < len; i++) buf[i] = SPI.transfer(0);
  spi_end(g_cs_global);
    if (g_spi_trace) {
      ESP_LOGD(TAG, "SPI RDB 0x%02X len=%u", addr, len);
    }
  }
  static void write_burst(uint8_t addr, const uint8_t *buf, uint8_t len) {
  spi_begin(g_cs_global);
    SPI.transfer(addr | WRITE_BURST);
    for (uint8_t i = 0; i < len; i++) SPI.transfer(buf[i]);
  spi_end(g_cs_global);
    if (g_spi_trace) {
      ESP_LOGD(TAG, "SPI WRB 0x%02X len=%u", addr, len);
    }
  }
  static void strobe(uint8_t cmd) {
  spi_begin(g_cs_global);
    SPI.transfer(cmd);
  spi_end(g_cs_global);
    if (g_spi_trace) {
      ESP_LOGD(TAG, "SPI STR 0x%02X", cmd);
    }
  }

  // From original: convert RSSI register to dBm
  // Convert CC1101 RSSI register (unsigned) to dBm per TI app note.
  // Use wider integer arithmetic to avoid overflow/wrap issues.
  static int rssi_to_dbm(uint8_t rssi_dec) {
    if (rssi_dec >= 128) {
      // For values >= 128, subtract 256 before halving and offsetting.
      return ((static_cast<int>(rssi_dec) - 256) / 2) - 74;
    }
    return (static_cast<int>(rssi_dec) / 2) - 74;
  }

  // Frequency setup assuming 26 MHz crystal
  static void setMHZ(float mhz) {
    // Use double precision for the math to reduce rounding error before register quantization
    const double f_xosc = 26.0;
    uint32_t freq = (uint32_t)((static_cast<double>(mhz) * 65536.0) / f_xosc);
    write_reg(FREQ2, (freq >> 16) & 0xFF);
    write_reg(FREQ1, (freq >> 8) & 0xFF);
    write_reg(FREQ0, freq & 0xFF);
  }

  static void cc1101_reset() {
    // Per datasheet, ensure CS is toggled before issuing SRES
  g_cs_global->digital_write(true);
    delayMicroseconds(30);
  g_cs_global->digital_write(false);
    delayMicroseconds(30);
  g_cs_global->digital_write(true);
    delay(1);
    strobe(SRES);
    delay(1);
    strobe(SFTX);
    strobe(SFRX);
  }

  static void cc1101_configureRF_0(float freq) {
    write_reg(IOCFG2, 0x0D);
    write_reg(IOCFG0, 0x06);
    write_reg(FIFOTHR, 0x47);
    write_reg(SYNC1, 0x55);
    write_reg(SYNC0, 0x00);
    write_reg(PKTCTRL1, 0x00);
    write_reg(PKTCTRL0, 0x00);
    write_reg(FSCTRL1, 0x08);
    setMHZ(freq);
    write_reg(MDMCFG4, 0xF6);
    write_reg(MDMCFG3, 0x83);
    write_reg(MDMCFG2, 0x02);
    write_reg(MDMCFG1, 0x00);
    write_reg(MDMCFG0, 0x00);
    write_reg(DEVIATN, 0x15);
    write_reg(MCSM1, 0x00);
    write_reg(MCSM0, 0x18);
    write_reg(FOCCFG, 0x1D);
    write_reg(BSCFG, 0x1C);
    write_reg(AGCCTRL2, 0xC7);
    write_reg(AGCCTRL1, 0x00);
    write_reg(AGCCTRL0, 0xB2);
    write_reg(WORCTRL, 0xFB);
    write_reg(FREND1, 0xB6);
    write_reg(FSCAL3, 0xE9);
    write_reg(FSCAL2, 0x2A);
    write_reg(FSCAL1, 0x00);
    write_reg(FSCAL0, 0x1F);
    write_reg(TEST2, 0x81);
    write_reg(TEST1, 0x35);
    write_reg(TEST0, 0x09);
    // PATABLE default minimal power
    const uint8_t PA[8] = {0x60,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
    write_burst(PATABLE_ADDR, PA, 8);
  }

  static void cc1101_rec_mode() {
    strobe(SIDLE);
    strobe(SRX);
    // Wait for RX state (0x0D..0x0F)
    uint8_t m = 0xFF;
    uint32_t t0 = millis();
    while (millis() - t0 < 300) {
      m = read_reg(MARCSTATE_ADDR) & 0x1F;
      if (m == 0x0D || m == 0x0E || m == 0x0F) break;
    }
  }

  // --- CRC Kermit (ported) ---
  static uint16_t crc_tab[256];
  static bool crc_inited = false;
  static void init_crc_tab() {
    for (uint16_t i = 0; i < 256; i++) {
      uint16_t crc = 0;
      uint16_t c = i;
      for (uint16_t j = 0; j < 8; j++) {
        if ((crc ^ c) & 0x0001) crc = (crc >> 1) ^ 0x8408;
        else crc >>= 1;
        c >>= 1;
      }
      crc_tab[i] = crc;
    }
    crc_inited = true;
  }
  static uint16_t crc_kermit(const uint8_t *data, size_t len) {
    if (!crc_inited) init_crc_tab();
    uint16_t crc = 0x0000;
    for (size_t a = 0; a < len; a++) {
      uint16_t short_c = 0x00FF & (uint16_t) data[a];
      uint16_t tmp = crc ^ short_c;
      crc = (crc >> 8) ^ crc_tab[tmp & 0xFF];
    }
    uint16_t low_byte  = (crc & 0xFF00) >> 8;
    uint16_t high_byte = (crc & 0x00FF) << 8;
    return (uint16_t)(low_byte | high_byte);
  }

  // Encode with start/stop bits and bit-reverse (ported)
  static int encode2serial_1_3(uint8_t *in, int in_len, uint8_t *out) {
    int j = 0;
    for (int i = 0; i < in_len * 8; i++) {
      if (i % 8 == 0) {
        if (i > 0) {
          // 3 stop bits (1)
          for (int k = 0; k < 3; k++) {
            int bytepos = j / 8;
            int bitpos = 7 - (j % 8);
            out[bytepos] |= (1 << bitpos);
            j++;
          }
        }
        // start bit 0
        int bytepos = j / 8; int bitpos = 7 - (j % 8);
        out[bytepos] &= ~(1 << bitpos);
        j++;
      }
      int bytepos = i / 8;
      int bitpos = i % 8;
      uint8_t mask = 1 << bitpos;
      bool one = (in[bytepos] & mask) > 0;
      int o_byte = j / 8; int o_bit = 7 - (j % 8);
      if (one) out[o_byte] |= 1 << o_bit; else out[o_byte] &= ~(1 << o_bit);
      j++;
    }
    // pad remaining bits in last byte with stop bits
    while (j % 8 > 0) {
      int o_byte = j / 8; int o_bit = 7 - (j % 8);
      out[o_byte] |= 1 << o_bit; j++;
    }
    out[j/8] = 0xFF; // sentinel
    return (j/8) + 1;
  }

  static int Make_Radian_Master_req(uint8_t *out, uint8_t year, uint32_t serial) {
    uint8_t payload[] = {0x13,0x10,0x00,0x45,0xFF,0xFF,0xFF,0xFF,0x00,0x45,0x20,0x0A,0x50,0x14,0x00,0x0A,0x40,0xFF,0xFF};
    uint8_t sync[]    = {0x50,0x00,0x00,0x00,0x03,0xFF,0xFF,0xFF,0xFF};
    payload[4]  = year;
    payload[5]  = (uint8_t)((serial & 0x00FF0000) >> 16);
    payload[6]  = (uint8_t)((serial & 0x0000FF00) >> 8);
    payload[7]  = (uint8_t) (serial & 0x000000FF);
    uint16_t crc = crc_kermit(payload, sizeof(payload)-2);
    payload[sizeof(payload)-2] = (uint8_t)((crc & 0xFF00) >> 8);
    payload[sizeof(payload)-1] = (uint8_t)(crc & 0x00FF);
    memcpy(out, sync, sizeof(sync));
    int enc_len = encode2serial_1_3(payload, sizeof(payload), &out[sizeof(sync)]);
    return enc_len + sizeof(sync);
  }

  // Decode oversampled serial back to bytes (ported)
  static uint8_t decode_4bitpbit_serial(uint8_t *rx, int total_bytes, uint8_t *decoded) {
    uint8_t bit_pol = rx[0] & 0x80;
    uint16_t dest_byte_cnt = 0;
    uint8_t dest_bit_cnt = 0;
    uint8_t bit_cnt = 0;
    int8_t bit_cnt_flush_S8 = 0;
    for (int i = 0; i < total_bytes; i++) {
      uint8_t cur = rx[i];
      for (int j = 0; j < 8; j++) {
        if ((cur & 0x80) == bit_pol) bit_cnt++;
        else if (bit_cnt == 1) {
          bit_pol = cur & 0x80;
          bit_cnt = bit_cnt_flush_S8 + 1;
        } else {
          bit_cnt_flush_S8 = bit_cnt;
          bit_cnt = (bit_cnt + 2) / 4;
          bit_cnt_flush_S8 = bit_cnt_flush_S8 - (bit_cnt * 4);
          for (int k = 0; k < bit_cnt; k++) {
            if (dest_bit_cnt < 8) {
              decoded[dest_byte_cnt] >>= 1;
              decoded[dest_byte_cnt] |= bit_pol ? 0x80 : 0x00;
            }
            dest_bit_cnt++;
            if ((dest_bit_cnt == 10) && (!bit_pol)) return dest_byte_cnt; // stop bit error
            if ((dest_bit_cnt >= 11) && (!bit_pol)) { // start bit
              dest_bit_cnt = 0;
              dest_byte_cnt++;
            }
          }
          bit_pol = cur & 0x80;
          bit_cnt = 1;
        }
        cur <<= 1;
      }
    }
    return dest_byte_cnt;
  }

  // Receive helper: find sync, then capture frame at higher data rate (ported)
  static int receive_radian_frame(int size_byte, int rx_tmo_ms, uint8_t *rx_buf, int rx_buf_sz) {
    uint8_t l_byte_in_rx = 0;
    uint16_t l_total = 0;
    uint16_t frame_sz = ((size_byte * (8 + 3)) / 8) + 1;
    if (frame_sz * 4 > rx_buf_sz) return 0;
    strobe(SFRX);
    write_reg(MCSM1, 0x0F);
    write_reg(MDMCFG2, 0x02);
    write_reg(SYNC1, 0x55);
    write_reg(SYNC0, 0x50);
    write_reg(MDMCFG4, 0xF6);
    write_reg(MDMCFG3, 0x83);
    write_reg(PKTLEN, 1);
    cc1101_rec_mode();
    int l_tmo = 0;
    while (!g_gdo0_global->digital_read() && (l_tmo < rx_tmo_ms)) { delay(1); l_tmo++; }
    if (!(l_tmo < rx_tmo_ms)) return 0;
    while ((l_byte_in_rx == 0) && (l_tmo < rx_tmo_ms)) {
      delay(5); l_tmo += 5;
      l_byte_in_rx = (read_reg(RXBYTES_ADDR) & RXBYTES_MASK);
      if (l_byte_in_rx) read_burst(RX_FIFO_ADDR, &rx_buf[0], l_byte_in_rx);
    }
    if (!(l_tmo < rx_tmo_ms && l_byte_in_rx > 0)) return 0;

    // Switch for frame receive
    write_reg(SYNC1, 0xFF);
    write_reg(SYNC0, 0xF0);
    write_reg(MDMCFG4, 0xF8);
    write_reg(MDMCFG3, 0x83);
    write_reg(PKTCTRL0, 0x02);
    strobe(SFRX);
    cc1101_rec_mode();
    l_total = 0; l_byte_in_rx = 1; l_tmo = 0;
    while (!g_gdo0_global->digital_read() && (l_tmo < rx_tmo_ms)) { delay(1); l_tmo++; }
    if (!(l_tmo < rx_tmo_ms)) return 0;
    while ((l_total < (frame_sz * 4)) && (l_tmo < rx_tmo_ms)) {
      delay(5); l_tmo += 5;
      l_byte_in_rx = (read_reg(RXBYTES_ADDR) & RXBYTES_MASK);
      if (l_byte_in_rx) {
        read_burst(RX_FIFO_ADDR, &rx_buf[l_total], l_byte_in_rx);
        l_total += l_byte_in_rx;
      }
    }
    if (!(l_tmo < rx_tmo_ms && l_total > 0)) return 0;
    strobe(SFRX);
    strobe(SIDLE);
    // Restore defaults
    write_reg(MDMCFG4, 0xF6);
    write_reg(MDMCFG3, 0x83);
    write_reg(PKTCTRL0, 0x00);
    write_reg(PKTLEN, 38);
    write_reg(SYNC1, 0x55);
    write_reg(SYNC0, 0x00);
    return l_total;
  }

  // Heuristic: raw oversampled buffer should contain 0xFF bytes if a RADIAN frame was captured
  static bool looks_like_radian_raw(const uint8_t *buf, int len) {
    for (int i = 0; i < len; i++) {
      if (buf[i] == 0xFF) return true;
    }
    return false;
  }

  static MeterData parse_meter(uint8_t *decoded, uint8_t size) {
    MeterData d;
    if (size >= 30) {
      d.liters = decoded[18] + (decoded[19] << 8) + (decoded[20] << 16) + (decoded[21] << 24);
    }
    if (size >= 48) {
      d.reads_counter = decoded[48];
      d.battery_left = decoded[31];
      d.time_start = decoded[44];
      d.time_end = decoded[45];
    }
    return d;
  }

  static bool get_meter_data(float freq_mhz, uint8_t year, uint32_t serial, uint32_t ack_timeout_ms, uint32_t data_timeout_ms, MeterData &out) {
    // Configure baseline RF (should be done already)
    cc1101_configureRF_0(freq_mhz);
    // Build wake-up buffer and request
    const uint8_t wupbyte = 0x55; // preamble 0101...
    uint8_t wupbuf[8]; for (int i=0;i<8;i++) wupbuf[i]=wupbyte;
    uint8_t txbuf[128]; memset(txbuf,0,sizeof(txbuf));
    int txlen = Make_Radian_Master_req(txbuf, year, serial);

    // Send 2s of wake-up preamble then the master request
    write_reg(MDMCFG2, 0x00); // no preamble/sync auto
    write_reg(PKTCTRL0, 0x02); // infinite length
    // Start TX and stream wakeup preamble continuously
    write_burst(TX_FIFO_ADDR, wupbuf, 8);
    strobe(STX);
    delay(10);
    // Feed ~2.5-3s of wake-up preamble while avoiding FIFO underflow
    uint16_t remain = 125; // ~2.5s with 20ms pacing
    while (remain--) {
      // If FIFO has room, push another 8 bytes of 0x55
      uint8_t used = (read_reg(TXBYTES_ADDR) & 0x7F);
      if (used <= 56) { // keep headroom
        write_burst(TX_FIFO_ADDR, wupbuf, 8);
      }
      delay(20);
    }
    // After wake-up, small guard time before request
    delay(200);
    // Stream the entire RADIAN master request into the TX FIFO
    int sent = 0;
    uint32_t t0 = millis();
    while (sent < txlen && (millis() - t0) < 2000) {
      uint8_t used = (read_reg(TXBYTES_ADDR) & 0x7F);
      uint8_t free_space = (used < 64) ? (uint8_t)(64 - used) : 0;
      if (free_space == 0) { delay(5); continue; }
      uint8_t chunk = (uint8_t) std::min<int>(free_space, txlen - sent);
      write_burst(TX_FIFO_ADDR, &txbuf[sent], chunk);
      sent += chunk;
      // brief pacing to allow FIFO to drain
      delay(2);
    }
    // Wait briefly for TX to finish, then flush TX FIFO to return to IDLE
    uint8_t marc = 0xFF; t0 = millis();
    do {
      delay(5);
      marc = read_reg(MARCSTATE_ADDR) & 0x1F; // 0x02 = TX
    } while (marc == 0x02 && (millis() - t0) < 700);
    strobe(SFTX);
    // restore default packet config
    write_reg(MDMCFG2, 0x02);
    write_reg(PKTCTRL0, 0x00);

  // Receive short ack
    uint8_t rxRaw[1000];
  int sz = receive_radian_frame(0x12, ack_timeout_ms, rxRaw, sizeof(rxRaw));
    (void) sz; // optional
  // Receive main data frame
  int rxSize = receive_radian_frame(0x7C, data_timeout_ms, rxRaw, sizeof(rxRaw));
    if (rxSize <= 0) return false;
    // Decode oversampled into bytes
    uint8_t decoded[256]; memset(decoded, 0, sizeof(decoded));
    uint8_t dsz = decode_4bitpbit_serial(rxRaw, rxSize, decoded);
    out = parse_meter(decoded, dsz);
    // Radio diagnostics
    out.rssi = read_reg(RSSI_ADDR);
    out.rssi_dbm = rssi_to_dbm(read_reg(RSSI_ADDR));
    out.lqi = read_reg(LQI_ADDR);
    return true;
  }

void EverbluComponent::setup() {
  ESP_LOGI(TAG, "Init CC1101 @ %.6f MHz", this->frequency_);
  this->cs_pin_->setup();
  this->cs_pin_->pin_mode(gpio::FLAG_OUTPUT);
  this->cs_pin_->digital_write(true);
  this->gdo0_pin_->setup();
  this->gdo0_pin_->pin_mode(gpio::FLAG_INPUT | gpio::FLAG_PULLUP);
  if (this->error_led_pin_ != nullptr) {
    this->error_led_pin_->setup();
    this->error_led_pin_->pin_mode(gpio::FLAG_OUTPUT);
    bool off = this->error_led_inverted_ ? true : false;
    this->error_led_pin_->digital_write(off);
  }
  SPI.begin();
#ifdef ARDUINO
#if defined(ESP8266)
  SPI.setFrequency(500000);
#endif
  SPI.setDataMode(SPI_MODE0);
  SPI.setBitOrder(MSBFIRST);
#endif
  g_cs_global = this->cs_pin_;
  g_gdo0_global = this->gdo0_pin_;
  g_self = this;
  cc1101_reset();
  // Probe radio with a few retries and log PART/VER for diagnostics
  bool ok = false;
  uint8_t last_pn = 0, last_ver = 0;
  for (int attempt = 1; attempt <= 3 && !ok; attempt++) {
    last_pn = read_reg(PARTNUM_ADDR);
    last_ver = read_reg(VERSION_ADDR);
    ESP_LOGD(TAG, "CC1101 probe attempt %d: PART=0x%02X VER=0x%02X", attempt, last_pn, last_ver);
    ok = !(last_pn == 0xFF || last_ver == 0xFF || (last_pn == 0x00 && last_ver == 0x00));
    if (!ok) { cc1101_reset(); delay(5); }
  }
  this->radio_ok_ = ok;
  if (!this->radio_ok_) {
    ESP_LOGE(TAG, "CC1101 not detected on SPI (PART=0x%02X VER=0x%02X). Check wiring, power, and CS/GDO0 pins.", last_pn, last_ver);
#if defined(ESP8266)
  // Extra hint: on ESP8266 HW SPI, MISO=GPIO12, MOSI=GPIO13, SCK=GPIO14
  int miso_lvl = digitalRead(12);
  int mosi_lvl = digitalRead(13);
  int sck_lvl  = digitalRead(14);
  int cs_lvl   = this->cs_pin_ ? (this->cs_pin_->digital_read() ? 1 : 0) : -1;
  ESP_LOGD(TAG, "Line levels: MISO(GPIO12)=%d MOSI(GPIO13)=%d SCK(GPIO14)=%d CS=%d", miso_lvl, mosi_lvl, sck_lvl, cs_lvl);
#endif
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
  } else {
    ESP_LOGI(TAG, "CC1101 radio found OK (PART=0x%02X VER=0x%02X)", last_pn, last_ver);
    cc1101_configureRF_0(this->frequency_);
    if (this->disc_freq_sensor_) this->disc_freq_sensor_->publish_state(this->frequency_);
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(true);
    this->stop_error_blink_();
  }
  if (this->read_at_startup_ && this->should_read_today_()) {
    MeterData d;
    if (this->perform_read_(d)) this->publish_(d);
  }
}

void EverbluComponent::process_scan_state_() {
  uint32_t now = millis();
  switch (this->scan_state_) {
    case ScanState::Idle:
      break;
    case ScanState::Init: {
      // Prepare first step
      this->scan_state_ = ScanState::Settle;
      // Apply initial frequency and allow small settle time
      this->frequency_ = this->scan_current_;
      cc1101_configureRF_0(this->frequency_);
      this->scan_next_ms_ = now + 25; // settle
  ESP_LOGD(TAG, "Scan init at %.6f MHz", this->frequency_);
      break;
    }
    case ScanState::Settle: {
      if (now >= this->scan_next_ms_) {
        if (this->is_busy()) {
          // Wait for any read to finish before starting a new one
          break;
        }
        // Start a read attempt without publishing intermediate results
        this->publish_when_done_ = false;
        this->start_read();
        this->scan_state_ = ScanState::WaitRead;
      }
      break;
    }
    case ScanState::WaitRead: {
      if (this->read_state_ == ReadState::Idle) {
        if (this->last_read_success_) {
          this->scan_found_ = true;
          this->scan_best_freq_ = this->frequency_;
          this->scan_data_ = this->pending_data_;
          this->scan_state_ = ScanState::Done;
        } else {
          this->scan_state_ = ScanState::Advance;
        }
      }
      break;
    }
    case ScanState::Advance: {
      // Move to the next frequency in current direction; if done, switch direction once
      float next = this->scan_current_ + (this->scan_dir_ == 0 ? this->scan_step_ : -this->scan_step_);
  bool in_range = (next >= this->nb_scan_start_ - 1e-6f && next <= this->nb_scan_end_ + 1e-6f);
      if (!in_range) {
        if (this->scan_dir_ == 0) {
          // Switch to descending
          this->scan_dir_ = 1;
          this->scan_current_ = this->nb_scan_end_;
        } else {
          // Completed both directions
          this->scan_state_ = ScanState::Done;
          break;
        }
      } else {
        this->scan_current_ = next;
      }
      // Apply new frequency and settle
      this->frequency_ = this->scan_current_;
      cc1101_configureRF_0(this->frequency_);
      this->scan_next_ms_ = now + 25;
      this->scan_state_ = ScanState::Settle;
  ESP_LOGD(TAG, "Scan step at %.6f MHz (dir %d)", this->frequency_, this->scan_dir_);
      break;
    }
    case ScanState::Done: {
      // If coarse pass found a candidate, automatically refine with a fine scan around it
      if (this->scan_found_ && this->scan_phase_ == ScanPhase::Coarse) {
        this->scan_phase_ = ScanPhase::Fine;
        // Narrow window +/- 0.010 MHz around best and use finer step
        float center = this->scan_best_freq_;
        this->nb_scan_start_ = center - 0.010f;
        this->nb_scan_end_   = center + 0.010f;
        if (this->nb_scan_start_ > this->nb_scan_end_) std::swap(this->nb_scan_start_, this->nb_scan_end_);
        this->scan_step_ = 0.00025f; // 0.25 kHz
        this->scan_current_ = this->nb_scan_start_;
        this->scan_found_ = false;
        this->scan_deep_ = true;
        this->scan_state_ = ScanState::Init;
        ESP_LOGI(TAG, "Frequency discovery coarse success at %.6f MHz; refining +/-0.010 MHz at 0.25 kHz", center);
        break;
      }

      if (this->scan_found_) {
        ESP_LOGI(TAG, "Frequency discovery %s success: %.6f MHz",
                 this->scan_deep_ ? "(deep)" : "", this->scan_best_freq_);
        this->frequency_ = this->scan_best_freq_;
        cc1101_configureRF_0(this->frequency_);
        if (this->disc_freq_sensor_) this->disc_freq_sensor_->publish_state(this->frequency_);
        // Publish the data we captured
        this->publish_(this->scan_data_);
      } else {
        float base = this->scan_best_freq_;
        float span = 0.050f;
        ESP_LOGW(TAG, "Frequency discovery %s failed within +/-%.4f MHz of %.6f MHz",
                 this->scan_deep_ ? "(deep)" : "", span, base);
      }
      if (this->scan_bin_sensor_) this->scan_bin_sensor_->publish_state(false);
      this->scan_state_ = ScanState::Idle;
      this->scan_phase_ = ScanPhase::Coarse;
      break;
    }
    case ScanState::Cancelled:
      ESP_LOGI(TAG, "Discovery scan cancelled");
      if (this->scan_bin_sensor_) this->scan_bin_sensor_->publish_state(false);
      this->scan_state_ = ScanState::Idle;
      break;
    default:
      this->scan_state_ = ScanState::Idle;
      break;
  }
}

void EverbluComponent::set_spi_trace(bool b) {
  this->spi_trace_ = b;
  g_spi_trace = b;
  ESP_LOGI(TAG, "SPI trace %s", b ? "ENABLED" : "DISABLED");
}
void EverbluComponent::start_read() {
  // Initialize buffers and timing
  memset(this->txbuf_, 0, sizeof(this->txbuf_));
  this->txlen_ = Make_Radian_Master_req(this->txbuf_, this->meter_year_, this->meter_serial_);
  this->sent_ = 0;
  this->last_read_success_ = false;
  // Convert preamble duration to number of pacing ticks
  this->wup_remain_ = (this->preamble_ms_ + (this->preamble_pace_ms_ - 1)) / this->preamble_pace_ms_;
  this->rx_total_ = 0;
  this->rx_target_ = 0;
  this->size_byte_target_ = 0x7C; // expect main data frame
  this->state_t0_ = millis();
  this->next_ms_ = this->state_t0_;
  this->pending_data_ = MeterData{};
  // Ensure RF is configured to current frequency
  cc1101_configureRF_0(this->frequency_);
  this->read_state_ = ReadState::StartPreamble;
  ESP_LOGI(TAG, "Starting non-blocking meter read at %.6f MHz", this->frequency_);
}

void EverbluComponent::process_read_state_() {
  const uint8_t wupbyte = 0x55;
  uint32_t now = millis();
  switch (this->read_state_) {
    case ReadState::StartPreamble: {
      // Prepare for infinite-length TX with manual preamble feed
      // Ensure TX FIFO is clean before starting a new TX sequence
      strobe(SFTX);
      write_reg(MDMCFG2, 0x00);
      write_reg(PKTCTRL0, 0x02);
      uint8_t wupbuf[8]; for (int i=0;i<8;i++) wupbuf[i]=wupbyte;
      write_burst(TX_FIFO_ADDR, wupbuf, 8);
      strobe(STX);
      this->next_ms_ = now; // feed immediately
      this->read_state_ = ReadState::StreamPreamble;
      break;
    }
    case ReadState::StreamPreamble: {
      if (now >= this->next_ms_) {
        // Top up TX FIFO with 0x55 while pacing at ~20ms
        uint8_t used = (read_reg(TXBYTES_ADDR) & 0x7F);
        // If radio slipped out of TX, kick it back
        uint8_t marc = read_reg(MARCSTATE_ADDR) & 0x1F;
        if (marc != 0x02) {
          strobe(STX);
        }
        if (used <= 56) {
          uint8_t wupbuf[8]; for (int i=0;i<8;i++) wupbuf[i]=wupbyte;
          write_burst(TX_FIFO_ADDR, wupbuf, 8);
        }
        this->next_ms_ = now + this->preamble_pace_ms_;
        if (this->wup_remain_ > 0) this->wup_remain_--;
      }
      if (this->wup_remain_ == 0) {
        this->state_t0_ = now;
        this->next_ms_ = now + this->guard_ms_; // guard
        this->read_state_ = ReadState::GuardBeforeReq;
      }
      break;
    }
    case ReadState::GuardBeforeReq: {
      if (now >= this->next_ms_) {
        this->read_state_ = ReadState::StartRequest;
      }
      break;
    }
    case ReadState::StartRequest: {
      // Begin streaming request bytes into TX FIFO
      this->state_t0_ = now;
      this->read_state_ = ReadState::StreamRequest;
      break;
    }
    case ReadState::StreamRequest: {
      // Stream chunks when there is space; do not block
      uint8_t txb = read_reg(TXBYTES_ADDR);
      bool tx_underflow = (txb & 0x80) != 0; // bit7 indicates underflow for TXBYTES
      uint8_t used = (txb & 0x7F);
      // Keep radio in TX; recover from underflow or idle
      uint8_t marc = read_reg(MARCSTATE_ADDR) & 0x1F;
      if (tx_underflow || marc == 0x16 /*TXFIFO_UNDERFLOW*/ ) {
        ESP_LOGW(TAG, "TX underflow detected (MARC=0x%02X), recovering", marc);
        strobe(SFTX);
        strobe(STX);
        // Reset the stage timer to allow streaming to continue
        this->state_t0_ = now;
      } else if (marc != 0x02 /*TX*/) {
        // Not transmitting? Nudge back into TX
        strobe(STX);
      }
      uint8_t free_space = (used < 64) ? (uint8_t)(64 - used) : 0;
      // Ensure a large initial burst like the original implementation (up to 39 bytes)
      if (this->sent_ == 0 && free_space >= 16) {
        int initial = std::min<int>(39, this->txlen_);
        int to_send = std::min<int>(initial, free_space);
        if (to_send > 0) {
          write_burst(TX_FIFO_ADDR, &this->txbuf_[0], (uint8_t) to_send);
          this->sent_ += to_send;
        }
      }
      if (free_space > 0 && this->sent_ < this->txlen_) {
        uint8_t chunk = (uint8_t) std::min<int>(free_space, this->txlen_ - this->sent_);
        write_burst(TX_FIFO_ADDR, &this->txbuf_[this->sent_], chunk);
        this->sent_ += chunk;
      }
      if (this->sent_ >= this->txlen_) {
        // All bytes queued; wait for TX to finish
        this->state_t0_ = now;
        this->read_state_ = ReadState::WaitTxFinish;
      } else if (now - this->state_t0_ > this->tx_stream_timeout_ms_) {
        // Log diagnostics to help debug TX stalls
        uint8_t marc2 = read_reg(MARCSTATE_ADDR) & 0x1F;
        uint8_t txb2 = read_reg(TXBYTES_ADDR);
        ESP_LOGW(TAG, "TX streaming timeout (sent=%d/%d, MARC=0x%02X, TXBYTES=0x%02X used=%u)",
                 this->sent_, this->txlen_, marc2, txb2, (txb2 & 0x7F));
        this->read_state_ = ReadState::Fail;
      }
      break;
    }
    case ReadState::WaitTxFinish: {
      uint8_t marc = read_reg(MARCSTATE_ADDR) & 0x1F;
      if (marc != 0x02) {
        strobe(SFTX);
        // restore defaults
        write_reg(MDMCFG2, 0x02);
        write_reg(PKTCTRL0, 0x00);
        this->read_state_ = ReadState::DataSetupStage1;
      } else if (now - this->state_t0_ > this->wait_tx_finish_ms_) {
        ESP_LOGW(TAG, "TX did not finish in time");
        strobe(SFTX);
        write_reg(MDMCFG2, 0x02);
        write_reg(PKTCTRL0, 0x00);
        this->read_state_ = ReadState::Fail;
      }
      break;
    }
    case ReadState::DataSetupStage1: {
      // Stage 1: sync detect at lower data rate
      strobe(SFRX);
      write_reg(MCSM1, 0x0F);
      write_reg(MDMCFG2, 0x02);
      write_reg(SYNC1, 0x55);
      write_reg(SYNC0, 0x50);
      write_reg(MDMCFG4, 0xF6);
      write_reg(MDMCFG3, 0x83);
      write_reg(PKTLEN, 1);
      cc1101_rec_mode();
      this->state_t0_ = now;
      this->read_state_ = ReadState::DataWaitSync1;
      break;
    }
    case ReadState::DataWaitSync1: {
      if (g_gdo0_global->digital_read()) {
        this->read_state_ = ReadState::DataFetch1;
      } else if (now - this->state_t0_ > this->data_timeout_ms_) {
        ESP_LOGW(TAG, "Data sync stage1 timed out; proceeding to main frame");
        this->read_state_ = ReadState::DataSetupStage2;
      }
      break;
    }
    case ReadState::DataFetch1: {
      uint8_t l_byte_in_rx = (read_reg(RXBYTES_ADDR) & RXBYTES_MASK);
      if (l_byte_in_rx) {
        read_burst(RX_FIFO_ADDR, &this->rxRaw_[0], l_byte_in_rx);
        // Proceed to stage2 once any bytes received
        this->read_state_ = ReadState::DataSetupStage2;
      } else if (now - this->state_t0_ > this->data_timeout_ms_) {
        ESP_LOGW(TAG, "Data fetch stage1 timed out; proceeding to main frame");
        this->read_state_ = ReadState::DataSetupStage2;
      }
      break;
    }
    case ReadState::DataSetupStage2: {
      // Stage 2: switch to frame receive and capture oversampled frame
      write_reg(SYNC1, 0xFF);
      write_reg(SYNC0, 0xF0);
      write_reg(MDMCFG4, 0xF8);
      write_reg(MDMCFG3, 0x83);
      write_reg(PKTCTRL0, 0x02);
      strobe(SFRX);
      cc1101_rec_mode();
      this->rx_total_ = 0;
      int frame_sz = ((this->size_byte_target_ * (8 + 3)) / 8) + 1;
      this->rx_target_ = frame_sz * 4;
      this->state_t0_ = now;
      this->read_state_ = ReadState::DataWaitSync2;
      break;
    }
    case ReadState::DataWaitSync2: {
      if (g_gdo0_global->digital_read()) {
        this->read_state_ = ReadState::DataFetch2;
      } else if (now - this->state_t0_ > this->data_timeout_ms_) {
        ESP_LOGW(TAG, "Data sync stage2 timed out");
        this->read_state_ = ReadState::Fail;
      }
      break;
    }
    case ReadState::DataFetch2: {
      uint8_t l_byte_in_rx = (read_reg(RXBYTES_ADDR) & RXBYTES_MASK);
      if (l_byte_in_rx) {
        int to_read = std::min<int>(l_byte_in_rx, (int)sizeof(this->rxRaw_) - this->rx_total_);
        if (to_read > 0) {
          read_burst(RX_FIFO_ADDR, &this->rxRaw_[this->rx_total_], to_read);
          this->rx_total_ += to_read;
        }
      }
      if (this->rx_total_ >= this->rx_target_) {
        // Restore defaults
        strobe(SFRX);
        strobe(SIDLE);
        write_reg(MDMCFG4, 0xF6);
        write_reg(MDMCFG3, 0x83);
        write_reg(PKTCTRL0, 0x00);
        write_reg(PKTLEN, 38);
        write_reg(SYNC1, 0x55);
        write_reg(SYNC0, 0x00);
        // Heuristic validity check before decoding
        if (!looks_like_radian_raw(this->rxRaw_, this->rx_total_)) {
          ESP_LOGW(TAG, "Frame capture does not look like RADIAN (no 0xFF sentinel in raw %d bytes)", this->rx_total_);
          this->read_state_ = ReadState::Fail;
          break;
        }
        this->read_state_ = ReadState::Decode;
      } else if (now - this->state_t0_ > this->data_timeout_ms_) {
        ESP_LOGW(TAG, "Data fetch stage2 timed out after %d bytes", this->rx_total_);
        // Restore defaults before failing
        strobe(SFRX);
        strobe(SIDLE);
        write_reg(MDMCFG4, 0xF6);
        write_reg(MDMCFG3, 0x83);
        write_reg(PKTCTRL0, 0x00);
        write_reg(PKTLEN, 38);
        write_reg(SYNC1, 0x55);
        write_reg(SYNC0, 0x00);
        this->read_state_ = ReadState::Fail;
      }
      break;
    }
    case ReadState::Decode: {
      uint8_t decoded[256]; memset(decoded, 0, sizeof(decoded));
      uint8_t dsz = decode_4bitpbit_serial(this->rxRaw_, this->rx_total_, decoded);
      // Debug: log decoded size and a short prefix of payload for troubleshooting
      if (dsz > 0) {
        char buf[128];
        int n = std::min<int>(dsz, 16);
        int off = 0;
        for (int i = 0; i < n && off < (int)sizeof(buf) - 3; i++) {
          off += snprintf(buf + off, sizeof(buf) - off, "%02X", decoded[i]);
          if (i != n - 1) buf[off++] = ' ';
        }
        buf[std::min(off, (int)sizeof(buf) - 1)] = '\0';
        ESP_LOGD(TAG, "Decoded frame len=%u head=%s", dsz, buf);
      } else {
        ESP_LOGW(TAG, "Decoded frame length is zero; dropping");
      }
      this->pending_data_ = parse_meter(decoded, dsz);
      // Radio diagnostics
      this->pending_data_.rssi = read_reg(RSSI_ADDR);
      this->pending_data_.rssi_dbm = rssi_to_dbm(read_reg(RSSI_ADDR));
      this->pending_data_.lqi = read_reg(LQI_ADDR);
  // Basic validity check: require at least some fields to be non-zero
  ESP_LOGD(TAG, "Parsed fields: liters=%d battery=%d counter=%d tstart=%d tend=%d",
       this->pending_data_.liters, this->pending_data_.battery_left, this->pending_data_.reads_counter,
       this->pending_data_.time_start, this->pending_data_.time_end);
  bool valid = (dsz >= 48) && (this->pending_data_.reads_counter > 0 || this->pending_data_.battery_left > 0 || this->pending_data_.liters > 0);
      if (!valid) {
        ESP_LOGW(TAG, "Decoded frame invalid or too short (len=%u); dropping", dsz);
        this->read_state_ = ReadState::Fail;
      } else {
        this->read_state_ = ReadState::Publish;
      }
      break;
    }
    case ReadState::Publish: {
      if (this->publish_when_done_) {
        this->publish_(this->pending_data_);
        // Keep last known wake/sleep hours
        this->last_time_start_ = this->pending_data_.time_start;
        this->last_time_end_ = this->pending_data_.time_end;
      }
      this->last_read_success_ = true;
      ESP_LOGI(TAG, "Read complete");
      this->read_state_ = ReadState::Idle;
      this->publish_when_done_ = false;
      break;
    }
    case ReadState::Fail: {
      ESP_LOGW(TAG, "Non-blocking read failed");
      // Attempt to restore default packet config and flush RX/TX
      strobe(SFRX);
      strobe(SFTX);
      strobe(SIDLE);
      write_reg(MDMCFG4, 0xF6);
      write_reg(MDMCFG3, 0x83);
      write_reg(MDMCFG2, 0x02);
      write_reg(PKTCTRL0, 0x00);
      write_reg(PKTLEN, 38);
      write_reg(SYNC1, 0x55);
      write_reg(SYNC0, 0x00);
      this->read_state_ = ReadState::Idle;
      this->publish_when_done_ = false;
      this->last_read_success_ = false;
      break;
    }
    default:
      this->read_state_ = ReadState::Idle;
      break;
  }
}

bool EverbluComponent::should_read_today_() {
  if (this->read_schedule_ == "Monday-Friday") {
    if (this->time_ == nullptr) return true;
    auto now = this->time_->now();
    if (!now.is_valid()) return true;
    int w = now.day_of_week; // 1=Mon..7=Sun
    bool weekday_ok = (w >= 1 && w <= 5);
    if (!weekday_ok) {
      ESP_LOGI(TAG, "Schedule gate: not weekday (dow=%d)", w);
      return false;
    }
    // If we know meter wake/sleep hours, gate reads to that window
    if (this->last_time_start_ >= 0 && this->last_time_end_ >= 0) {
      int h = now.hour;
      int s = this->last_time_start_;
      int e = this->last_time_end_;
      // Sanity check
      if (s < 0 || s > 23 || e < 0 || e > 23) {
        ESP_LOGW(TAG, "Schedule gate: ignoring invalid window %d-%d (hour=%d)", s, e, h);
      } else if (s == e) {
        // Interpret equal start/end as 'always allowed' (avoid permanent block)
        ESP_LOGD(TAG, "Schedule gate: start==end (%d), treating as always-on", s);
      } else {
        bool in_window = false;
        if (s <= e) {
          // Same-day window (e.g., 08-18)
          in_window = (h >= s && h <= e);
        } else {
          // Wrap-around window across midnight (e.g., 21-06)
          in_window = (h >= s || h <= e);
        }
        if (!in_window) {
          ESP_LOGI(TAG, "Schedule gate: hour %d outside window %d-%d (wrap%s)", h, s, e, (s>e?"=yes":"=no"));
          return false;
        }
      }
    }
    return true;
  }
  if (this->read_schedule_ == "Monday-Saturday") {
    if (this->time_ == nullptr) return true;
    auto now = this->time_->now();
    if (!now.is_valid()) return true;
    int w = now.day_of_week;
    bool weekday_ok = (w >= 1 && w <= 6);
    if (!weekday_ok) {
      ESP_LOGI(TAG, "Schedule gate: not Mon-Sat (dow=%d)", w);
      return false;
    }
    if (this->last_time_start_ >= 0 && this->last_time_end_ >= 0) {
      int h = now.hour;
      int s = this->last_time_start_;
      int e = this->last_time_end_;
      if (s < 0 || s > 23 || e < 0 || e > 23) {
        ESP_LOGW(TAG, "Schedule gate: ignoring invalid window %d-%d (hour=%d)", s, e, h);
      } else if (s == e) {
        ESP_LOGD(TAG, "Schedule gate: start==end (%d), treating as always-on", s);
      } else {
        bool in_window = (s <= e) ? (h >= s && h <= e) : (h >= s || h <= e);
        if (!in_window) {
          ESP_LOGI(TAG, "Schedule gate: hour %d outside window %d-%d (wrap%s)", h, s, e, (s>e?"=yes":"=no"));
          return false;
        }
      }
    }
    return true;
  }
  return true;
}

void EverbluComponent::update() {
  if (!this->radio_ok_) {
    ESP_LOGW(TAG, "Skipping read: CC1101 radio not detected");
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
    return;
  }
  this->stop_error_blink_();
  if (this->is_scanning()) {
    ESP_LOGI(TAG, "Skipping scheduled read: discovery scan in progress");
    return;
  }
  if (!this->should_read_today_()) {
    ESP_LOGI(TAG, "Skipping read today per schedule: %s", this->read_schedule_.c_str());
    return;
  }
  if (!this->is_busy()) {
    // Start a non-blocking read during the regular update cycle
    this->publish_when_done_ = true;
    this->start_read();
  } else {
    ESP_LOGD(TAG, "Update tick while read in progress; skipping new read");
  }
}

void EverbluComponent::reprobe_radio() {
  ESP_LOGI(TAG, "Re-probing CC1101 radio...");
  cc1101_reset();
  bool ok = false; uint8_t last_pn = 0, last_ver = 0;
  for (int attempt = 1; attempt <= 3 && !ok; attempt++) {
    last_pn = read_reg(PARTNUM_ADDR);
    last_ver = read_reg(VERSION_ADDR);
    ESP_LOGD(TAG, "CC1101 probe attempt %d: PART=0x%02X VER=0x%02X", attempt, last_pn, last_ver);
    ok = !(last_pn == 0xFF || last_ver == 0xFF || (last_pn == 0x00 && last_ver == 0x00));
    if (!ok) { cc1101_reset(); delay(5); }
  }
  this->radio_ok_ = ok;
  if (!ok) {
    ESP_LOGE(TAG, "CC1101 still not detected (PART=0x%02X VER=0x%02X).", last_pn, last_ver);
#if defined(ESP8266)
  int miso_lvl = digitalRead(12);
  int mosi_lvl = digitalRead(13);
  int sck_lvl  = digitalRead(14);
  int cs_lvl   = this->cs_pin_ ? (this->cs_pin_->digital_read() ? 1 : 0) : -1;
  ESP_LOGD(TAG, "Line levels: MISO(GPIO12)=%d MOSI(GPIO13)=%d SCK(GPIO14)=%d CS=%d", miso_lvl, mosi_lvl, sck_lvl, cs_lvl);
#endif
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
    return;
  }
  cc1101_configureRF_0(this->frequency_);
  if (this->disc_freq_sensor_) this->disc_freq_sensor_->publish_state(this->frequency_);
  if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(true);
  ESP_LOGI(TAG, "CC1101 detected and configured.");
  this->stop_error_blink_();
}

void EverbluComponent::dump_cc1101_status() {
  if (!this->radio_ok_) {
    ESP_LOGW(TAG, "Cannot dump CC1101 status: radio not detected");
    return;
  }
  uint8_t pn = read_reg(PARTNUM_ADDR);
  uint8_t ver = read_reg(VERSION_ADDR);
  uint8_t marc = read_reg(MARCSTATE_ADDR) & 0x1F;
  uint8_t lqi = read_reg(LQI_ADDR);
  uint8_t rssi = read_reg(RSSI_ADDR);
  uint8_t rxbytes = read_reg(RXBYTES_ADDR) & RXBYTES_MASK;
  ESP_LOGI(TAG, "CC1101: PART=0x%02X VER=0x%02X MARC=0x%02X LQI=%u RSSI=%u RXBYTES=%u", pn, ver, marc, lqi, rssi, rxbytes);
  uint8_t f2 = read_reg(FREQ2), f1 = read_reg(FREQ1), f0 = read_reg(FREQ0);
  ESP_LOGI(TAG, "CC1101 FREQ regs: %02X %02X %02X (%.6f MHz configured)", f2, f1, f0, this->frequency_);
  // Derive actual LO frequency from registers (assumes 26 MHz crystal)
  uint32_t freqw = ((uint32_t)f2 << 16) | ((uint32_t)f1 << 8) | (uint32_t)f0;
  double mhz_actual = (static_cast<double>(freqw) * 26.0) / 65536.0;
  ESP_LOGI(TAG, "CC1101 LO actual ~ %.6f MHz (quantized)", mhz_actual);
}

void EverbluComponent::spi_self_test() {
  ESP_LOGI(TAG, "Starting CC1101 SPI self-test...");
  // Basic CS line sanity
#if defined(ESP8266)
  int miso_lvl = digitalRead(12);
  int mosi_lvl = digitalRead(13);
  int sck_lvl  = digitalRead(14);
  int cs_lvl = this->cs_pin_ ? (this->cs_pin_->digital_read() ? 1 : 0) : -1;
  ESP_LOGI(TAG, "Line levels: MISO(GPIO12)=%d MOSI(GPIO13)=%d SCK(GPIO14)=%d CS=%d", miso_lvl, mosi_lvl, sck_lvl, cs_lvl);
#else
  int cs_lvl = this->cs_pin_ ? (this->cs_pin_->digital_read() ? 1 : 0) : -1;
  ESP_LOGI(TAG, "CS level=%d", cs_lvl);
#endif

  // Try PART/VERSION multiple times
  uint8_t pn1 = read_reg(PARTNUM_ADDR);
  uint8_t vr1 = read_reg(VERSION_ADDR);
  delay(2);
  uint8_t pn2 = read_reg(PARTNUM_ADDR);
  uint8_t vr2 = read_reg(VERSION_ADDR);
  ESP_LOGI(TAG, "PART 0x%02X/0x%02X VERSION 0x%02X/0x%02X", pn1, pn2, vr1, vr2);
  bool id_ok = !(pn1 == 0xFF || vr1 == 0xFF || (pn1 == 0x00 && vr1 == 0x00));

  // Safe write/readback test on FSCTRL1 (not destructive) and PATABLE[0]
  uint8_t fs_orig = read_reg(FSCTRL1);
  write_reg(FSCTRL1, fs_orig ^ 0x01);
  uint8_t fs_new = read_reg(FSCTRL1);
  write_reg(FSCTRL1, fs_orig); // restore

  // PATABLE read/write first entry
  uint8_t pa_buf[8]; memset(pa_buf, 0, sizeof(pa_buf));
  read_burst(PATABLE_ADDR, pa_buf, 8);
  uint8_t pa0_orig = pa_buf[0];
  uint8_t pa0_test = (pa0_orig == 0x60) ? 0x50 : 0x60; // toggle between common values
  uint8_t tmp_pa[8]; memcpy(tmp_pa, pa_buf, 8); tmp_pa[0] = pa0_test;
  write_burst(PATABLE_ADDR, tmp_pa, 8);
  memset(pa_buf, 0, sizeof(pa_buf));
  read_burst(PATABLE_ADDR, pa_buf, 8);
  bool pa_ok = (pa_buf[0] == pa0_test);
  // Restore original
  memcpy(tmp_pa, pa_buf, 8); tmp_pa[0] = pa0_orig; write_burst(PATABLE_ADDR, tmp_pa, 8);

  bool fs_ok = ((fs_new & 0x01) == (uint8_t)((fs_orig ^ 0x01) & 0x01));
  bool pass = id_ok && fs_ok && pa_ok;
  ESP_LOGI(TAG, "Self-test result: %s (ID:%s FS:%s PA:%s)", pass ? "PASS" : "FAIL",
           id_ok ? "OK" : "BAD", fs_ok ? "OK" : "BAD", pa_ok ? "OK" : "BAD");
}

bool EverbluComponent::perform_read_(MeterData &out) {
  // Deprecated blocking path retained for discovery; normal reads use non-blocking state machine.
  if (!this->radio_ok_) return false;
  return get_meter_data(this->frequency_, this->meter_year_, this->meter_serial_, this->ack_timeout_ms_, this->data_timeout_ms_, out);
}

void EverbluComponent::publish_(const MeterData &d) {
  // Basic sanity: if we never received a valid frame, do not publish misleading zeros
  // RSSI register ranges 0..255, LQI 0..255; use NaN when not meaningful
  const float nanv = NAN;
  if (this->liters_sensor_) this->liters_sensor_->publish_state(d.liters > 0 ? (float) d.liters : nanv);
  if (this->battery_sensor_) this->battery_sensor_->publish_state(d.battery_left > 0 ? (float) d.battery_left : nanv);
  if (this->reads_counter_sensor_) this->reads_counter_sensor_->publish_state(d.reads_counter > 0 ? (float) d.reads_counter : nanv);
  if (this->rssi_sensor_) this->rssi_sensor_->publish_state(this->radio_ok_ ? (float) d.rssi : nanv);
  if (this->rssi_dbm_sensor_) this->rssi_dbm_sensor_->publish_state(this->radio_ok_ ? (float) d.rssi_dbm : nanv);
  if (this->lqi_sensor_) this->lqi_sensor_->publish_state(this->radio_ok_ ? (float) d.lqi : nanv);
  if (this->time_start_sensor_) this->time_start_sensor_->publish_state(d.time_start > 0 ? (float) d.time_start : nanv);
  if (this->time_end_sensor_) this->time_end_sensor_->publish_state(d.time_end > 0 ? (float) d.time_end : nanv);
}

void EverbluComponent::loop() {
  if (!this->radio_ok_ && this->blink_on_failure_) {
    this->start_error_blink_();
  }
  // Advance non-blocking read state machine
  if (this->read_state_ != ReadState::Idle) {
    this->process_read_state_();
  }
  // Advance non-blocking discovery scan if active
  if (this->scan_state_ != ScanState::Idle) {
    this->process_scan_state_();
  }
}

void EverbluComponent::force_read() {
  if (!this->radio_ok_) {
    ESP_LOGW(TAG, "Force read requested but CC1101 not detected");
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
    return;
  }
  this->stop_error_blink_();
  if (this->is_scanning()) {
    ESP_LOGW(TAG, "Force read requested but a discovery scan is in progress; ignoring");
    return;
  }
  if (this->is_busy()) {
    ESP_LOGW(TAG, "Read already in progress; ignoring Force Read");
    return;
  }
  this->publish_when_done_ = true;
  this->start_read();
}

void EverbluComponent::discover_frequency() {
  if (!this->radio_ok_) {
    ESP_LOGW(TAG, "Frequency discovery requested but CC1101 not detected");
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
    return;
  }
  if (this->is_scanning()) {
    ESP_LOGW(TAG, "Discovery already in progress; ignoring new request");
    return;
  }
  this->stop_error_blink_();
  // Determine range and step
  const float base = this->frequency_;
  const float span = 0.050f;
  this->scan_step_ = 0.0010f; // 1.0 kHz coarse
    this->nb_scan_start_ = has_scan_range_ ? this->scan_start_ : (base - span);
  this->nb_scan_end_   = has_scan_range_ ? this->scan_end_   : (base + span);
  if (this->nb_scan_start_ > this->nb_scan_end_) std::swap(this->nb_scan_start_, this->nb_scan_end_);
  this->scan_deep_ = false;
  this->scan_phase_ = ScanPhase::Coarse;
  this->scan_state_ = ScanState::Init;
  this->scan_dir_ = 0;
  this->scan_current_ = this->nb_scan_start_;
  this->scan_found_ = false;
  this->scan_best_freq_ = base;
  this->scan_next_ms_ = millis();
  if (this->scan_bin_sensor_) this->scan_bin_sensor_->publish_state(true);
  ESP_LOGI(TAG, "Starting non-blocking frequency discovery %s: %.6f to %.6f MHz (step %.6f)",
           has_scan_range_ ? "(custom)" : "(auto)", this->nb_scan_start_, this->nb_scan_end_, this->scan_step_);
}

void EverbluComponent::discover_frequency_deep() {
  if (!this->radio_ok_) {
    ESP_LOGW(TAG, "Deep frequency discovery requested but CC1101 not detected");
    if (this->radio_bin_sensor_ != nullptr) this->radio_bin_sensor_->publish_state(false);
    if (this->blink_on_failure_) this->start_error_blink_();
    return;
  }
  if (this->is_scanning()) {
    ESP_LOGW(TAG, "Discovery already in progress; ignoring new request");
    return;
  }
  this->stop_error_blink_();
  const float base = this->frequency_;
  const float span = 0.050f;
  this->scan_step_ = 0.00025f; // 0.25 kHz
  // Prefer deep scan range; fallback to normal; else +/- span
  this->nb_scan_start_ = has_deep_scan_range_ ? deep_scan_start_ : (has_scan_range_ ? this->scan_start_ : (base - span));
  this->nb_scan_end_   = has_deep_scan_range_ ? deep_scan_end_   : (has_scan_range_ ? this->scan_end_   : (base + span));
  if (this->nb_scan_start_ > this->nb_scan_end_) std::swap(this->nb_scan_start_, this->nb_scan_end_);
  this->scan_deep_ = true;
  this->scan_state_ = ScanState::Init;
  this->scan_dir_ = 0;
  this->scan_current_ = this->nb_scan_start_;
  this->scan_found_ = false;
  this->scan_best_freq_ = base;
  this->scan_next_ms_ = millis();
  if (this->scan_bin_sensor_) this->scan_bin_sensor_->publish_state(true);
  ESP_LOGI(TAG, "Starting non-blocking deep frequency discovery %s: %.6f to %.6f MHz (step %.6f)",
           (has_deep_scan_range_ || has_scan_range_) ? "(custom)" : "(auto)", this->nb_scan_start_, this->nb_scan_end_, this->scan_step_);
}

void EverbluComponent::start_error_blink_() {
  if (!this->error_led_pin_) return;
  static uint32_t last_toggle = 0;
  uint32_t now = millis();
  if (now - last_toggle >= 500) { // 1 Hz blink
    this->blink_state_ = !this->blink_state_;
    bool level = this->error_led_inverted_ ? !this->blink_state_ : this->blink_state_;
    this->error_led_pin_->digital_write(level);
    last_toggle = now;
  }
}

void EverbluComponent::stop_error_blink_() {
  if (!this->error_led_pin_) return;
  this->blink_state_ = false;
  bool off = this->error_led_inverted_ ? true : false;
  this->error_led_pin_->digital_write(off);
}

void EverbluComponent::cancel_discovery() {
  if (this->scan_state_ == ScanState::Idle) {
    ESP_LOGW(TAG, "Cancel requested but no discovery scan is in progress");
    return;
  }
  this->scan_state_ = ScanState::Cancelled;
}

}  // namespace everblu
}  // namespace esphome
