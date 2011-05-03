dnl --------------------------------
dnl Initialization macros.
dnl --------------------------------


AC_INIT(hnd, 0.1, morgenro@ibr.cs.tu-bs.de)
AC_CONFIG_SRCDIR(src/Main.cpp)
AM_INIT_AUTOMAKE
LT_INIT
AM_PATH_CPPUNIT(1.9.6)

AC_CONFIG_HEADER([src/config.h])
AC_CONFIG_MACRO_DIR([m4])
AM_MAINTAINER_MODE

dnl -----------------------------------------------
dnl Checks for programs.
dnl -----------------------------------------------

AC_PROG_CXX
AC_PROG_CC

AC_PROG_AWK
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_MAKE_SET
AC_LIBTOOL_DLOPEN
AC_PROG_LIBTOOL

AC_LANG_CPLUSPLUS

# check for ibrcommon library
LOCAL_IBRCOMMON_VERSION=0.5
LOCAL_CHECK_IBRCOMMON
AC_SUBST(ibrcommon_CFLAGS)
AC_SUBST(ibrcommon_LIBS)


dnl -----------------------------------------------
dnl Generates Makefiles, configuration files and scripts
dnl -----------------------------------------------

AC_CONFIG_FILES([Makefile \
                 doc/Makefile \
                 man/Makefile \
                 src/Makefile])
	
AC_OUTPUT