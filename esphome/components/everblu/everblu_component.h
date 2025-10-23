#pragma once
#include "esphome/core/component.h"
#include "esphome/core/hal.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/time/real_time_clock.h"

#ifdef USE_ESP8266
#include <SPI.h>
#endif
#ifdef USE_ESP32
#include <SPI.h>
#endif

namespace esphome {
namespace everblu {

struct MeterData {
  int liters = 0;
  int reads_counter = 0;
  int battery_left = 0;   // months
  int time_start = 0;     // hour (0-23)
  int time_end = 0;       // hour (0-23)
  int rssi = 0;
  int rssi_dbm = 0;
  int lqi = 0;            // 0-255
};

class EverbluComponent : public PollingComponent {
 public:
  void set_cs_pin(GPIOPin *pin) { this->cs_pin_ = pin; }
  void set_gdo0_pin(GPIOPin *pin) { this->gdo0_pin_ = pin; }
  void set_frequency(float f) { this->frequency_ = f; }
  void set_meter_serial(uint32_t s) { this->meter_serial_ = s; }
  void set_meter_year(uint8_t y) { this->meter_year_ = y; }
  float get_frequency() const { return this->frequency_; }
  void set_read_schedule(const std::string &s) { this->read_schedule_ = s; }
  void set_read_at_startup(bool b) { this->read_at_startup_ = b; }
  void set_time(time::RealTimeClock *t) { this->time_ = t; }
  // Optional: blink an LED when radio init fails
  void set_error_led_pin(GPIOPin *pin) { this->error_led_pin_ = pin; }
  void set_blink_on_failure(bool b) { this->blink_on_failure_ = b; }
  void set_error_led_inverted(bool b) { this->error_led_inverted_ = b; }

  // Manual trigger (e.g., from a template button)
  void force_read();
  // Start a non-blocking read sequence; returns immediately. Progresses in loop().
  void start_read();
  // Whether a non-blocking read is currently running
  bool is_busy() const { return this->read_state_ != ReadState::Idle; }
  // Scan around the current frequency to find the meter; updates frequency_ on success
  void discover_frequency();
  // Deep scan with 1 kHz step for more precise discovery
  void discover_frequency_deep();
  // Re-probe the CC1101 radio presence and reconfigure if found
  void reprobe_radio();
  // Enable/disable verbose SPI tracing logs
  void set_spi_trace(bool b);
  // Dump a selection of CC1101 status/config registers to logs
  void dump_cc1101_status();
  // Run a basic SPI/CC1101 self-test with safe read/write checks
  void spi_self_test();

  // Optional scan ranges; if not set, fall back to +/- span around base frequency
  void set_scan_range(float start_mhz, float end_mhz) {
    this->scan_start_ = start_mhz; this->scan_end_ = end_mhz; this->has_scan_range_ = true;
  }
  void set_deep_scan_range(float start_mhz, float end_mhz) {
    this->deep_scan_start_ = start_mhz; this->deep_scan_end_ = end_mhz; this->has_deep_scan_range_ = true;
  }
  void clear_scan_ranges() { this->has_scan_range_ = false; this->has_deep_scan_range_ = false; }

  void set_liters_sensor(sensor::Sensor *s) { this->liters_sensor_ = s; }
  void set_battery_sensor(sensor::Sensor *s) { this->battery_sensor_ = s; }
  void set_reads_counter_sensor(sensor::Sensor *s) { this->reads_counter_sensor_ = s; }
  void set_rssi_sensor(sensor::Sensor *s) { this->rssi_sensor_ = s; }
  void set_rssi_dbm_sensor(sensor::Sensor *s) { this->rssi_dbm_sensor_ = s; }
  void set_lqi_sensor(sensor::Sensor *s) { this->lqi_sensor_ = s; }
  void set_time_start_sensor(sensor::Sensor *s) { this->time_start_sensor_ = s; }
  void set_time_end_sensor(sensor::Sensor *s) { this->time_end_sensor_ = s; }
  void set_discovered_frequency_sensor(sensor::Sensor *s) { this->disc_freq_sensor_ = s; }
  void set_radio_connected_binary_sensor(binary_sensor::BinarySensor *b) { this->radio_bin_sensor_ = b; }

  float get_setup_priority() const override { return setup_priority::DATA; }

  void setup() override;
  void loop() override;
  void update() override;

 protected:
  bool check_radio_();
  bool should_read_today_();
  bool perform_read_(MeterData &out);
  void publish_(const MeterData &d);
  void start_error_blink_();
  void stop_error_blink_();

  // Non-blocking read state machine
  enum class ReadState {
    Idle,
    Prepare,
    StartPreamble,
    StreamPreamble,
    GuardBeforeReq,
    StartRequest,
    StreamRequest,
    WaitTxFinish,
    DataSetupStage1,
    DataWaitSync1,
    DataFetch1,
    DataSetupStage2,
    DataWaitSync2,
    DataFetch2,
    Decode,
    Publish,
    Fail
  };
  void process_read_state_();

  ReadState read_state_{ReadState::Idle};
  uint32_t state_t0_{0};
  uint32_t next_ms_{0};
  uint16_t wup_remain_{0};
  uint8_t txbuf_[128];
  int txlen_{0};
  int sent_{0};
  uint8_t rxRaw_[1000];
  int rx_total_{0};
  int rx_target_{0};
  int size_byte_target_{0};
  uint32_t ack_timeout_ms_{500};
  uint32_t data_timeout_ms_{2000};
  bool publish_when_done_{false};
  MeterData pending_data_{};

  GPIOPin *cs_pin_{nullptr};
  GPIOPin *gdo0_pin_{nullptr};
  float frequency_{433.820f};
  uint32_t meter_serial_{0};
  uint8_t meter_year_{0};
  std::string read_schedule_{"Monday-Friday"};
  bool read_at_startup_{true};
  time::RealTimeClock *time_{nullptr};
  GPIOPin *error_led_pin_{nullptr};
  bool blink_on_failure_{true};
  bool error_led_inverted_{false};

  sensor::Sensor *liters_sensor_{nullptr};
  sensor::Sensor *battery_sensor_{nullptr};
  sensor::Sensor *reads_counter_sensor_{nullptr};
  sensor::Sensor *rssi_sensor_{nullptr};
  sensor::Sensor *rssi_dbm_sensor_{nullptr};
  sensor::Sensor *lqi_sensor_{nullptr};
  sensor::Sensor *time_start_sensor_{nullptr};
  sensor::Sensor *time_end_sensor_{nullptr};
  sensor::Sensor *disc_freq_sensor_{nullptr};
  binary_sensor::BinarySensor *radio_bin_sensor_{nullptr};

  bool radio_ok_{false};
  int last_time_start_{-1};
  int last_time_end_{-1};
  bool spi_trace_{false};
  bool blink_state_{false};

  // Optional absolute scan ranges
  bool has_scan_range_{false};
  float scan_start_{0.0f};
  float scan_end_{0.0f};
  bool has_deep_scan_range_{false};
  float deep_scan_start_{0.0f};
  float deep_scan_end_{0.0f};
};

}  // namespace everblu
}  // namespace esphome
