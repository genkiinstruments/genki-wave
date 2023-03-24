#pragma once

#if __ANDROID__

#include <jni.h>
#include <gsl/span>
#include <gsl/byte>
#include <string>

template <class T>
struct JniArrayAssociations{};

template <>
struct JniArrayAssociations<gsl::byte>
{
    using JniType = jbyte;
    using JniArrayType = jbyteArray;

    static JniType* GetArrayElements(JNIEnv* env, JniArrayType arr, jboolean* isCopy)
    {
        return env->GetByteArrayElements(arr, isCopy);
    }

    static void ReleaseArrayElements(JNIEnv* env, JniArrayType arr, JniType* elements)
    {
        env->ReleaseByteArrayElements(arr, elements, JNI_ABORT);
    }
};

template <>
struct JniArrayAssociations<float>
{
    using JniType = jfloat;
    using JniArrayType = jfloatArray;

    static JniType* GetArrayElements(JNIEnv* env, JniArrayType arr, jboolean* isCopy)
    {
        return env->GetFloatArrayElements(arr, isCopy);
    }

    static void ReleaseArrayElements(JNIEnv* env, JniArrayType arr, JniType* elements)
    {
        env->ReleaseFloatArrayElements(arr, elements, JNI_ABORT);
    }
};

template <class T>
class NativeArray
{
private:
    using Assoc = JniArrayAssociations<T>;
    using ArrayType = typename Assoc::JniArrayType;
    using ElementType = typename Assoc::JniType;

    JNIEnv* javaEnv;
    ArrayType javaArray;
    jboolean isCopy{};
    ElementType* elements;

public:
    gsl::span<const T> data;

    NativeArray(JNIEnv* env, ArrayType arr)
        : javaEnv{ env }
        , javaArray{ arr }
        , elements{ Assoc::GetArrayElements(env, arr, &isCopy) }
        , data{
            reinterpret_cast<const T*>(elements), static_cast<size_t>(env->GetArrayLength(arr))
        }
    {
    }

    NativeArray(const NativeArray&) = delete;
    NativeArray(NativeArray&&) = delete;

    ~NativeArray()
    {
        Assoc::ReleaseArrayElements(javaEnv, javaArray, elements);
    }
};

using NativeByteArray = NativeArray<gsl::byte>;
using NativeFloatArray = NativeArray<float>;

std::string to_string(const NativeByteArray& nativeArray) {
    static_assert(sizeof(gsl::byte) == sizeof(char));
    return { reinterpret_cast<const char*>(nativeArray.data.data()),
             reinterpret_cast<const char*>(nativeArray.data.data() + nativeArray.data.size()) };
}

#endif
