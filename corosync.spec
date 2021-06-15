#
# Conditional build:
%bcond_without	apidocs		# build apidocs (some man3 pages are provided anyway)
%bcond_without	augeas		# augeas lens support
%bcond_without	dbus		# DBus events
%bcond_without	rdma		# RDMA support
%bcond_without	snmp		# SNMP protocol support
%bcond_without	testagents	# test agents build
%bcond_without	watchdog	# watchdog support
%bcond_without	monitoring	# resource monitoring
%bcond_without	qdevices	# Quorum devices support
%bcond_without	qnetd		# Quorum Net Daemon support
%bcond_without	xmlconf		# XML configuration support
%bcond_without	libcgroup	# libcgroup support
#
Summary:	Corosync - OSI Certified implementation of a complete cluster engine
Summary(pl.UTF-8):	Corosync - implementacja silnika klastrowego certyfikowana przez OSI
Name:		corosync
Version:	2.4.5
Release:	4
License:	BSD
Group:		Base
#Source0Download: http://corosync.org/download/
Source0:	https://build.clusterlabs.org/corosync/releases/%{name}-%{version}.tar.gz
# Source0-md5:	e36a056b893c313c4ec1fe0d7e6cdebd
Source1:	%{name}.init
Source2:	%{name}-notifyd.init
Source3:	%{name}-notifyd.sysconfig
URL:		https://www.corosync.org/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake >= 1:1.11
%{?with_dbus:BuildRequires:	dbus-devel}
%{?with_apidocs:BuildRequires:	doxygen}
%{?with_apidocs:BuildRequires:	graphviz}
BuildRequires:	groff
%{?with_libcgroup:BuildRequires:	libcgroup-devel}
BuildRequires:	libqb-devel
%if %{with rdma}
BuildRequires:	libibverbs-devel
BuildRequires:	librdmacm-devel
%endif
%{?with_monitoring:BuildRequires:	libstatgrab-devel >= 0.90}
BuildRequires:	libtool >= 2:2.2.6
%{?with_snmp:BuildRequires:	net-snmp-devel}
BuildRequires:	nss-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.644
# only for cpghum test program
#BuildRequires:	zlib-devel
%{?with_xmlconf:Requires:	libxslt-progs}
Requires:	rc-scripts
Requires:	systemd-units >= 38
Requires(post,preun):	/sbin/chkconfig
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

%package testagents
Summary:	The Corosync Cluster Engine test agents
Summary(pl.UTF-8):	Testowi agenci silnika klastrowego Corosync
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description testagents
This package contains Corosync test agents.

%description testagents -l pl.UTF-8
Ten pakiet zawiera testowych agentów silnika Corosync.

%package -n mibs-corosync
Summary:	Corosync SNMP MIB data
Summary(pl.UTF-8):	Dane SNMP MIB dla Corosync
Group:		Applications/System
Requires:	mibs-dirs

%description -n mibs-corosync
Corosync SNMP MIB data.

%description -n mibs-corosync -l pl.UTF-8
Dane SNMP MIB dla Corosync.

%prep
%setup -q

# force regeneration with proper BASHPATH
%{__rm} cts/agents/{cmap-dispatch-deadlock,shm_leak_audit}.sh

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	BASHPATH=/bin/bash \
	%{?with_augeas:--enable-augeas} \
	%{?with_dbus:--enable-dbus} \
	%{?with_libcgroup:--enable-libcgroup} \
	%{?with_monitoring:--enable-monitoring} \
	%{?with_qdevices:--enable-qdevices} \
	%{?with_qnetd:--enable-qnetd} \
	%{?with_rdma:--enable-rdma} \
	--disable-silent-rules \
	%{?with_snmp:--enable-snmp} \
	--enable-systemd \
	%{?with_testagents:--enable-testagents} \
	%{?with_watchdog:--enable-watchdog} \
	%{?with_xmlconf:--enable-xmlconf} \
	--with-initddir=/etc/rc.d/init.d \
	--with-systemddir=%{systemdunitdir}

%{__make}

%{?with_apidocs:%{__make} doxygen}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig}
install -d $RPM_BUILD_ROOT/var/log/cluster

%{__make} install \
	mibdir=%{_datadir}/mibs \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/corosync

sed -e 's/^/#/' $RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf.example \
	>$RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/corosync/corosync.conf.example*

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}-notifyd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}-notifyd

%if %{with qdevices} || %{with qnetd}
install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/corosync.conf <<EOF
%if %{with qdevices}
d /var/run/corosync-qdevice 0770 root root -
%endif
%if %{with qnetd}
d /var/run/corosync-qnetd 0770 root root -
%endif
EOF
%endif

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/lib*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
/sbin/chkconfig --add %{name}-notifyd
%service %{name}-notifyd restart
%systemd_post %{name}-notifyd.service
export NORESTART=1
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
	%service -q %{name}-notifyd stop
	/sbin/chkconfig --del %{name}-notifyd
fi
%systemd_preun %{name}.service
%systemd_preun %{name}-notifyd.service

