#pragma once

#include <cstdint>
#include <gsl/span>
#include <type_traits>

namespace genki {

//======================================================================================================================
template<typename Func, typename... Items>
constexpr void for_each(Func&& func, Items&& ... items)
noexcept(noexcept(std::initializer_list<int>{(func(std::forward<Items>(items)), 0)...}))
{
    (void) std::initializer_list<int>{((void) func(std::forward<Items>(items)), 0)...};
}

//======================================================================================================================
template<size_t size, size_t... szs>
constexpr auto split(gsl::span<const gsl::byte> s)
{
    if constexpr (sizeof...(szs) > 0)
    {
        return std::tuple_cat(std::make_tuple(s.first<size>()), split<szs...>(s.subspan<size>()));
    }
    else
    {
        return std::make_tuple(s.first<size>(), s.subspan<size>());
    }
}

template<typename T, size_t Extent = gsl::dynamic_extent>
T copy(gsl::span<const gsl::byte, Extent> s)
{
    // TODO: If we want to be pedantic, we should use std::is_trivially_copyable here, but we are using some standard
    //       library containers and Eigen vectors in our structs, which are not trivially copyable.
    static_assert(std::is_standard_layout_v<T>);

    assert(sizeof(T) == s.size());

    T t;
    std::memcpy(&t, s.data(), sizeof(t));
    return t;
}

//======================================================================================================================
constexpr size_t byte_size() { return 0; }

template<typename T, typename... Ts>
constexpr size_t byte_size(const T& t, const Ts& ... ts)
{
    if constexpr (std::is_standard_layout<T>::value)
    {
        return sizeof(t) + byte_size(ts...);
    }
    else
    {
        return (size_t) t.size() + byte_size(ts...);
    }
}

constexpr auto pack(gsl::span<gsl::byte> s) { return s; }

template<typename T, typename... Ts>
constexpr auto pack(gsl::span<gsl::byte> dest, const T& t, const Ts& ... ts)
{
    if constexpr (std::is_standard_layout<T>::value)
    {
        const auto s = gsl::as_bytes(gsl::make_span(&t, 1));

        assert(dest.size() >= s.size());
        std::copy(s.begin(), s.end(), dest.begin());

        assert(s.size() > 0);

        return pack(dest.subspan(s.size()), ts...);
    }
    else
    {
        // NOTE: This assumes T is a span type
        const auto s = gsl::as_bytes(t);
        std::copy(s.begin(), s.end(), dest.begin());

        return pack(dest.subspan(s.size()), ts...);
    }
}

template<typename Buffer, typename... Ts>
Buffer& pack(Buffer& out_buffer, const Ts& ... ts)
{
    assert(out_buffer.empty());

    out_buffer.resize(byte_size(ts...));
    pack(gsl::make_span(out_buffer), ts...);

    return out_buffer;
}

//======================================================================================================================
constexpr auto unpack(gsl::span<const gsl::byte> s) { return std::make_tuple(s); }

template<typename T, typename... Ts>
constexpr auto unpack(gsl::span<const gsl::byte> s)
{
    if constexpr (std::is_standard_layout<T>::value)
    {
        const auto [left, right] = split<sizeof(T)>(s);
        const auto current       = copy<T>(left);

        if constexpr (sizeof...(Ts) > 0)
        {
            return std::tuple_cat(std::make_tuple(current), unpack<Ts...>(right));
        }
        else
        {
            return std::tuple_cat(std::make_tuple(current), unpack(right));
        }
    }
}

} // namespace genki

namespace gsl {
    template<typename It>
    auto make_span(It begin, It end)
    {
        static_assert(std::is_same_v<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>);

        return gsl::make_span(&(*begin), static_cast<size_t>(std::distance(begin, end)));
    }
}