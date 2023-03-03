#pragma once

#include <gsl/span>
#include <vector>

#include "wave_public_types.h"

namespace genki {
template<typename Comm, typename Q, typename... Args>
[[maybe_unused]] bool send_query(Comm& comm, const Q& query, const Args& ... args)
{
    const auto sz = byte_size(query, args...);
    jassert(query.payload_size == sz - sizeof(query));

    std::vector<gsl::byte> buf{};
    buf.reserve(sz);

    return comm.encodeAndTransmit(std::move(pack(buf, query, args...)));
}

template<typename Comm, typename... Args, typename Q = Wave::Api::Query>
[[maybe_unused]] bool request(Comm& comm, typename Q::Id qid, const Args& ... args)
{
    return send_query(comm, Q{Q::Type::Request, qid, static_cast<uint16_t>(byte_size(args...))}, args...);
}

} // namespace genki
