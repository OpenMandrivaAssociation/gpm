%bcond_without	ncurses

# this defines the library version that this package builds.
%define	major 2
%define	libname %mklibname %{name} %{major}
%define	devname %mklibname %{name} -d

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	1.99.7
Release:	5
License:	GPLv2+
Group:		System/Servers
Url:		http://www.nico.schottelius.org/software/gpm/
Source0:	http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{version}.tar.lzma
Source2:	inputattach.c
Source3:	gpm.service
# fedora patches (gpm-1.20.5-1.fc10.src.rpm)
Patch1:		gpm-1.20.1-multilib.patch
Patch2:		gpm-1.20.1-lib-silent.patch
Patch4:		gpm-1.20.5-close-fds.patch
Patch5:		gpm-1.20.7-weak-wgetch.patch
#Patch6:		gpm-1.20.6-missing-header-dir-in-make-depend.patch
# mdv patches
Patch50:	gpm-1.20.5-nodebug.patch
Patch51:	gpm-1.20.0-docfix.patch
Patch52:	gpm-1.20.7-do_not_build_it_twice.diff
Patch53:	gpm-1.20.5-format_not_a_string_literal_and_no_format_arguments.diff
# these automake files are utter crap, so just let's rip out the stuff that really doesn't belong
# there, we don't use and that's causing problem..
#Patch54:	gpm-1.20.7-fix-out-of-source-build.patch
Patch56:	gpm-1.99.7-fix-warnings.patch
Patch57:	gpm-1.99.7-compile.patch
# from debian
Patch58:	070_struct_ucred.diff

BuildRequires:	byacc
BuildRequires:	texinfo
%if %{with ncurses}
BuildRequires:	pkgconfig(ncursesw)
%endif
Requires(post,preun):	chkconfig
Requires(post,preun):	rpm-helper

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
OpenMandriva Lx system.

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

sed -i -e 's,git-describe,echo %{version},g' autogen.sh
echo %{version} >.gitversion
sed -i -e 's,.git/HEAD,,g' Makefile.in
./autogen.sh

%build
export ac_cv_path_emacs=no

# Heavy use of nested functions
export CC=gcc
export CXX=g++

CFLAGS="%{optflags} -fno-strict-aliasing" \
%configure \
	--enable-static \
%if !%{with ncurses}
	--without-curses
%endif

%make

%{__cc} %{optflags} %{ldflags} -o inputattach inputattach.c

%install
%makeinstall_std MKDIR="mkdir -p"

install -m644 example-configurations/gpm-root.conf -D %{buildroot}%{_sysconfdir}/gpm-root.conf
install -m755 inputattach -D %{buildroot}%{_sbindir}/inputattach

mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libgpm.so.%{major}* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libgpm.so.%{major}.*.* %{buildroot}%{_libdir}/libgpm.so

# systemd
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

%files -n %{libname}
/%{_lib}/libgpm.so.%{major}*

%files -n %{devname}
%{_libdir}/libgpm.a
%{_libdir}/libgpm.so
%{_includedir}/gpm.h
