#pragma once

#include <napi.h>

class PacketHandler : public Napi::ObjectWrap<PacketHandler> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  PacketHandler(const Napi::CallbackInfo& info);

 private:
  void PushBytes(const Napi::CallbackInfo& info);
};