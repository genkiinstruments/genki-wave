#include <napi.h>
#include "packet_handler.h"

Napi::Object InitAll(Napi::Env env, Napi::Object exports) {
  return PacketHandler::Init(env, exports);
}

NODE_API_MODULE(addon, InitAll)