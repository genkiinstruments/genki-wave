#pragma once

#include <gsl/span>
#include <juce_data_structures/juce_data_structures.h>

namespace genki {

//======================================================================================================================
template<typename BleTransport, template<typename> typename Codec>
struct BlePacketizer
{
    using CallbackType = std::function<void(gsl::span<const gsl::byte>)>;

    BlePacketizer(BleTransport& t, const juce::Uuid& uuid, const CallbackType& cb, size_t packetSize = 20)
            : transport(t, uuid, cb),
              codec(transport, packetSize)
    {
        DBG("BlePacketizer using MTU: " << packetSize);
    }

    ~BlePacketizer() = default;

    //==================================================================================================================
    // Queue transmission of an arbitrarily sized payload, which might or might not fit in a single BLE packet.
    bool encodeAndTransmit(const std::vector<gsl::byte>& data)
    {
        const bool success = [&]
        {
            const juce::ScopedLock lock(txLock);

            return codec.encodeAndTransmit(gsl::make_span(data), true);
        }();

        codec.startTransfer();

        return success;
    }

    void onCharacteristicWritten(bool success)
    {
        const juce::ScopedLock lock(txLock);

        success ? codec.onTxComplete() : codec.maybeRetryTx();
    }

    void onValueChanged(gsl::span<const gsl::byte> data) { codec.receivePacket(data); }

    //==================================================================================================================
    struct Transport
    {
        Transport(BleTransport& t, const juce::Uuid& uuid, CallbackType cb)
                : charactUuid(uuid),
                  trans(t),
                  onPacketReceived(std::move(cb)) {}

        bool transmitPacket(gsl::span<const gsl::byte> data)
        {
            DBG("transmitPacket " << juce::String::toHexString(data.data(), static_cast<int>(data.size())));
            trans.write(charactUuid, data);

            return true;
        }

        template<typename Packet>
        void receiveMessage(const Packet& packet) const
        {
            if (onPacketReceived)
                onPacketReceived(gsl::as_bytes(gsl::make_span(packet)));
        }

        const juce::Uuid charactUuid;
        BleTransport& trans;
        CallbackType onPacketReceived;
    };

    Transport transport;

private:
    //==================================================================================================================
    juce::CriticalSection txLock;
    Codec<Transport>      codec;
};

} // namespace genki
