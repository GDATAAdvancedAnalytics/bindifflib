cmake_minimum_required(VERSION 2.7)

project(libxml2 C)

# set (SOURCES buf.c c14n.c catalog.c chvalid.c debugXML.c dict.c encoding.c 
#              entities.c error.c globals.c hash.c HTMLparser.c HTMLtree.c 
#              legacy.c list.c nanoftp.c nanohttp.c parserInternals.c 
#              parser.c pattern.c relaxng.c SAX2.c SAX.c schematron.c 
#              testdso.c threads.c tree.c uri.c valid.c xinclude.c xlink.c 
#              xmlIO.c xmlmemory.c xmlmodule.c xmlreader.c xmlregexp.c 
#              xmlsave.c xmlschemas.c xmlschemastypes.c xmlstring.c 
#              xmlunicode.c xmlwriter.c xpath.c xpointer.c xzlib.c)

FILE (GLOB SOURCES LIST_DIRECTORIES false *.c)
FILE (GLOB HEADERS_local LIST_DIRECTORIES false *.h)
FILE (GLOB_RECURSE HEADERS_include LIST_DIRECTORIES false include/*.h)
SET (HEADERS ${HEADERS_local} ${HEADERS_include})

include_directories(${CMAKE_CURRENT_SOURCE_DIR} include/)

add_library(xml2 SHARED ${SOURCES})
set_target_properties(xml2 PROPERTIES OUTPUT_NAME "xml2")

install(TARGETS xml2
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(FILES HEADERS_include DESTINATION include)