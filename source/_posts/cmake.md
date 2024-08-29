layout: post

title: 简易 CMake 入门（miniob 版本）

author: junyu33

tags: 

- cmake

categories: 

- 笔记

date: 2023-10-30 00:00:00

---

# 简易 CMake 入门

> 首先建立一个直觉：CMake是与平台无关的，你不会制定具体使用什么编译器与链接器，也不会编写shell命令。最好把它当成一种**面向对象**的**新语言**看待。

<!-- more -->

## 最小范例

先看这个 minimum example:

```cmake
cmake_minimum_required(VERSION 3.8)

project(Calculator LANGUAGES CXX)

add_library(calclib STATIC src/calclib.cpp include/calc/lib.hpp)
target_include_directories(calclib PUBLIC include)
target_compile_features(calclib PUBLIC cxx_std_11)

add_executable(calc apps/calc.cpp)
target_link_libraries(calc PUBLIC calclib)
```

> 这里加粗字体表示必选项。

- **`cmake_minimum_required(VERSION 3.8)`** 
    - 指定使用的 CMake 版本标准。
- **`project(Calculator LANGUAGES CXX)`**
    - 制定项目的属性，此处名称为`Calculator`，项目名称与目标文件没有关系。
    - CMake大部分内建函数都有以下语法：`function([MODE ...] target ATTR1 val1 ATTR2 val2 ...)`，其中`val`可以是单个元素，也可以是一个列表（以空格或分号分割）
- `add_library(calclib STATIC src/calclib.cpp include/calc/lib.hpp)`：
    - 将`calclib.cpp`与`lib.hpp`以静态链接方式链接到`calclib`。（此时`calclib`是一个库）
- `target_include_directories(calclib PUBLIC include)`
    - 指定目标包含的库文件夹。（此处为项目路径的`include`）
- `target_compile_features(calclib PUBLIC cxx_std_11)`
    - 指定编译的选项。（此处为`--std=c++11`）
- **`add_executable(calc apps/calc.cpp)`**
    - 指定可执行文件，并使用`calc.cpp`编译。
- `target_link_libraries(calc PUBLIC calclib)`
    - 将`calclib`作为库链接到`calc`这个可执行文件。

## miniob

这是一个具有嵌套关系的项目：

- minidb
    - benchmark
    - deps/common
    - src
        - obclient
        - observer
    - test/perf
    - tools
    - unittest
        - (a set of unit tests)

这里只分析`minidb`与`observer`。

### minidb (根项目)

```cmake
cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)

project(minidb)

MESSAGE(STATUS "This is Project source dir " ${PROJECT_SOURCE_DIR})
MESSAGE(STATUS "This is PROJECT_BINARY_DIR dir " ${PROJECT_BINARY_DIR})

SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)

SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/cmake)

OPTION(ENABLE_ASAN "Enable build with address sanitizer" ON)
OPTION(WITH_UNIT_TESTS "Compile miniob with unit tests" ON)
OPTION(CONCURRENCY "Support concurrency operations" OFF)
OPTION(STATIC_STDLIB "Link std library static or dynamic, such as libgcc, libstdc++, libasan" OFF)
```

- 函数名不区分大小写；函数内部提倡关键字用大写，变量用小写。
- `set(CMAKE_CXX_STANDARD 20)` 
    - 相当于赋值语句。`CMAKE_CXX_STANDARD` = 20
    - 如果一个变量在先前没有出现，那么它应该是内建关键字，具体RTFM
- `MESSAGE(STATUS "This is Project source dir " ${PROJECT_SOURCE_DIR})`
    - 打印指令
    - `${foobar}` 表示解引用。
> `[cmake] -- This is Project source dir /home/junyu33/Desktop/github/miniob`
- `OPTION(foobar "comment" ON/OFF)`
    - 可以理解为对bool类型的`set`

```cmake
MESSAGE(STATUS "HOME dir: $ENV{HOME}")
#SET(ENV{变量名} 值)
IF(WIN32)
    MESSAGE(STATUS "This is windows.")
    ADD_DEFINITIONS(-DWIN32)
ELSEIF(WIN64)
    MESSAGE(STATUS "This is windows.")
    ADD_DEFINITIONS(-DWIN64)
ELSEIF(APPLE)
    MESSAGE(STATUS "This is apple")
    # normally __MACH__ has already been defined
    ADD_DEFINITIONS(-D__MACH__ )
ELSEIF(UNIX)
    MESSAGE(STATUS "This is UNIX")
    ADD_DEFINITIONS(-DUNIX -DLINUX)
ELSE()
    MESSAGE(STATUS "This is UNKNOW OS")
ENDIF(WIN32)

```

