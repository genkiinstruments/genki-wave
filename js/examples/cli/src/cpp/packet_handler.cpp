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

PacketHandler::PacketHandler(const Napi::CallbackInfo& info) : Napi::ObjectWrap<PacketHandler>(info) { }

void PacketHandler::PushBytes(const Napi::CallbackInfo& info) {
    if (info.Length() == 1 && info[0].IsArrayBuffer())
    {
        Napi::ArrayBuffer buf = info[0].As<Napi::ArrayBuffer>();

        std::vector<uint8_t> v(buf.ByteLength());
        std::memcpy(v.data(), buf.Data(), buf.ByteLength());

        for (const auto& b : v)
            std::printf("%02x ", b);

        std::printf("\n");

        // TODO: Do something with bytes here...
    }
}
