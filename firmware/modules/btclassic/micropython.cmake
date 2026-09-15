add_library(usermod_btclassic INTERFACE)

target_sources(usermod_btclassic INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/btclassic.c
)

target_include_directories(usermod_btclassic INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(usermod INTERFACE usermod_btclassic)
