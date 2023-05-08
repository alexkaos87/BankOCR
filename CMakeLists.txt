cmake_minimum_required(VERSION 3.16.0 FATAL_ERROR)

set(CMAKE_SYSTEM_VERSION 8.1 CACHE STRING "" FORCE)

set(PROJ_NAME "BankOCR")
set(PROJ_TEST "BankOCRTests")
project(${PROJ_NAME} CXX)

add_library(${PROJ_NAME} STATIC BankOCR/OCR.cpp)
add_executable(${PROJ_TEST} Tests/OCRTest.cpp Tests/runner.cpp)

set(HEADERS_FILE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/BankOCR)
target_include_directories(${PROJ_NAME} PUBLIC ${HEADERS_FILE_DIRS})
target_include_directories(${PROJ_TEST} PUBLIC ${HEADERS_FILE_DIRS})
target_link_libraries(${PROJ_TEST} ${PROJ_NAME})

set (CMAKE_CXX_STANDARD 17)
add_definitions(-Wall -Werror -Wunused -Wextra)

# Locate GTest
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})
 
# Link BankOCRTests with what we want to test and the GTest and pthread library
target_link_libraries(${PROJ_TEST} ${GTEST_LIBRARIES})
