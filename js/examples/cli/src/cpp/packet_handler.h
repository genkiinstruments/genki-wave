#pragma once

#include <napi.h>

#include "cobs_codec.h"
#include "requests.h"
#include "utility.h"
#include "fmt/ranges.h"

class PacketHandler : public Napi::ObjectWrap<PacketHandler> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);

  using CallbackType = std::function<void(gsl::span<const gsl::byte>)>;

  PacketHandler(const Napi::CallbackInfo& info)
   : Napi::ObjectWrap<PacketHandler>(info),
            transport(*this,
                      [this](gsl::span<const gsl::byte> bytes)
              {
                  if (bytes.size() < sizeof(genki::Wave::Api::Query))
                  {
                        fmt::print("Corrupt packet, expected at least {} bytes for query, got: {}\n",
                                                sizeof(genki::Wave::Api::Query),
                                                bytes.size());

                      return;
                  }

                  const auto [query, payload] = genki::unpack<genki::Wave::Api::Query>(bytes);

                  if (payload.size() != query.payload_size)
                  {
                        fmt::print("Corrupt payload, expected {} bytes, got: {}\n",
                                                query.payload_size,
                                                payload.size());

                      return;
                  }

                  // TODO: Call to js...
                  fmt::print("Query: {} {} {} {}\n", (int) query.type, (int) query.id, query.payload_size, payload);
              }),
                codec(transport, 20)
   {}

 private:
    struct Transport {
        Transport(PacketHandler& hndlr, CallbackType cb)
                : handler(hndlr),
                  onPacketReceived(std::move(cb))
        {

        }

        bool transmitPacket(gsl::span<const gsl::byte> data) {
            // TODO: Call to js
            return true;
        }

        template<typename Packet>
        void receiveMessage(const Packet &packet) const {
            if (onPacketReceived)
                onPacketReceived(gsl::as_bytes(gsl::make_span(packet)));
        }

        PacketHandler& handler;
        CallbackType onPacketReceived;
    };

  void PushBytes(const Napi::CallbackInfo& info);

  Transport transport;
  genki::CobsCodec<Transport> codec;
};
