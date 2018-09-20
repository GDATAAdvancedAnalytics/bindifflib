cmake_minimum_required(VERSION 2.7)

project(iconv C)

FILE (GLOB sources LIST_DIRECTORIES false lib/*.h)
LIST (APPEND sources lib/iconv.c libcharset/lib/localcharset.c lib/relocatable.c)


add_library(iconv SHARED ${sources})
target_include_directories(iconv include/ localcharset/include/)
set_target_properties(iconv PROPERTIES OUTPUT_NAME "iconv")

install(TARGETS iconv 
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(DIRECTORY include/ DESTINATION include)