#include "packet_handler.h"
#include "fmt/ranges.h"

Napi::Object PacketHandler::Init(Napi::Env env, Napi::Object exports) {
  Napi::Function func =
      DefineClass(env,
                  "PacketHandler", {
                    InstanceMethod("pushBytes", &PacketHandler::PushBytes),
                    InstanceMethod("sendQuery", &PacketHandler::SendQuery)
                   });

  Napi::FunctionReference* constructor = new Napi::FunctionReference();
  *constructor = Napi::Persistent(func);
  env.SetInstanceData(constructor);

  exports.Set("PacketHandler", func);
  return exports;
}

void PacketHandler::PushBytes(const Napi::CallbackInfo& info) {
    if (info.Length() == 1 && info[0].IsArrayBuffer())
    {
        Napi::ArrayBuffer buf = info[0].As<Napi::ArrayBuffer>();

        std::vector<uint8_t> v(buf.ByteLength());
        std::memcpy(v.data(), buf.Data(), buf.ByteLength());

        const auto s = gsl::as_bytes(gsl::span(reinterpret_cast<const uint8_t*>(buf.Data()), buf.ByteLength()));

        codec.receivePacket(s);
    }
}

void PacketHandler::SendQuery(const Napi::CallbackInfo& info) {
    if (info.Length() > 0 && info[0].IsObject())
    {
        const auto type_from_str = [](const std::string& str)
        {
            using Type = genki::Wave::Api::Query::Type;

            return str == "request" ? Type::Request :
                   str == "response" ? Type::Response :
                   str == "stream" ? Type::Stream : Type::MAX_VAL;
        };

        const auto jq = info[0].As<Napi::Object>();

        const genki::Wave::Api::Query query {
            .type = genki::Wave::Api::Query::Type(static_cast<uint8_t>(static_cast<int>(jq.Get("type").ToNumber()))),
            .id = genki::Wave::Api::Query::Id(static_cast<uint8_t>(static_cast<int>(jq.Get("id").ToNumber()))),
            .payload_size = static_cast<uint16_t>(static_cast<int>(jq.Get("payload_size").ToNumber())),
        };

        if (info.Length() > 1 && info[1].IsArrayBuffer())
        {
            Napi::ArrayBuffer buf = info[1].As<Napi::ArrayBuffer>();
            const auto payload = gsl::as_bytes(gsl::span(reinterpret_cast<const uint8_t*>(buf.Data()), buf.ByteLength()));

            genki::send_query(*this, query, payload);
        }

        genki::send_query(*this, query);
    }
}
