cmake_minimum_required(VERSION 3.5.0)
project(iqr-multivideo VERSION 0.1.0 LANGUAGES C CXX)

find_package(realsense2 REQUIRED)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

set(CMAKE_CXX_FLAGS_RELEASE "-O3")

include(CheckCXXCompilerFlag)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(iqr-multivideo main.cpp)

target_link_libraries( iqr-multivideo realsense2 )

install(
    TARGETS

    iqr-multivideo

    RUNTIME DESTINATION
    ${CMAKE_INSTALL_BINDIR}
)