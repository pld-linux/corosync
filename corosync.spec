# Conditional build:
%bcond_with	apidocs		# build apidocs

Summary:	Corosync - OSI Certified implementation of a complete cluster engine
Name:		corosync
Version:	1.0.0
Release:	1
License:	BSD
Group:		Base
Source0:	http://devresources.linux-foundation.org/dev/openais/downloads/%{name}-%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	257f5509f3da951ba84b596fedf42185
URL:		http://www.corosync.org/
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_apidocs:BuildRequires:	doxygen}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Corosync Cluster Engine is an OSI Certified implementation of a
complete cluster engine.

%package libs
Summary:	The corosync OSI Certified implementation of a complete cluster engine libraries
Group:		Libraries

%description libs
This package contains the corosync libraries.

%package devel
Summary:	The corosync OSI Certified implementation of a complete cluster engine libraries development files
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the include files used to develop using corosync
APIs.

%package static
Summary:	The corosync OSI Certified implementation of a complete cluster engine static libraries
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
This package contains the corosync static libraries.

%prep
%setup -q

%build
%{__aclocal}
%{__autoconf}
%{__automake}

%configure \
	--enable-nss \
	--with-lcrso-dir=%{_libdir}/lcrso

%{__make}

%{?with_apidocs:%{__make} doxygen}
    
%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT/usr/share/doc/corosync

mv $RPM_BUILD_ROOT/etc/corosync/corosync.conf{.example,}
sed -i -e 's/\(^.*$\)/#\1/' $RPM_BUILD_ROOT/etc/corosync/corosync.conf

%{?with_apidocs:install doc/api/man/man3/* $RPM_BUILD_ROOT%{_mandir}/man3}

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG README.devmap README.recovery SECURITY
%defattr(644,root,root,755)
%dir %{_sysconfdir}/corosync
%verify(not md5 mtime size) %config(noreplace) %{_sysconfdir}/corosync/corosync.conf
%attr(755,root,root) %{_sbindir}/corosync
%attr(755,root,root) %{_sbindir}/corosync-cfgtool
%attr(755,root,root) %{_sbindir}/corosync-fplay
%attr(755,root,root) %{_sbindir}/corosync-keygen
%attr(755,root,root) %{_sbindir}/corosync-objctl
%attr(755,root,root) %{_sbindir}/corosync-pload
%attr(755,root,root) %{_libdir}/lcrso/*.lcrso
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*

%files libs
%defattr(644,root,root,755)
%dir %{_libdir}/lcrso
%attr(755,root,root) %{_libdir}/libcfg.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcfg.so.4
%attr(755,root,root) %{_libdir}/libconfdb.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libconfdb.so.4
%attr(755,root,root) %{_libdir}/libcoroipcc.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcoroipcc.so.4
%attr(755,root,root) %{_libdir}/libcoroipcs.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcoroipcs.so.4
%attr(755,root,root) %{_libdir}/libcpg.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcpg.so.4
%attr(755,root,root) %{_libdir}/libevs.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libevs.so.4
%attr(755,root,root) %{_libdir}/liblogsys.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/liblogsys.so.4
%attr(755,root,root) %{_libdir}/libpload.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libpload.so.4
%attr(755,root,root) %{_libdir}/libquorum.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libquorum.so.4
%attr(755,root,root) %{_libdir}/libtotem_pg.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libtotem_pg.so.4
%attr(755,root,root) %{_libdir}/libvotequorum.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libvotequorum.so.4

%files devel
%defattr(644,root,root,755)
%{_includedir}/corosync
%{_libdir}/libcfg.so
%{_libdir}/libconfdb.so
%{_libdir}/libcoroipcc.so
%{_libdir}/libcoroipcs.so
%{_libdir}/libcpg.so
%{_libdir}/libevs.so
%{_libdir}/liblogsys.so
%{_libdir}/libpload.so
%{_libdir}/libquorum.so
%{_libdir}/libtotem_pg.so
%{_libdir}/libvotequorum.so
%{_pkgconfigdir}/*.pc
%{_mandir}/man3/*.3*

%files static
%defattr(644,root,root,755)
%{_libdir}/libcfg.a
%{_libdir}/libconfdb.a
%{_libdir}/libcoroipcc.a
%{_libdir}/libcoroipcs.a
%{_libdir}/libcpg.a
%{_libdir}/libevs.a
%{_libdir}/liblcr.a
%{_libdir}/liblogsys.a
%{_libdir}/libpload.a
%{_libdir}/libquorum.a
%{_libdir}/libtotem_pg.a
%{_libdir}/libvotequorum.a
