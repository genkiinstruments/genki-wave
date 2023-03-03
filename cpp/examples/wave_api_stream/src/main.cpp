#include <atomic>
#include <csignal>
#include <range/v3/view.hpp>
#include <string>

#include "ble_transport.h"
#include "wave_api_device.h"
#include "format.h"

int main()
{
    static std::atomic_bool term = false;

    for (const auto& signum: {SIGTERM, SIGINT})
        std::signal(signum, [](int) { term.store(true); });

    juce::MessageManager::getInstance();

    genki::BleAdapter        adapter;
    genki::ValueTreeListener listener{adapter.state};

    std::unique_ptr<genki::WaveApiDevice> wave;

    listener.property_changed = [&](juce::ValueTree& vt, const juce::Identifier& id)
    {
        if (vt.hasType(ID::BLUETOOTH_ADAPTER) && id == ID::status)
        {
            const auto is_powered_on = AdapterStatus((int) vt.getProperty(id)) == AdapterStatus::PoweredOn;

            fmt::print("{}\n", is_powered_on
                               ? "Adapter powered on, starting scan..."
                               : "Adapter powered off/disabled, stopping scan...");

            adapter.scan(is_powered_on);
        }
        else if (vt.hasType(ID::BLUETOOTH_DEVICE) && id == ID::last_seen)
        {
            if (vt.getProperty(ID::name).toString().isNotEmpty())
            {
                fmt::print("{} {} - rssi: {}\n",
                        vt.getProperty(ID::name).toString().toStdString(),
                        vt.getProperty(ID::address).toString().toStdString(),
                        (int) vt.getProperty(ID::rssi));
            }
        }
    };

    listener.child_added = [&](juce::ValueTree&, juce::ValueTree& vt)
    {
        const juce::String name = vt.getProperty(ID::name);

        // Note: Should preferably match on a BLE address instead...
        if (name.contains("Wave"))
        {
            fmt::print("Found device: {} connecting...\n", name);
            const auto ble_address = vt.getProperty(ID::address).toString();

            wave = std::make_unique<genki::WaveApiDevice>(
                    std::make_unique<genki::BleTransport>(adapter, ble_address),
                    [&](const genki::Wave::Api::Query& query, gsl::span<const gsl::byte> payload)
                    {
                        const auto id = static_cast<genki::Wave::Api::Query::Id>(query.id);
                        using Id = genki::Wave::Api::Query::Id;

                        if (id == Id::Datastream)
                        {
                            const auto& ds = genki::copy<genki::Wave::Datastream>(payload);
                            DBG(fmt::format("Datastream: gyro: {} acc: {}, orientation: {}",
                                    ds.data.gyro, ds.data.accel, ds.motionData.currentPose));
                        }
                        else if (id == Id::ButtonEvent)
                        {
                            const auto evt = genki::copy<genki::Wave::ButtonEvent>(payload);

                            DBG(fmt::format("Button event: {}", evt));

                            if (evt.id == genki::Wave::ButtonId::B && evt.action == genki::Wave::ButtonAction::Click)
                            {
                                wave->recenter();
                            }
                        }
                        else if (id == Id::DeviceInfo)
                        {
                            const auto [ver, board, mac, serial] = genki::copy<genki::Wave::DeviceInfo>(payload);

                            const auto mac_str = mac.data
                                                 | ranges::views::transform([](uint8_t b) { return fmt::format("{:02X}", b); })
                                                 | ranges::views::reverse
                                                 | ranges::views::join(':')
                                                 | ranges::to<std::string>();

                            DBG(fmt::format("Device info:\n"
                                            "  Firmware version: {}.{}.{}\n"
                                            "  Board version: {}\n"
                                            "  MAC address: {}\n"
                                            "  Serial number: {}",
                                    ver.major, ver.minor, ver.patch,
                                    board.c_str(),
                                    mac_str,
                                    serial.c_str()));
                        }
                        else if (id == Id::BatteryStatus)
                        {
                            const auto bs = genki::copy<genki::Wave::BatteryStatus>(payload);

                            DBG(fmt::format("Battery status: {}%{}\n",
                                    static_cast<int>(bs.percentage), bs.is_charging ? " (charging)" : ""));
                        }
                    }
            );

            // Assume Wave has been successfully connected after a short while.
            // Ideally you'd want to keep track of the connection state and send commands once connection has been
            // established and the characteristics discovered.
            juce::Timer::callAfterDelay(1000, [&]
            {
                wave->request_info();
                wave->read_battery();

                wave->update_display({
                        {
                                {0x00, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0x00, 0x00},
                                {0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0x00},
                                {0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00},
                                {0x00, 0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0x00, 0x00},
                                {0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00},
                        }
                });
            });

            adapter.scan(false);
        }
    };

    while (!term)
        juce::MessageManager::getInstance()->runDispatchLoopUntil(50);

    juce::MessageManager::deleteInstance();
    juce::DeletedAtShutdown::deleteAll();
}
