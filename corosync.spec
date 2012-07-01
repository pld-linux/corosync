#
# Conditional build:
%bcond_with	apidocs		# build apidocs (man3 pages are provided anyway)
%bcond_without	dbus		# DBus events
%bcond_without	rdma		# RDMA support
%bcond_without	snmp		# SNMP protocol support
%bcond_with testagents
%bcond_with watchdog
%bcond_with monitoring
%bcond_with xmlconf
#
Summary:	Corosync - OSI Certified implementation of a complete cluster engine
Summary(pl.UTF-8):	Corosync - implementacja silnika klastrowego certyfikowana przez OSI
Name:		corosync
Version:	2.0.1
Release:	0.1
License:	BSD
Group:		Base
Source0:	ftp://ftp:downloads@corosync.org/downloads/%{name}-%{version}/corosync-%{version}.tar.gz
# Source0-md5:	9e23f3f5594676455ff39ff363658155
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-lib_deps.patch
Patch2:		%{name}-install.patch
URL:		http://www.corosync.org/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake
%{?with_dbus:BuildRequires:	dbus-devel}
%{?with_apidocs:BuildRequires:	doxygen}
BuildRequires:	libqb-devel
%if %{with rdma}
BuildRequires:	libibverbs-devel
BuildRequires:	librdmacm-devel
%endif
%{?with_xmlconf:BuildRequires:	libxslt}
%{?with_snmp:BuildRequires:	net-snmp-devel}
BuildRequires:	nss-devel
BuildRequires:	pkgconfig
Requires:	%{name}-libs = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# short_service_name_get() is defined in executable
%define		skip_post_check_so	libcoroipcs\.so.*

%description
The Corosync Cluster Engine is an OSI Certified implementation of a
complete cluster engine.

%description -l pl.UTF-8
Corosync Cluster Engine to implementacja pełnego silnika klastrowego
certyfikowana przez OSI.

%package libs
Summary:	Corosync Cluster Engine libraries
Summary(pl.UTF-8):	Biblioteki silnika klastrowego Corosync
Group:		Libraries

%description libs
This package contains the libraries of Corosync Cluster Engine, an OSI
Certified implementation of a complete cluster engine.

%description libs -l pl.UTF-8
Ten pakiet zawiera biblioteki Corosync Cluster Engine - pełnego
silnika klastrowego certyfikowanego przez OSI.

%package devel
Summary:	Header files for Corosync libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek Corosync
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Conflicts:	openais-devel < 1.0

%description devel
This package contains the include files used to develop using Corosync
APIs.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe potrzebne do tworzenia programów z
użyciem API Corosync.

%package static
Summary:	Corosync static libraries
Summary(pl.UTF-8):	Statyczne biblioteki Corosync
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
This package contains the Corosync static libraries.

%description static -l pl.UTF-8
Ten pakiet zawiera statyczne biblioteki Corosync.

%package -n mibs-corosync
Summary:	Corosync SNMP MIB data
Summary(pl.UTF-8):	Dane SNMP MIB dla Corosync
Group:		Applications/System
Requires:	mibs-dirs

%description -n mibs-corosync
Corosync SNMP MIB data.

%description -n mibs-corosync -l pl.UTF-8
Dane SNMP MIB dla Corosync.

%package -n corosync-testagents
Summary:	The Corosync Cluster Engine Test Agents
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description -n corosync-testagents
This package contains corosync test agents.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	%{?with_testagents:--enable-testagents} \
	%{?with_watchdog:--enable-watchdog} \
	%{?with_monitoring:--enable-monitoring} \
	%{?with_xmlconf:--enable-xmlconf} \
	%{?with_dbus:--enable-dbus} \
	%{?with_rdma:--enable-rdma} \
	%{?with_snmp:--enable-snmp} \
	--enable-systemd \
	--with-systemddir=%{systemdunitdir} \
	--with-initddir=/etc/rc.d/init.d

%{__make}

%{?with_apidocs:%{__make} doxygen}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/corosync

sed -e 's/^/#/' $RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf.example \
	>$RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf.example*

