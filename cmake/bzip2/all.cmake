cmake_minimum_required(VERSION 2.7)

project(bzip2 C)

SET(sources bzlib.h blocksort.c huffman.c crctable.c randtable.c compress.c decompress.c bzlib.c bzip2.c)
SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DWIN32 -MD -Ox -D_FILE_OFFSET_BITS=64 -nologo")

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_library(bz2 SHARED ${sources})
set_target_properties(bz2 PROPERTIES OUTPUT_NAME "bz2")

install(TARGETS bz2 
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
        ARCHIVE DESTINATION lib)

install(FILES bzlib.h DESTINATION include)