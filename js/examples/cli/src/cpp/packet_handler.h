#pragma once

#include <napi.h>

#include "cobs_codec.h"
#include "requests.h"
#include "utility.h"
#include "fmt/format.h"

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
                      fmt::print("Corrupt packet, expected at least {} bytes for query, got: {}\n", sizeof(genki::Wave::Api::Query), bytes.size());
                      return;
                  }

                  const auto [query, payload] = genki::unpack<genki::Wave::Api::Query>(bytes);

                  if (payload.size() != query.payload_size)
                  {
                      fmt::print("Corrupt payload, expected {} bytes, got: {}\n", query.payload_size, payload.size());
                      return;
                  }

                  [[maybe_unused]] const auto query_to_js = [&](const genki::Wave::Api::Query& q)
                  {
                      Napi::Object jq = Napi::Object::New(env);
                      jq.Set("type", (int) q.type);
                      jq.Set("id", (int) q.id);
                      jq.Set("payloadSize", (int) q.payload_size);

                      return jq;
                  };

                  using ID = genki::Wave::Api::Query::Id;

                  if (query.id == ID::ButtonEvent)
                  {
                      const auto button_to_js = [&](const genki::Wave::ButtonEvent& btn)
                      {
                          constexpr auto actions = std::array{ "up", "down", "long", "longup", "extralong", "extralongup", "click", "doubleclick" };

                          Napi::Object jb = Napi::Object::New(env);
                          jb.Set("id", (int) btn.id);
                          jb.Set("action", std::string(actions[(size_t) btn.action]));
                          jb.Set("timestamp", btn.timestamp);

                          return jb;
                      };

                    emit.Call({Napi::String::New(env, "button"), button_to_js(genki::copy<genki::Wave::ButtonEvent>(payload))});
                  }
                  else if (query.id == ID::BatteryStatus)
                  {
                      const auto battery_to_js = [&](const genki::Wave::BatteryStatus& bs)
                      {
                          Napi::Object jb = Napi::Object::New(env);
                          jb.Set("voltage", bs.voltage);
                          jb.Set("percentage", bs.percentage);
                          jb.Set("isCharging", bs.is_charging);

                          return jb;
                      };

                    emit.Call({Napi::String::New(env, "battery"), battery_to_js(genki::copy<genki::Wave::BatteryStatus>(payload))});
                  }
                  else if (query.id == ID::Datastream)
                  {
                      const auto datastream_to_js = [&](const genki::Wave::Datastream& ds)
                      {
                          const auto convert_3d = [&](const auto& d)
                          {
                              const auto [x, y, z] = d;

                              Napi::Object obj = Napi::Object::New(env);
                              obj.Set("x", x);
                              obj.Set("y", y);
                              obj.Set("z", z);

                              return obj;
                          };

                          const auto convert_4d = [&](const auto& q)
                          {
                              const auto [w, x, y, z] = q;

                              Napi::Object obj = Napi::Object::New(env);
                              obj.Set("w", w);
                              obj.Set("x", x);
                              obj.Set("y", y);
                              obj.Set("z", z);

                              return obj;
                          };

                          Napi::Object datastream = Napi::Object::New(env);
                          Napi::Object sensor_data = Napi::Object::New(env);
                          Napi::Object motion_data = Napi::Object::New(env);
                          Napi::Object peak = Napi::Object::New(env);

                          sensor_data.Set("gyro", convert_3d(ds.data.gyro));
                          sensor_data.Set("accel", convert_3d(ds.data.accel));
                          sensor_data.Set("mag", convert_3d(ds.data.mag));

                          datastream.Set("data", sensor_data);

                          sensor_data.Set("rawPose", convert_4d(ds.motionData.rawPose));
                          sensor_data.Set("currentPose", convert_4d(ds.motionData.currentPose));
                          sensor_data.Set("euler", convert_3d(ds.motionData.euler));
                          sensor_data.Set("linearAccel", convert_3d(ds.motionData.linearAccel));

                          peak.Set("detected", ds.motionData.tap.detected);
                          peak.Set("normVelocity", ds.motionData.tap.normVelocity);
                          sensor_data.Set("peak", peak);

                          datastream.Set("motionData", motion_data);

                          datastream.Set("timestampUs", ds.timestamp_us);

                          return datastream;
                      };

                      const auto& ds = genki::copy<genki::Wave::Datastream>(payload);

                      emit.Call({Napi::String::New(env, "data"), datastream_to_js(ds)});
                  }
              }),
                codec(transport, 20), // TODO: Need to know MTU
                env(info.Env()),
                emit(Napi::Persistent(info[0].As<Napi::Function>()))
   {
   }

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

  Napi::Env env;
  Napi::FunctionReference emit;

};
