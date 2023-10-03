#include "packet_handler.h"

Napi::Object PacketHandler::Init(Napi::Env env, Napi::Object exports) {
  Napi::Function func =
      DefineClass(env,
                  "PacketHandler", {
                    InstanceMethod("pushBytes", &PacketHandler::PushBytes)
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
