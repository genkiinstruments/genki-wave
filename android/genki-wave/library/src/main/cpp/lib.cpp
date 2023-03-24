#if __ANDROID__
#include <jni.h>

#include "cobs_codec.h"
#include "native_array.h"
#include "requests.h"
#include "utility.h"

#define JNI_IMPL(ret, func) extern "C" JNIEXPORT ret JNICALL Java_com_genki_wave_PacketHandler_##func

struct PacketHandler {
    using CallbackType = std::function<void(gsl::span<const gsl::byte>)>;

    PacketHandler(JNIEnv* env, jobject obj, size_t packetSize = 20)
            : transport(*this,
                        [this](gsl::span<const gsl::byte> bytes)
            {
                const auto [query, payload] = genki::unpack<genki::Wave::Api::Query>(bytes);

                auto [jnienv, jniobj] = get_jni_ctx();

                jclass self_class = jnienv->GetObjectClass(jniobj);
                jmethodID handleQuery = jnienv->GetMethodID(self_class, "handleQuery", "(I[B)V");

                jbyteArray jbytes = jnienv->NewByteArray(static_cast<jsize>(payload.size()));
                jnienv->SetByteArrayRegion(jbytes, 0, static_cast<jsize>(payload.size()), reinterpret_cast<const jbyte*>(payload.data()));
                jnienv->CallVoidMethod(jniobj, handleQuery, (int) query.id, jbytes);
            }),
              codec(transport, packetSize),
              jobj(env->NewGlobalRef(obj)),
              javavm([&] { JavaVM* vm{}; env->GetJavaVM(&vm); return vm; }())
    {
    }

    auto get_jni_ctx() -> std::pair<JNIEnv*, jobject>
    {
        JNIEnv* env = nullptr;
        javavm->AttachCurrentThread(&env, nullptr);

        return {env, jobj};;
    }

    ~PacketHandler()
    {
        auto [env, obj] = get_jni_ctx();

        if (env != nullptr)
            env->DeleteGlobalRef(obj);
    }

    //==================================================================================================================
    // Queue transmission of an arbitrarily sized payload, which might or might not fit in a single BLE packet.
    bool encodeAndTransmit(const std::vector<gsl::byte>& data)
    {
        return codec.encodeAndTransmit(gsl::make_span(data), false);
    }

    void onCharacteristicWritten(bool success) { success ? codec.onTxComplete() : codec.maybeRetryTx(); }

    void onValueChanged(gsl::span<const gsl::byte> data) { codec.receivePacket(data); }

    //==================================================================================================================
    struct Transport {
        Transport(PacketHandler& hndlr, CallbackType cb)
                : handler(hndlr),
                  onPacketReceived(std::move(cb))
        {

        }

        bool transmitPacket(gsl::span<const gsl::byte> data) {
            auto [env, obj] = handler.get_jni_ctx();

            jclass clazz = env->GetObjectClass(obj);
            jmethodID write_method = env->GetMethodID(clazz, "writePacket", "([B)V");

            jbyteArray jbytes = env->NewByteArray(static_cast<jsize>(data.size()));
            env->SetByteArrayRegion(jbytes, 0, static_cast<jsize>(data.size()), reinterpret_cast<const jbyte*>(data.data()));
            env->CallVoidMethod(obj, write_method, jbytes);

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

    Transport transport;
    genki::CobsCodec<Transport> codec;

    JavaVM* javavm;
    jobject jobj;
};

PacketHandler& getHandler(JNIEnv* env, jobject jself, jlong nativeHandle)
{
    return *reinterpret_cast<PacketHandler*>(nativeHandle);
}


JNI_IMPL(long, ConstructNative)(JNIEnv* env, jobject self, jlong packetSize) {
    return reinterpret_cast<long>(new PacketHandler(env, self, packetSize));
}

JNI_IMPL(void, CleanupNative)(JNIEnv* env, jobject self, jlong jhandle) {
    delete reinterpret_cast<PacketHandler*>(jhandle);
}

JNI_IMPL(void, PushBytesNative)(JNIEnv* env, jobject self, jlong nativeHandle, jbyteArray jdata) {
    const auto native_data = NativeByteArray{ env, jdata };

    auto& handler = getHandler(env, self, nativeHandle);
    handler.onValueChanged(native_data.data);
}

JNI_IMPL(bool, SendQueryNative)(JNIEnv* env, jobject self, jlong nativeHandle, jobject jquery, jbyteArray jpayload) {
    const jclass clazz = env->GetObjectClass(jquery);

    const jfieldID qtype_id = env->GetFieldID(clazz, "type", "B");
    const jbyte jqtype = env->GetByteField(jquery, qtype_id);

    const jfieldID qid_id = env->GetFieldID(clazz, "id", "B");
    const jbyte jqid = env->GetByteField(jquery, qid_id);

    const jfieldID qsize_id = env->GetFieldID(clazz, "payloadSize", "S");
    const jshort jqsz = env->GetShortField(jquery, qsize_id);

    const auto native_payload = NativeByteArray{ env, jpayload };

    using Q = genki::Wave::Api::Query;
    const Q query{
        .type = Q::Type(jqtype),
        .id = Q::Id(jqid),
        .payload_size = static_cast<uint16_t>(jqsz),
    };

    assert(query.payload_size == native_payload.data.size());

    auto& handler = getHandler(env, self, nativeHandle);

    return genki::send_query(handler, query);
}

JNI_IMPL(void, OnWriteCompleteNative)(JNIEnv* env, jobject self, jlong nativeHandle, jboolean jsuccess) {
    auto& handler = getHandler(env, self, nativeHandle);
    handler.onCharacteristicWritten(static_cast<bool>(jsuccess));
}

#endif // __ANDROID__