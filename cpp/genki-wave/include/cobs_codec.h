#pragma once

#include <etl/queue.h>
#include <gsl/span>

#include "cobs.h"
#include "sml_wrapper.h"
#include "txrx.h"

namespace genki {

template <typename T>
using ProcessQueueFSM = etl::queue<T, 8>;

template<typename Transport, size_t MaxPacketSize = 256, size_t TxBufferSize = 512, size_t RxBufferSize = 512, size_t PacketQueueSize = 8>
struct CobsCodec
{
    CobsCodec(Transport& t, size_t packetSize) : state(t, packetSize), sm(state) {}

    bool encodeAndTransmit(gsl::span<const gsl::byte> data, bool hold_transfer = false)
    {
        if (cobs_encoded_size(data.size()) > state.buffer.tx.available())
            return false;

        std::array<gsl::byte, cobs_encoded_size(TxBufferSize)> encoded {};

        const auto encoded_end = cobs_encode(data.begin(), data.end(), encoded.begin());
        state.buffer.tx.insert(state.buffer.tx.end(), encoded.begin(), encoded_end);

        if (!hold_transfer)
            startTransfer();

        return true;
    }

    void startTransfer() { sm.process_event(fsm::events::transmit{}); }

    void onTxComplete(size_t count = 1) { sm.process_event(fsm::events::tx_done{count}); }

    void receivePacket(gsl::span<const gsl::byte> data)
    {
        auto& buffer = state.buffer;

        // If we don't have room for the packet, it's better to discard it and deal with a single corrupt message
        // rather than crashing the application...
        if (buffer.rx.size() + data.size() <= buffer.rx.capacity())
        {
            buffer.rx.insert(buffer.rx.end(), data.begin(), data.end());

            auto opt_p = find_cobs_packet(buffer.rx.cbegin(), buffer.rx.cend());

            while (opt_p.has_value())
            {
                const auto[start, end] = *opt_p;

                std::vector<gsl::byte> packet{};
                cobs_decode(start, end, std::back_inserter(packet));

                if (!packet.empty())
                    state.transport.receiveMessage(packet);

                buffer.rx.erase(start, end);

                opt_p = find_cobs_packet(buffer.rx.cbegin(), buffer.rx.cend());
            }
        }
    }

    void maybeRetryTx() { sm.process_event(fsm::events::unknown{}); }

    void reset()
    {
        sm.process_event(fsm::events::reset{});
        assert(sm.is(boost::sml::state<fsm::txrx::idle>));
    }

    //==================================================================================================================
    using State = TransportState<Transport, TxBufferSize, RxBufferSize, PacketQueueSize>;
    State state{};

    boost::sml::sm<fsm::txrx::fsm<State, MaxPacketSize>, boost::sml::process_queue<ProcessQueueFSM>> sm;
};

} // namespace genki