%{?with_apidocs:install doc/api/man/man3/* $RPM_BUILD_ROOT%{_mandir}/man3}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add corosync
%service corosync restart "Corosync Cluster Engine"

%systemd_post corosync.service

%preun
if [ "$1" = "0" ]; then
        %service corosync stop
        /sbin/chkconfig --del corosync
fi
%systemd_preun corosync.service

%postun
%systemd_reload

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog LICENSE README.recovery SECURITY TODO conf/corosync.conf.example*
%if %{with xmlconf}
%doc conf/corosync.xml.example*
%endif
%attr(754,root,root) /etc/rc.d/init.d/corosync
%attr(754,root,root) /etc/rc.d/init.d/corosync-notifyd
%dir %{_sysconfdir}/corosync
%{systemdunitdir}/corosync.service
%{systemdunitdir}/corosync-notifyd.service
%verify(not md5 mtime size) %config(noreplace) %{_sysconfdir}/corosync/corosync.conf
%attr(755,root,root) %{_bindir}/corosync-blackbox
%attr(755,root,root) %{_sbindir}/corosync
%attr(755,root,root) %{_sbindir}/corosync-cfgtool
%attr(755,root,root) %{_sbindir}/corosync-cmapctl
%attr(755,root,root) %{_sbindir}/corosync-cpgtool
%attr(755,root,root) %{_sbindir}/corosync-fplay
%attr(755,root,root) %{_sbindir}/corosync-keygen
%attr(755,root,root) %{_sbindir}/corosync-notifyd
%attr(755,root,root) %{_sbindir}/corosync-quorumtool
%{_mandir}/man5/corosync.conf.5*
%{_mandir}/man8/corosync.8*
%{_mandir}/man8/corosync-blackbox.8*
%{_mandir}/man8/corosync-cmapctl.8*
%{_mandir}/man8/corosync-cfgtool.8*
%{_mandir}/man8/corosync-cpgtool.8*
%{_mandir}/man8/corosync-fplay.8*
%{_mandir}/man8/corosync-keygen.8*
%{_mandir}/man8/corosync-notifyd.8*
%{_mandir}/man8/corosync-quorumtool.8*
%if %{with xmlconf}
%attr(755,root,root) %{_bindir}/corosync-xmlproc
%config(noreplace) %{_sysconfdir}/corosync/corosync.xml.example
%dir %{_datadir}/corosync
%dir %{_datadir}/corosync/xml2conf.xsl
%{_mandir}/man8/corosync-xmlproc.8*
%{_mandir}/man5/corosync.xml.5*
%endif
%if %{with dbus}
/etc/dbus-1/system.d/corosync-signals.conf
%endif

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcfg.so.6.*.*
%attr(755,root,root) %ghost %{_libdir}/libcfg.so.6
%attr(755,root,root) %{_libdir}/libcmap.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcmap.so.4
%attr(755,root,root) %{_libdir}/libcorosync_common.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcorosync_common.so.4
%attr(755,root,root) %{_libdir}/libcpg.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libcpg.so.4
%attr(755,root,root) %{_libdir}/libsam.so.4.*.*
%attr(755,root,root) %ghost %{_libdir}/libsam.so.4
%attr(755,root,root) %{_libdir}/libquorum.so.5.*.*
%attr(755,root,root) %ghost %{_libdir}/libquorum.so.5
%attr(755,root,root) %{_libdir}/libtotem_pg.so.5.*.*
%attr(755,root,root) %ghost %{_libdir}/libtotem_pg.so.5
%attr(755,root,root) %{_libdir}/libvotequorum.so.5.*.*
%attr(755,root,root) %ghost %{_libdir}/libvotequorum.so.5

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcfg.so
%attr(755,root,root) %{_libdir}/libcmap.so
%attr(755,root,root) %{_libdir}/libcorosync_common.so
%attr(755,root,root) %{_libdir}/libcpg.so
%attr(755,root,root) %{_libdir}/libsam.so
%attr(755,root,root) %{_libdir}/libquorum.so
%attr(755,root,root) %{_libdir}/libtotem_pg.so
%attr(755,root,root) %{_libdir}/libvotequorum.so
%{_includedir}/corosync
%{_pkgconfigdir}/corosync.pc
%{_pkgconfigdir}/libcfg.pc
%{_pkgconfigdir}/libcmap.pc
%{_pkgconfigdir}/libcorosync_common.pc
%{_pkgconfigdir}/libcpg.pc
%{_pkgconfigdir}/libquorum.pc
%{_pkgconfigdir}/libsam.pc
%{_pkgconfigdir}/libtotem_pg.pc
%{_pkgconfigdir}/libvotequorum.pc
%{_mandir}/man3/cmap_*.3*
%{_mandir}/man3/cpg_*.3*
%{_mandir}/man3/quorum_*.3*
%{_mandir}/man3/sam_*.3*
%{_mandir}/man3/votequorum_*.3*
%{_mandir}/man5/votequorum.5*
# should be man7...
%{_mandir}/man8/cmap_keys.8*
%{_mandir}/man8/cmap_overview.8*
%{_mandir}/man8/corosync_overview.8*
%{_mandir}/man8/cpg_overview.8*
%{_mandir}/man8/sam_overview.8*
%{_mandir}/man8/votequorum_overview.8*
%{_mandir}/man8/quorum_overview.8*
%files static
%defattr(644,root,root,755)
%{_libdir}/libcfg.a
%{_libdir}/libcmap.a
%{_libdir}/libcorosync_common.a
%{_libdir}/libcpg.a
%{_libdir}/libsam.a
%{_libdir}/libquorum.a
%{_libdir}/libtotem_pg.a
%{_libdir}/libvotequorum.a

%if %{with snmp}
%files -n mibs-corosync
%defattr(644,root,root,755)
%{_datadir}/snmp/mibs/COROSYNC-MIB.txt
%endif

%if %{with testagents}
%files -n corosync-testagents
%defattr(644,root,root,755)
%{_datadir}/corosync/tests/mem_leak_test.sh
%{_datadir}/corosync/tests/net_breaker.sh
%{_datadir}/corosync/tests/cmap-dispatch-deadlock.sh
%{_datadir}/corosync/tests/shm_leak_audit.sh
%attr(755,root,root) %{_bindir}/cpg_test_agent
%attr(755,root,root) %{_bindir}/sam_test_agent
%attr(755,root,root) %{_bindir}/votequorum_test_agent
%endif
