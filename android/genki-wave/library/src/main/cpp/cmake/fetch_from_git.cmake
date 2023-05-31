function(fetch_from_git target git_repository)
    set(single_value_args GIT_REPOSITORY GIT_TAG URL SOURCE_DIRECTORY_VAR BINARY_DIRECTORY_VAR)
    cmake_parse_arguments(PARSED_ARGS "${flag_args}" "${single_value_args}" "" ${ARGN})

    string(TOLOWER ${target} lowercase_target)

    include(FetchContent)

    message("Fetching ${git_repository} ${PARSED_ARGS_GIT_TAG}")

    FetchContent_Declare(${target}
            GIT_REPOSITORY ${git_repository}
            GIT_TAG ${PARSED_ARGS_GIT_TAG}
            GIT_PROGRESS TRUE
            )

    FetchContent_GetProperties(${target})
    if (NOT ${lowercase_target}_POPULATED)
        FetchContent_MakeAvailable(${target})

        set(TARGET_SOURCE_DIR "${${lowercase_target}_SOURCE_DIR}")

        get_filename_component(compiler ${CMAKE_CXX_COMPILER} NAME)
        set(TARGET_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/${lowercase_target}-build/${compiler}/${CMAKE_BUILD_TYPE}")

        if (DEFINED PARSED_ARGS_SOURCE_DIRECTORY_VAR)
            set(${PARSED_ARGS_SOURCE_DIRECTORY_VAR} ${TARGET_SOURCE_DIR} PARENT_SCOPE)
        endif ()

        if (DEFINED PARSED_ARGS_BINARY_DIRECTORY_VAR)
            set(${PARSED_ARGS_BINARY_DIRECTORY_VAR} ${TARGET_BINARY_DIR} PARENT_SCOPE)
        endif ()
    endif ()
endfunction()
