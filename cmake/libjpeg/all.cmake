cmake_minimum_required(VERSION 2.7)

project(libjpeg)

set (SOURCES jaricom.c jcapimin.c jcapistd.c jcarith.c jccoefct.c jccolor.c 
        jcdctmgr.c jchuff.c jcinit.c jcmainct.c jcmarker.c jcmaster.c 
        jcomapi.c jcparam.c jcprepct.c jcsample.c jctrans.c jdapimin.c 
        jdapistd.c jdarith.c jdatadst.c jdatasrc.c jdcoefct.c jdcolor.c 
        jddctmgr.c jdhuff.c jdinput.c jdmainct.c jdmarker.c jdmaster.c 
        jdmerge.c jdpostct.c jdsample.c jdtrans.c jerror.c jfdctflt.c 
        jfdctfst.c jfdctint.c jidctflt.c jidctfst.c jidctint.c jquant1.c 
        jquant2.c jutils.c jmemmgr.c jmemnobs.c)
set (HEADERS jdct.h jerror.h jinclude.h jmemsys.h jmorecfg.h jpegint.h 
        jpeglib.h jversion.h cdjpeg.h cderror.h transupp.h jconfig.h)

if (NOT (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/jconfig.h))
    file(RENAME jconfig.vc jconfig.h)
endif()

add_library(libjpeg_shared SHARED ${SOURCES} ${HEADERS})
add_library(libjpeg STATIC ${SOURCES} ${HEADERS})

set_target_properties(libjpeg PROPERTIES OUTPUT_NAME "libjpeg")
set_target_properties(libjpeg_shared PROPERTIES OUTPUT_NAME "libjpeg_shared")

install(TARGETS libjpeg 
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(TARGETS libjpeg_shared
        RUNTIME DESTINATION bin)

install(FILES ${HEADERS} DESTINATION include)