- 注意`${foobar}`在引号里也可以解引用
- 这里`WIN32 WIN64 APPLE`等都是内建关键字
- `IF ELSEIF`中条件为真的有以下类型：
    - `ON`, `YES`, `TRUE`, `Y`, or non zero number
- 为假的有以下类型：
    - `0`, `OFF`, `NO`, `FALSE`, `N`, `IGNORE`, `NOTFOUND`, `""`, or ends in `-NOTFOUND`
- `ADD_DEFINITIONS`：跟编译选项添加`-D`的语法一致

```cmake
# This is for clangd plugin for vscode
SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS} -Wall -Werror")
IF(DEBUG)
    MESSAGE(STATUS "DEBUG has been set as TRUE ${DEBUG}")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O0 -g -DDEBUG ")
    ADD_DEFINITIONS(-DENABLE_DEBUG)
ELSEIF(NOT DEFINED ENV{DEBUG})
    MESSAGE(STATUS "Disable debug")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O2 -g ")
ELSE()
    MESSAGE(STATUS "Enable debug")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O0 -g -DDEBUG")
    ADD_DEFINITIONS(-DENABLE_DEBUG)
ENDIF(DEBUG)
```

- 注意`CMAKE_COMMON_FLAGS`是一个用户定义的变量，你可以发现这里的添加都是增量添加
- `ENV`，取系统环境变量，`ENV{foo}`取环境变量`foo`

```cmake
IF (CONCURRENCY)
    MESSAGE(STATUS "CONCURRENCY is ON")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS} -DCONCURRENCY")
    ADD_DEFINITIONS(-DCONCURRENCY)
ENDIF (CONCURRENCY)

MESSAGE(STATUS "CMAKE_CXX_COMPILER_ID is " ${CMAKE_CXX_COMPILER_ID})
IF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" AND ${STATIC_STDLIB})
    ADD_LINK_OPTIONS(-static-libgcc -static-libstdc++)
ENDIF()
```

- `ADD_LINK_OPTIONS`，与前文所述的添加`DEFINITION`类似，这里指定链接选项
- `STREQUAL`：即`==`，注意`STREQUAL`的优先级高于`AND`


```cmake
IF (ENABLE_ASAN)
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS} -fno-omit-frame-pointer -fsanitize=address")
    IF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" AND ${STATIC_STDLIB})
        ADD_LINK_OPTIONS(-static-libasan)
    ENDIF()
ENDIF()

IF (CMAKE_INSTALL_PREFIX)
    MESSAGE(STATUS "CMAKE_INSTALL_PREFIX has been set as " ${CMAKE_INSTALL_PREFIX} )
ELSEIF(DEFINED ENV{CMAKE_INSTALL_PREFIX})
    SET(CMAKE_INSTALL_PREFIX $ENV{CMAKE_INSTALL_PREFIX})
ELSE()
    SET(CMAKE_INSTALL_PREFIX /tmp/${PROJECT_NAME})
ENDIF()
MESSAGE(STATUS "Install target dir is " ${CMAKE_INSTALL_PREFIX})

IF (DEFINED ENV{LD_LIBRARY_PATH})
    SET(LD_LIBRARY_PATH_STR $ENV{LD_LIBRARY_PATH})
    string(REPLACE ":" ";" LD_LIBRARY_PATH_LIST ${LD_LIBRARY_PATH_STR})
    MESSAGE(" Add LD_LIBRARY_PATH to -L flags " ${LD_LIBRARY_PATH_LIST})
    LINK_DIRECTORIES(${LD_LIBRARY_PATH_LIST})
ENDIF ()
```

- `string(REPLACE srcStr dstStr dstVal srcVal)`，类似还有`REGEX REPLACE`
- `LINK_DIRECTORIES`，与`TARGET_LINK_DIRECTORIES`类似，不指定某个具体的目标。

