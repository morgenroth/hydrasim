AUTOMAKE_OPTIONS = foreign

# what flags you want to pass to the C compiler & linker
AM_CPPFLAGS = @ibrcommon_CFLAGS@
AM_LDFLAGS = @ibrcommon_LIBS@

INCLUDES = -I@top_srcdir@/src

# this lists the binaries to produce, the (non-PHONY, binary) targets in
# the previous manual Makefile
bin_PROGRAMS = hnd
#sbin_PROGRAMS = 
hnd_SOURCES = Main.cpp \
		Configuration.h \
		Configuration.cpp \
		DiscoverComponent.h \
		DiscoverComponent.cpp \
		CommandServer.h \
		CommandServer.cpp \
		FakeGPS.h \
		FakeGPS.cpp \
		HostControl.h \
		HostControl.cpp
