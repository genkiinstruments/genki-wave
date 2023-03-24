# For more information about using CMake with Android Studio, read the
# documentation: https://d.android.com/studio/projects/add-native-code.html
cmake_minimum_required(VERSION 3.18.1)

set(CMAKE_CXX_STANDARD 17)

project(genkiwave VERSION 0.1.0)

set(genki_wave_root "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../..")
message("CMAKE_CURRENT_SOURCE_DIR: ${CMAKE_CURRENT_SOURCE_DIR}")
include(${genki_wave_root}/cpp/cmake/fetch_from_git.cmake)

include(cmake/fetch_from_git.cmake)

fetch_from_git(gsl https://github.com/microsoft/GSL.git GIT_TAG main)
fetch_from_git(etl https://github.com/ETLCPP/etl.git)
fetch_from_git(fmt https://github.com/fmtlib/fmt.git)
fetch_from_git(sml https://github.com/boost-ext/sml.git SOURCE_DIRECTORY_VAR sml_source_dir)

#find_library(log-lib log)

add_library(${CMAKE_PROJECT_NAME} SHARED
        lib.cpp
        )

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
        ${genki_wave_root}/cpp/genki-wave/include
        ${sml_source_dir}/include
        )

target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE
#        ${log-lib}
        etl
        fmt
        GSL
        )