```cmake
IF (EXISTS /usr/local/lib)
    LINK_DIRECTORIES (/usr/local/lib)
ENDIF ()
IF (EXISTS /usr/local/lib64)
    LINK_DIRECTORIES (/usr/local/lib64)
ENDIF ()

INCLUDE_DIRECTORIES(. ${PROJECT_SOURCE_DIR}/deps /usr/local/include)

# ADD_SUBDIRECTORY(src bin)  bin 为目标目录， 可以省略
ADD_SUBDIRECTORY(deps)
ADD_SUBDIRECTORY(src/obclient)
ADD_SUBDIRECTORY(src/observer)
ADD_SUBDIRECTORY(test/perf)
ADD_SUBDIRECTORY(benchmark)
ADD_SUBDIRECTORY(tools)
```

- `EXISTS`： 检查路径是否存在
- `INCLUDE_DIRECTORIES`：与`TARGET_INCLUDE_DIRECTORIES`，不针对具体目标
- `ADD_SUBDIRECTORY`：如果子目录里有cmake项目（例如`CMakeLists.txt`），递归执行子目录中的项目

```cmake
IF(WITH_UNIT_TESTS)
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS} -fprofile-arcs -ftest-coverage")
    enable_testing()
    ADD_SUBDIRECTORY(unittest)
ENDIF(WITH_UNIT_TESTS)

SET(CMAKE_CXX_FLAGS ${CMAKE_COMMON_FLAGS})
SET(CMAKE_C_FLAGS ${CMAKE_COMMON_FLAGS})
MESSAGE(STATUS "CMAKE_CXX_FLAGS is " ${CMAKE_CXX_FLAGS})

INSTALL(DIRECTORY etc DESTINATION .
		FILE_PERMISSIONS OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ)
```

- `enable_testing()`：内建命令，启用测试。
    - This command should be in the source directory root because ctest expects to find a test file in the build directory root. This command is automatically invoked when the CTest module is included, except if the BUILD_TESTING option is turned off.
- `INSTALL`：对于`DIRECTORY`这个option，将`etc`里面的文件，以`OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ`的权限安装到当前目录。

### observer

```cmake
MESSAGE(STATUS "This is CMAKE_CURRENT_SOURCE_DIR dir " ${CMAKE_CURRENT_SOURCE_DIR})

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

FILE(GLOB_RECURSE ALL_SRC *.cpp *.c)
SET(MAIN_SRC main.cpp)
MESSAGE("MAIN SRC: " ${MAIN_SRC})
FOREACH (F ${ALL_SRC})

    IF (NOT ${F} STREQUAL ${MAIN_SRC})
        SET(LIB_SRC ${LIB_SRC} ${F})
    ENDIF()

    MESSAGE("Use " ${F})

ENDFOREACH (F)

SET(LIBEVENT_STATIC_LINK TRUE)
FIND_PACKAGE(Libevent CONFIG REQUIRED)
```

- `FILE(GLOB_RECURSE ...)`：`ALL_SRC = $(find . \( -name "*.c" -o -name "*.cpp" \))`
- `FOREACH`：`F`是循环变量，`${ALL_SRC}`是循环集合。
- `FIND_PACKAGE`：在`Libevent`的这个包里找配置文件，`REQUIRED`强调依赖性。

```cmake
SET(LIBRARIES common pthread dl libevent::core libevent::pthreads libjsoncpp.a)

# 指定目标文件位置
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
MESSAGE("Binary directory:" ${EXECUTABLE_OUTPUT_PATH})
SET(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)
MESSAGE("Archive directory:" ${LIBRARY_OUTPUT_PATH})

ADD_EXECUTABLE(observer ${MAIN_SRC})
TARGET_LINK_LIBRARIES(observer observer_static)

ADD_LIBRARY(observer_static STATIC ${LIB_SRC})
INCLUDE (readline)
MINIOB_FIND_READLINE()
```

- `INCLUDE(foobar)`：包含该`camke`文件，如果文件不存在，在`CMAKE_MODULE_PATH`中搜索名为`foobar.cmake`的文件。

```cmake
# readline.cmake
MACRO (MINIOB_FIND_READLINE)

  FIND_PATH(READLINE_INCLUDE_DIR readline.h PATH_SUFFIXES readline)
  FIND_LIBRARY(READLINE_LIBRARY NAMES readline)
  IF (READLINE_INCLUDE_DIR AND READLINE_LIBRARY)
    SET(HAVE_READLINE 1)
  ELSE ()
    MESSAGE("cannot find readline")
  ENDIF()

ENDMACRO (MINIOB_FIND_READLINE)
```

