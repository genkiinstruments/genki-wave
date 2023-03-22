set(target "genki-wave")
add_library(${target} INTERFACE)

target_include_directories(${target}
        INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${sml_source_dir}/include # See target_link_libraries below
        )

target_link_libraries(${target}
        INTERFACE
        genki::bluetooth

        etl
        fmt
        GSL
        range-v3

#        NOTE: linking with sml forces warnings to be treated as errors for the whole project, which isn't always what we want
#        sml
        )

