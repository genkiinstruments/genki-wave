#pragma once

#include <utility>

#include "ble_packetizer.h"
#include "ble_transport.h"
#include "cobs_codec.h"
#include "format.h"
#include "utility.h"
#include "wave_public_types.h"
#include "requests.h"

namespace genki {

namespace util {
constexpr auto get_service = [](const juce::ValueTree& vt, const juce::Uuid& uuid)
{
    jassert(vt.hasType(ID::BLUETOOTH_DEVICE));

    auto srv = vt.getChildWithProperty(ID::uuid, uuid.toDashedString());
    jassert(srv.hasType(ID::SERVICE));

    return srv;
};
} // namespace util

struct WaveApiDevice : private juce::ValueTree::Listener
{
    //==================================================================================================================
    using QueryCallback = std::function<void(const Wave::Api::Query&, gsl::span<const gsl::byte>)>;

    //==================================================================================================================
    static constexpr std::string_view GenkiServiceUuidString = "65e9296c-8dfb-11ea-bc55-0242ac130003";
    static constexpr std::string_view ApiCharactUuidString   = "65e92bb1-8dfb-11ea-bc55-0242ac130003";

    //==================================================================================================================
    WaveApiDevice(std::unique_ptr<BleTransport> trans, QueryCallback qcb)
            : transport(std::move(trans)),
              query_callback(std::move(qcb))
    {
        const auto dev = transport->connect(ble_callbacks);

        transport->state().addListener(this);
    }


    //======================================================================================================================
    template<typename... Args>
    bool send(const Wave::Api::Query& query, const Args& ... args) const
    {
        return send_query(*ble_packetizer, query, args...);
    }

    template<typename... Args, typename Q = Wave::Api::Query>
    [[maybe_unused]] bool request(typename Q::Id qid, const Args& ... args) const
    {
        jassert(ble_packetizer != nullptr);

        return genki::request(*ble_packetizer, qid, args...);
    }

    bool request_info() const { return request(Wave::Api::Query::Id::DeviceInfo); }
    bool read_battery() const { return request(Wave::Api::Query::Id::BatteryStatus); }
    bool recenter() const { return request(Wave::Api::Query::Id::Recenter); }
    bool update_display(const Wave::LedFrame& frame) const { return request(Wave::Api::Query::Id::DisplayFrame, frame); }

private:
    //==================================================================================================================
    void valueTreePropertyChanged(juce::ValueTree& vt, const juce::Identifier& id) override
    {
        if (transport != nullptr && vt == transport->state())
        {
            if (id == ID::is_connected)
            {
                message(vt, ID::DISCOVER_SERVICES);
            }
            else if (id == ID::max_pdu_size)
            {
                const auto max_pdu = static_cast<size_t>((int) vt.getProperty(id));

                ble_packetizer = std::make_unique<BlePacketizer<BleTransport, Codec>>
                        (
                                *transport,
                                juce::Uuid(ApiCharactUuidString.data()),
                                [this](auto d) { handleIncomingPacket(d); }, max_pdu);
            }
        }
    }

    void valueTreeChildAdded(juce::ValueTree&, juce::ValueTree& child) override
    {
        if (transport != nullptr && child.isAChildOf(transport->state()))
        {
            if (child.hasType(ID::CHARACTERISTIC))
            {
                if (child.getProperty(ID::uuid))
                {
                    message(child, ID::ENABLE_NOTIFICATIONS);
                }
            }
            else if (child.hasType(ID::SERVICES_DISCOVERED))
            {
                if (const auto s = util::get_service(transport->state(), juce::Uuid(GenkiServiceUuidString.data())); s.isValid())
                {
                    message(s, ID::DISCOVER_CHARACTERISTICS);
                }
            }
        }
    }

    //==================================================================================================================
    void handleIncomingPacket(gsl::span<const gsl::byte> packet)
    {
        const auto [query, s_query] = genki::unpack<Wave::Api::Query>(packet);

        jassert(query.payload_size == s_query.size());

        if (query_callback)
            query_callback(query, s_query);
    }

    //==================================================================================================================
    std::unique_ptr<BleTransport> transport;

    //==================================================================================================================
    const BleDevice::Callbacks ble_callbacks{
            .valueChanged = [this](const juce::Uuid& uuid, gsl::span<const gsl::byte> data)
            {
                if (ble_packetizer != nullptr && uuid == ble_packetizer->transport.charactUuid)
                    ble_packetizer->onValueChanged(data);
            },
            .characteristicWritten = [this](const juce::Uuid& uuid, bool success)
            {
                if (ble_packetizer != nullptr && uuid == ble_packetizer->transport.charactUuid)
                    ble_packetizer->onCharacteristicWritten(success);
            },
    };

    const QueryCallback query_callback;

    //==================================================================================================================
    // The BlePacketizer expects a single-parameter template
    template<typename T>
    using Codec = CobsCodec<T>;

    std::unique_ptr<BlePacketizer<BleTransport, Codec>> ble_packetizer;
};

} // namespace genki