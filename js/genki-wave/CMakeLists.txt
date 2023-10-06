cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0091 NEW)
cmake_policy(SET CMP0042 NEW)

project (packethandler)

if (APPLE)
    set(CMAKE_OSX_ARCHITECTURES "x86_64;arm64" CACHE STRING "macOS architecture" FORCE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "macOS target" FORCE)
elseif(WIN32)
    set(CMAKE_SYSTEM_VERSION "10.0.22000.0" CACHE STRING "Windows version" FORCE)
endif()

set(GENKI_WAVE_BUILD_EXAMPLES OFF)
set(GENKI_WAVE_ENABLE_TESTING OFF)
set(GENKI_WAVE_ENABLE_JUCE_TARGETS OFF)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../cpp ${CMAKE_CURRENT_BINARY_DIR}/genki-wave)

# Add Node bindings.
execute_process(COMMAND node -p "require('node-addon-api').include_dir"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    OUTPUT_VARIABLE NODE_ADDON_API_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

add_library(${PROJECT_NAME} SHARED
    lib/addon.cpp
    lib/packet_handler.cpp
    lib/packet_handler.h
    ${CMAKE_JS_SRC}
)

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/lib
    ${CMAKE_JS_INC}
    ${NODE_ADDON_API_DIR}
)

target_link_libraries(${PROJECT_NAME} PRIVATE genki-wave-headers ${CMAKE_JS_LIB})
target_compile_definitions(${PROJECT_NAME} PRIVATE NAPI_VERSION=6)
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_NAME "${PROJECT_NAME}"
    CXX_STANDARD 17
    PREFIX ""
    SUFFIX ".node"
)

if (MSVC AND CMAKE_JS_NODELIB_DEF AND CMAKE_JS_NODELIB_TARGET)
    # Generate node.lib
    execute_process(COMMAND ${CMAKE_AR} /def:${CMAKE_JS_NODELIB_DEF} /out:${CMAKE_JS_NODELIB_TARGET} ${CMAKE_STATIC_LINKER_FLAGS})
endif()