- `MACRO` 宏定义
- `find_path (<VAR> name1 [path1 path2 ...])`： 在后缀为`readline`中的文件夹寻找包含`readline.h`的文件夹，并保存至`READLINE_INCLUDE_DIR`
- `find_library (<VAR> name1 [path1 path2 ...])`:查找名字为`readline`的库文件。
> Each library name given to the NAMES option is first considered as a library file name and then considered with platform-specific prefixes (e.g. lib) and suffixes (e.g. .so). Therefore one may specify library file names such as libfoo.a directly. This can be used to locate static libraries on UNIX-like systems.

> `[cmake] readline include dir: /usr/include/readline`
> `[cmake] readline library: /usr/lib/libreadline.so`

```cmake
IF (HAVE_READLINE)
    TARGET_LINK_LIBRARIES(observer_static ${READLINE_LIBRARY})
    TARGET_INCLUDE_DIRECTORIES(observer_static PRIVATE ${READLINE_INCLUDE_DIR})
    ADD_DEFINITIONS(-DUSE_READLINE)
    MESSAGE ("observer_static use readline")
ELSE ()
    MESSAGE ("readline is not found")
ENDIF()

SET_TARGET_PROPERTIES(observer_static PROPERTIES OUTPUT_NAME observer)
TARGET_LINK_LIBRARIES(observer_static ${LIBRARIES})

# Target 必须在定义 ADD_EXECUTABLE 之后， programs 不受这个限制
# TARGETS和PROGRAMS 的默认权限是OWNER_EXECUTE, GROUP_EXECUTE, 和WORLD_EXECUTE，即755权限， programs 都是处理脚本类
# 类型分为RUNTIME／LIBRARY／ARCHIVE, prog
INSTALL(TARGETS observer observer_static 
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib)
```

- `SET_TARGET_PROPERTIES`：给目标设置属性，这里将目标名称设置为`observer`
- `install(TARGETS <target>... [...])`：部署`observer`与`observer_static`这两个目标的运行路径为`bin`，存档文件路径为`lib`。

# 杂项问题

## Cmake 究竟做了什么？

个人看来，Cmake 做了一个与平台无关的抽象，而 Cmake 的 build 过程相当于把它的语言“翻译”成平台相关的编译、链接命令，并组装为各种文件（在 Linux 即 `Makefile` 与相关的依赖文件）。

我们可以在 Cmake 的 build 目录找到相应的、机器生成的 `Makefile`。

## 如何在 Cmake 中实现类似于 `make -B` 或 `make -n` 的功能？

~~please RTFM~~

对于前者，可以使用 `--fresh` 参数。

对于后者，可以使用 `--trace` 实现。另外使用 `make --trace-expand` 可以展开相应的变量。 

## 以下代码中，`DEBUG`是从哪里来的？

```cmake
# This is for clangd plugin for vscode
SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS} -Wall -Werror")
IF(DEBUG)
    MESSAGE(STATUS "DEBUG has been set as TRUE ${DEBUG}")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O0 -g -DDEBUG ")
    ADD_DEFINITIONS(-DENABLE_DEBUG)
ELSEIF(NOT DEFINED ENV{DEBUG})
    MESSAGE(STATUS "Disable debug")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O2 -g ")
ELSE()
    MESSAGE(STATUS "Enable debug")
    SET(CMAKE_COMMON_FLAGS "${CMAKE_COMMON_FLAGS}  -O0 -g -DDEBUG")
    ADD_DEFINITIONS(-DENABLE_DEBUG)
ENDIF(DEBUG)
```

你没有查看`build.sh`：

```sh
function build
{
  set -- "${BUILD_ARGS[@]}"
  case "x$1" in
    xrelease)
      do_build "$@" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DDEBUG=OFF
      ;;
    xdebug)
      do_build "$@" -DCMAKE_BUILD_TYPE=Debug -DDEBUG=ON
      ;;
    *)
      BUILD_ARGS=(debug "${BUILD_ARGS[@]}")
      build
      ;;
  esac
}
```

这里面有一个编译选项`-DDEBUG=ON`，按照上文描述的方法 trace，或者在相应的位置打个 log 即可确认 `DEBUG` 这部变量来自于 `cmake` 的运行参数。




# Ref

https://modern-cmake-cn.github.io/Modern-CMake-zh_CN/

https://cmake.org/cmake/help/latest/index.html
