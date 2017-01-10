%bcond_without	ncurses
%bcond_with	uclibc

# this defines the library version that this package builds.
%define	major 2
%define	libname %mklibname %{name} %{major}
%define	devname %mklibname %{name} -d

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	1.20.7.1
Epoch:		1
Release:	1
License:	GPLv2+
Group:		System/Servers
Url:		http://www.nico.schottelius.org/software/gpm/
Source0:	https://github.com/proyvind/gpm/archive/%{version}.tar.gz
#(proyvind): please don't remove, still used by ucDrakX micro environment
Source1:	gpm.init
Source2:	inputattach.c
Source3:	gpm.service
# fedora patches (gpm-1.20.5-1.fc10.src.rpm)
Patch1:		gpm-1.20.1-multilib.patch
Patch2:		gpm-1.20.7.1-lib-silent.patch
Patch4:		gpm-1.20.7.1-close-fds.patch
Patch5:		gpm-1.20.7.1-weak-wgetch.patch
# mdv patches
Patch50:	gpm-1.20.7.1-nodebug.patch
Patch51:	gpm-1.20.0-docfix.patch
Patch55:	gpm-1.99.7-uclibc.patch
# these automake files are utter crap, so just let's rip out the stuff that really doesn't belong
# there, we don't use and that's causing problem..
Patch57:	gpm-1.20.7.1-compile.patch

BuildRequires:	byacc
BuildRequires:	texinfo
%if %{with ncurses}
BuildRequires:	pkgconfig(ncursesw)
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-3
BuildRequires:	uclibc-ncurses-devel
%endif

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
OpenMandriva Lx system.

%if %{with uclibc}
%package -n	uclibc-%{name}
Summary:	A mouse server for the Linux console (uClibc build)
Group:		System/Servers

%description -n	uclibc-%{name}
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

%package -n	uclibc-%{libname}
Summary:	Libraries and header files for developing mouse driven programs (uClibc build)
Group:		System/Libraries

%description -n	uclibc-%{libname}
Library used by the gpm program.

%package -n	uclibc-%{devname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{devname} = %{EVRD}
Requires:	uclibc-%{libname} = %{EVRD}
Provides:	uclibc-%{name}-devel = %{EVRD}
Conflicts:	%{devname} < 1.20.7-15

%description -n	uclibc-%{devname}
The uclibc-%{devname} package contains the libraries and header 
files needed for development of mouse driven programs.
This package allows you to develop text-mode programs which 
use the mouse.

Install uclibc-%{devname} if you need to develop text-mode
programs which will use the mouse.
You'll also need to install the gpm package.
%endif

%package -n	%{libname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries

%description -n	%{libname}
Library used by the gpm program.

Install %{libname}dev if you need to develop text-mode programs which 
will use the mouse. You'll also need to install the gpm package.

%package -n	%{devname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
The %{devname} package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %{devname} if you need to develop text-mode programs which
will use the mouse. You'll also need to install the gpm package.

%prep
%setup -q
find -name \*.c |xargs chmod 644
# The code is nowhere near compiling with -Werror with clang 3.7
sed -i -e 's,-Werror ,,' Makefile.*

%apply_patches

cp %{SOURCE2} inputattach.c

./autogen.sh

%if %{with uclibc}
mkdir .uclibc
find .uclibc -name ".*~" |xargs rm -rf
%endif

%build
export ac_cv_path_emacs=no

%if %{with uclibc}
pushd .uclibc
%define uclibc_cflags %{optflags} -fno-strict-aliasing
%uclibc_configure \
	--disable-static \
%if !%{with ncurses}
	--without-curses
%endif
#
%make
unset CFLAGS
popd
%endif

CFLAGS="%{optflags} -fno-strict-aliasing" \
%configure \
	--enable-static \
%if !%{with ncurses}
	--without-curses
%endif

%make

%{__cc} %{optflags} %{ldflags} -o inputattach inputattach.c

%install
%if %{with uclibc}
%makeinstall_std -C .uclibc MKDIR="mkdir -p"
mkdir -p %{buildroot}%{uclibc_root}/%{_lib}
mv %{buildroot}%{uclibc_root}%{_libdir}/libgpm.so.%{major}* %{buildroot}%{uclibc_root}/%{_lib}
ln -srf %{buildroot}%{uclibc_root}/%{_lib}/libgpm.so.%{major}.* %{buildroot}%{uclibc_root}%{_libdir}/libgpm.so
%endif

%makeinstall_std MKDIR="mkdir -p"

install -m644 conf/gpm-root.conf -D %{buildroot}%{_sysconfdir}/gpm-root.conf
install -m755 inputattach -D %{buildroot}%{_sbindir}/inputattach

mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libgpm.so.%{major}* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libgpm.so.%{major}.*.* %{buildroot}%{_libdir}/libgpm.so

%if %{with uclibc}
install -m755 %{SOURCE1} -D %{buildroot}%{_initrddir}/gpm
%endif
install -m644 %{SOURCE3} -D %{buildroot}%{_unitdir}/gpm.service

rm -f %{buildroot}%{uclibc_root}%{_libdir}/*.a

%files
%config(noreplace) %{_sysconfdir}/gpm-root.conf
%{_unitdir}/gpm.service
%{_bindir}/display-buttons
%{_bindir}/display-coords
%{_bindir}/mev
%{_bindir}/gpm-root
%{_bindir}/hltest
%{_bindir}/mouse-test
%{_bindir}/disable-paste
%{_bindir}/get-versions
%{_sbindir}/gpm
%{_sbindir}/inputattach
%{_infodir}/gpm.info*
%{_mandir}/man1/mev.1*
%{_mandir}/man1/mouse-test.1*
%{_mandir}/man1/gpm-root.1*
%{_mandir}/man7/gpm-types.7*
%{_mandir}/man8/gpm.8*

%if %{with uclibc}
%files -n uclibc-%{name}
%{_initrddir}/gpm
%{uclibc_root}%{_bindir}/display-buttons
%{uclibc_root}%{_bindir}/display-coords
%{uclibc_root}%{_bindir}/mev
%{uclibc_root}%{_bindir}/gpm-root
%{uclibc_root}%{_bindir}/hltest
%{uclibc_root}%{_bindir}/mouse-test
%{uclibc_root}%{_bindir}/disable-paste
%{uclibc_root}%{_bindir}/get-versions
%{uclibc_root}%{_sbindir}/gpm
%endif

%files -n %{libname}
/%{_lib}/libgpm.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libgpm.so.%{major}*

%files -n uclibc-%{devname}
%{uclibc_root}%{_libdir}/libgpm.so
%endif

%files -n %{devname}
%{_libdir}/libgpm.a
%{_libdir}/libgpm.so
%{_includedir}/gpm.h
