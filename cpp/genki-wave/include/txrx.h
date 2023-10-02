#pragma once

#include <etl/deque.h>

#include "sml_wrapper.h"
#include "utility.h"

namespace genki {

template<typename T, size_t tx_size, size_t rx_size = tx_size>
struct TxRx
{
    etl::deque<T, tx_size> tx;
    etl::deque<T, rx_size> rx;
};

template<typename Transport, size_t TxBufferSize, size_t RxBufferSize, size_t PacketQueueSize>
struct TransportState
{
    TransportState(Transport& t, size_t packetSize) : transport(t), mtu(packetSize) {}

    Transport& transport;

    const size_t mtu{};

    etl::deque<uint8_t, PacketQueueSize>              tx_bytes{};
    TxRx<gsl::byte, TxBufferSize, RxBufferSize> buffer{};
};

namespace fsm {
namespace events {
struct transmit {};
struct tx_failed {};
struct tx_done { const size_t count{}; };
struct unknown {};
struct reset {};
} // namespace events

namespace txrx {
// States
class idle;
class tx;
class tx_waiting;

template<typename State, size_t MaxPacketSize>
struct fsm
{
    auto operator()() const noexcept
    {
        namespace sml = boost::sml;
        using namespace boost::sml;
        using namespace events;

        const auto transmit_packet = [](State& st, sml::back::process<transmit, tx_failed> proc)
        {
            static std::array<gsl::byte, MaxPacketSize> packet_buf{};

            auto& [transport, mtu, tx_bytes, buffer] = st;

            const auto cur_num_tx_bytes    = std::accumulate(tx_bytes.cbegin(), tx_bytes.cend(), 0u);
            const auto tx_begin            = buffer.tx.begin() + cur_num_tx_bytes;
            const auto num_bytes_remaining = static_cast<size_t>(std::distance(tx_begin, buffer.tx.end()));

            const auto packet_size = std::min(num_bytes_remaining, mtu);
            const auto packet_end  = std::copy(tx_begin, tx_begin + static_cast<int>(packet_size), packet_buf.begin());
            const auto packet      = gsl::as_bytes(gsl::make_span(packet_buf.begin(), packet_end));

            const bool is_async = tx_bytes.capacity() > 0;

            const bool can_tx = !is_async || !tx_bytes.full();

            if (can_tx && transport.transmitPacket(packet))
            {
                if (is_async)
                    tx_bytes.push_back(static_cast<uint8_t>(packet_size));
                else
                    buffer.tx.erase(buffer.tx.begin(), buffer.tx.begin() + static_cast<int>(packet_size));

                proc(transmit{});
            }
            else
            {
                proc(tx_failed{});
            }
        };

        const auto handle_tx_done = [](const tx_done& d, State& s)
        {
            auto& [transport, mtu, tx_bytes, buffer] = s;

            assert(tx_bytes.size() >= d.count);

            const auto num_bytes = std::accumulate(tx_bytes.cbegin(), tx_bytes.cbegin() + static_cast<long>(d.count), 0);
            tx_bytes.erase(tx_bytes.begin(), tx_bytes.begin() + static_cast<long>(d.count));

            assert(buffer.tx.size() >= static_cast<size_t>(num_bytes));
            buffer.tx.erase(buffer.tx.begin(), buffer.tx.begin() + num_bytes);
        };

        const auto is_last_packet = [](const tx_done& d, const State& s)
        {
            auto& [transport, mtu, tx_bytes, buffer] = s;

            assert(tx_bytes.size() >= d.count);

            const auto num_bytes = std::accumulate(tx_bytes.cbegin(), tx_bytes.cbegin() + static_cast<long>(d.count), 0u);

            return num_bytes == buffer.tx.size();
        };

        const auto has_bytes_to_tx = [](const State& s)
        {
            const auto& [transport, mtu, tx_bytes, buffer] = s;

            return buffer.tx.size() - std::accumulate(tx_bytes.cbegin(), tx_bytes.cend(), 0u) > 0;
        };

        const auto has_unconfirmed_packets = [](const State& s) { return !s.tx_bytes.empty(); };

        const auto reset_state = [](State& s)
        {
            genki::for_each([](auto& e) { e.clear(); }, s.tx_bytes, s.buffer.rx, s.buffer.tx);
        };

        const auto is_async     = [](const State& s) { return s.tx_bytes.capacity() > 0; };
        const auto is_not_async = [is_async](const State& s) { return !is_async(s); };

        //==============================================================================================================
        return make_transition_table(
                *state<idle> + event<transmit> / transmit_packet = state<tx>,

                state<tx> + event<tx_failed> = state<tx_waiting>,
                state<tx> + event<transmit>[has_bytes_to_tx] / transmit_packet,
                state<tx> + event<tx_done>[is_last_packet] / handle_tx_done = state<idle>,
                state<tx> + event<tx_done>[has_unconfirmed_packets] / handle_tx_done,
                state<tx> + event<tx_done> / (handle_tx_done, transmit_packet),
                state<tx> + event<reset> / reset_state = state<idle>,

                state<tx_waiting> + event<transmit>[is_not_async] / transmit_packet    = state<tx>,
                state<tx_waiting> + event<tx_done> / (handle_tx_done, transmit_packet) = state<tx>,
                state<tx_waiting> + event<unknown>[has_bytes_to_tx] / transmit_packet  = state<tx>,
                state<tx_waiting> + event<reset> / reset_state                         = state<idle>
        );
    }
};

} // namespace transport
} // namespace fsm
} // namespace genki