%postun
%systemd_reload

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog LICENSE README.recovery SECURITY conf/corosync.conf.example*
%if %{with xmlconf}
%doc conf/corosync.xml.example*
%endif
%attr(754,root,root) /etc/rc.d/init.d/corosync
%attr(754,root,root) /etc/rc.d/init.d/corosync-notifyd
%verify(not md5 mtime size) %config(noreplace) /etc/logrotate.d/%{name}
%verify(not md5 mtime size) %config(noreplace) /etc/sysconfig/%{name}-notifyd
%dir %{_sysconfdir}/corosync
%dir %{_sysconfdir}/corosync/service.d
%dir %{_sysconfdir}/corosync/uidgid.d
%{systemdunitdir}/corosync.service
%{systemdunitdir}/corosync-notifyd.service
%if %{with qdevices} || %{with qnetd}
%{systemdtmpfilesdir}/corosync.conf
%endif
%verify(not md5 mtime size) %config(noreplace) %{_sysconfdir}/corosync/corosync.conf
%attr(755,root,root) %{_bindir}/corosync-blackbox
%attr(755,root,root) %{_sbindir}/corosync
%attr(755,root,root) %{_sbindir}/corosync-cfgtool
%attr(755,root,root) %{_sbindir}/corosync-cmapctl
%attr(755,root,root) %{_sbindir}/corosync-cpgtool
%attr(755,root,root) %{_sbindir}/corosync-keygen
%attr(755,root,root) %{_sbindir}/corosync-notifyd
%attr(755,root,root) %{_sbindir}/corosync-quorumtool
%{_mandir}/man5/corosync.conf.5*
%{_mandir}/man5/votequorum.5*
%{_mandir}/man8/corosync.8*
%{_mandir}/man8/corosync-blackbox.8*
%{_mandir}/man8/corosync-cmapctl.8*
%{_mandir}/man8/corosync-cfgtool.8*
%{_mandir}/man8/corosync-cpgtool.8*
%{_mandir}/man8/corosync-keygen.8*
%{_mandir}/man8/corosync-notifyd.8*
%{_mandir}/man8/corosync-quorumtool.8*
# should be man7...
%{_mandir}/man8/cmap_keys.8*
%{_mandir}/man8/cmap_overview.8*
%{_mandir}/man8/corosync_overview.8*
%{_mandir}/man8/cpg_overview.8*
%{_mandir}/man8/sam_overview.8*
%{_mandir}/man8/votequorum_overview.8*
%{_mandir}/man8/quorum_overview.8*
%dir %{_datadir}/corosync
%attr(755,root,root) %{_datadir}/%{name}/corosync
%attr(755,root,root) %{_datadir}/%{name}/corosync-notifyd
%if %{with xmlconf}
%attr(755,root,root) %{_bindir}/corosync-xmlproc
%config(noreplace) %{_sysconfdir}/corosync/corosync.xml.example
%{_datadir}/corosync/xml2conf.xsl
%{_mandir}/man8/corosync-xmlproc.8*
%{_mandir}/man5/corosync.xml.5*
%endif
%if %{with augeas}
%{_datadir}/augeas/lenses/corosync.aug
%{_datadir}/augeas/lenses/tests/test_corosync.aug
%endif
%if %{with dbus}
/etc/dbus-1/system.d/corosync-signals.conf
%endif
%dir /var/lib/corosync
%attr(700,root,root) %dir /var/log/cluster
%if %{with qdevices}
%attr(755,root,root) %{_sbindir}/corosync-qdevice
%attr(755,root,root) %{_sbindir}/corosync-qdevice-net-certutil
%attr(755,root,root) %{_sbindir}/corosync-qdevice-tool
%{_datadir}/corosync/corosync-qdevice
%{systemdunitdir}/corosync-qdevice.service
%dir %{_sysconfdir}/corosync/qdevice
%attr(770,root,root) %dir %{_sysconfdir}/corosync/qdevice/net
%attr(770,root,root) %dir /var/run/corosync-qdevice
%{_mandir}/man8/corosync-qdevice.8*
%{_mandir}/man8/corosync-qdevice-net-certutil.8*
%{_mandir}/man8/corosync-qdevice-tool.8*
%endif
%if %{with qnetd}
%attr(755,root,root) %{_bindir}/corosync-qnetd
%attr(755,root,root) %{_bindir}/corosync-qnetd-certutil
%attr(755,root,root) %{_bindir}/corosync-qnetd-tool
%{_datadir}/corosync/corosync-qnetd
%{systemdunitdir}/corosync-qnetd.service
%attr(770,root,root) %dir %{_sysconfdir}/corosync/qnetd
%attr(770,root,root) %dir /var/run/corosync-qnetd
%{_mandir}/man8/corosync-qnetd.8*
%{_mandir}/man8/corosync-qnetd-certutil.8*
%{_mandir}/man8/corosync-qnetd-tool.8*
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
%attr(755,root,root) %{_libdir}/libvotequorum.so.8.*.*
%attr(755,root,root) %ghost %{_libdir}/libvotequorum.so.8

%files devel
%defattr(644,root,root,755)
%{?with_apidocs:%doc doc/api/html/*}
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

%if %{with testagents}
%files testagents
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cpg_test_agent
%attr(755,root,root) %{_bindir}/sam_test_agent
%attr(755,root,root) %{_bindir}/votequorum_test_agent
%dir %{_datadir}/corosync/tests
%{_datadir}/corosync/tests/mem_leak_test.sh
%{_datadir}/corosync/tests/net_breaker.sh
%{_datadir}/corosync/tests/cmap-dispatch-deadlock.sh
%{_datadir}/corosync/tests/shm_leak_audit.sh
%endif

%if %{with snmp}
%files -n mibs-corosync
%defattr(644,root,root,755)
%{_datadir}/mibs/COROSYNC-MIB.txt
%endif
