set(target "genki-wave")
set(headers "${target}-headers")

add_library(${headers} INTERFACE)
add_library(${target} INTERFACE)

target_include_directories(${headers}
        INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${sml_source_dir}/include # See target_link_libraries below
        )

target_link_libraries(${headers}
        INTERFACE
        etl
        fmt
        GSL
        range-v3
        sml
        )

if (GENKI_WAVE_ENABLE_JUCE_TARGETS)
    target_link_libraries(${target}
            INTERFACE
            ${headers}
            genki::bluetooth
            )
endif ()
