cmake_minimum_required(VERSION 2.7)

project(tinyxml)

set (SOURCES tinyxml.cpp tinyxmlparser.cpp xmltest.cpp tinyxmlerror.cpp tinystr.cpp)
set (HEADERS tinystr.h tinyxml.h)

add_library(tinyxml SHARED ${SOURCES} ${HEADERS})

set_target_properties(tinyxml PROPERTIES OUTPUT_NAME "tinyxml")

install(TARGETS tinyxml 
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(FILES ${HEADERS} DESTINATION include)