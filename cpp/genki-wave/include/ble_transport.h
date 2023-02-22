#pragma once

#include "juce_bluetooth/juce_bluetooth.h"

namespace genki {

struct BleTransport
{
    BleTransport(BleAdapter& a, juce::String addr) : adapter(a), address(std::move(addr)) {}

    juce::ValueTree connect(const BleDevice::Callbacks& cb)
    {
        device = adapter.connect(adapter.state.getChildWithProperty(ID::address, address), cb);

        return device.state;
    }

    void disconnect()
    {
        if (device.state.getProperty(ID::is_connected))
            adapter.disconnect(device);
    }

    void write(const juce::Uuid& uuid, gsl::span<const gsl::byte> data, bool withResponse = true)
    {
        device.write(adapter, uuid, data, withResponse);
    }

    [[nodiscard]] const juce::ValueTree& state() const { return device.state; }
    juce::ValueTree& state() { return device.state; }

    BleAdapter& adapter;

    const juce::String address;
    BleDevice          device;
};

} // namespace genki
